#!/usr/bin/env python3
"""Wikidata type-specific ETL — 03 のリトライ。

戦略:
- 範囲 FILTER (YEAR(?creation) ...) を使わず、特定の P31 type に絞る
- 各 type 50 件ずつ、計 ~250 件を目標
- TIMEOUT を厳格に管理 (60 秒で諦めて次へ)

対象 type:
  Q210980 monastic_order  — 修道会
  Q15243209 historical_organization — 歴史的組織
  Q1530705 Hanseatic League family — ハンザ系
  Q4287745 DAO            — 分散自律組織
  Q43702 kingdom           — 王国
  Q11425700 clan          — 氏族
"""
import json
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

WD_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "OrganizationGenealogyResearch/0.1 (info@emerging-future.org)"


def uid():
    return uuid.uuid4().hex


# (qid, label, era_bucket, limit)
TARGETS = [
    ("Q210980",   "monastic_order",          "medieval",     50),
    ("Q15243209", "historical_organization", "various",      50),
    ("Q1530705",  "hanseatic_league",        "medieval",     30),
    ("Q4287745",  "dao",                     "digital",      50),
    ("Q11425700", "clan",                    "ancient",      30),
    ("Q188509",   "corporation",             "modern",       50),
]


def build_query(type_qid: str, limit: int = 50) -> str:
    """Type-specific query — no broad date FILTER, just instance_of subclass."""
    return f"""
SELECT DISTINCT ?org ?orgLabelJa ?orgLabelEn ?creation ?dissolution ?countryLabelJa ?countryLabelEn WHERE {{
  ?org wdt:P31/wdt:P279* wd:{type_qid} .
  OPTIONAL {{ ?org wdt:P571 ?creation }}
  OPTIONAL {{ ?org wdt:P576 ?dissolution }}
  OPTIONAL {{ ?org rdfs:label ?orgLabelJa . FILTER(LANG(?orgLabelJa) = "ja") }}
  OPTIONAL {{ ?org rdfs:label ?orgLabelEn . FILTER(LANG(?orgLabelEn) = "en") }}
  OPTIONAL {{
    ?org wdt:P17 ?country .
    OPTIONAL {{ ?country rdfs:label ?countryLabelJa . FILTER(LANG(?countryLabelJa) = "ja") }}
    OPTIONAL {{ ?country rdfs:label ?countryLabelEn . FILTER(LANG(?countryLabelEn) = "en") }}
  }}
}}
LIMIT {limit}
"""


def sparql_get(query: str, timeout: int = 60) -> list:
    qs = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{WD_ENDPOINT}?{qs}"
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["results"]["bindings"]


def get_or_create_source(cur, title, **kwargs):
    row = cur.execute("SELECT source_id FROM source WHERE title = ? LIMIT 1", (title,)).fetchone()
    if row:
        return row[0]
    sid = uid()
    cur.execute(
        """INSERT INTO source
           (source_id, source_type, title, publisher, locator, accessed_at,
            reliability_score, reliability_basis, license, redistribution)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (sid, kwargs.get("source_type", "dataset"), title,
         kwargs.get("publisher"),
         json.dumps(kwargs.get("locator", {}), ensure_ascii=False),
         kwargs.get("accessed_at", time.strftime("%Y-%m-%d")),
         kwargs.get("reliability_score", 0.6),
         kwargs.get("reliability_basis", ""),
         kwargs.get("license", "CC0"),
         kwargs.get("redistribution", "public_redistributable")),
    )
    return sid


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    source_id = get_or_create_source(cur, "Wikidata SPARQL endpoint",
        source_type="dataset", publisher="Wikimedia Foundation",
        locator={"url": WD_ENDPOINT},
        reliability_score=0.6,
        reliability_basis="コミュニティ編集の構造化データ。出典付き statement の確度は claim 単位で再評価が必要。",
        license="CC0", redistribution="public_redistributable")

    total_new = 0
    by_type = {}

    for qid, label, era, limit in TARGETS:
        print(f"\n--- {qid} {label} (era={era}, limit={limit}) ---", flush=True)
        try:
            rows = sparql_get(build_query(qid, limit), timeout=45)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr, flush=True)
            by_type[label] = {"err": str(e)}
            continue

        type_new = 0
        type_skip = 0
        for r in rows:
            try:
                org_uri = r["org"]["value"]
                wd_qid = org_uri.rsplit("/", 1)[-1]

                existing = cur.execute(
                    "SELECT organization_id FROM organization "
                    "WHERE json_extract(external_ids, '$.wikidata') = ?",
                    (wd_qid,),
                ).fetchone()
                if existing:
                    type_skip += 1
                    continue

                label_ja = r.get("orgLabelJa", {}).get("value")
                label_en = r.get("orgLabelEn", {}).get("value")
                canonical = label_ja or label_en or wd_qid

                alt = []
                if label_ja and label_ja != canonical:
                    alt.append({"name": label_ja, "lang": "ja"})
                if label_en and label_en != canonical:
                    alt.append({"name": label_en, "lang": "en"})

                creation = r.get("creation", {}).get("value", "")
                start_date = creation[:10] if creation else None
                start_prec = "exact" if start_date else "unknown"

                dissolution = r.get("dissolution", {}).get("value", "")
                end_date = dissolution[:10] if dissolution else None
                end_prec = "exact" if end_date else None
                status = "extinct" if end_date else "unknown"

                country = r.get("countryLabelJa", {}).get("value") or r.get("countryLabelEn", {}).get("value")

                org_id = uid()
                attributes = {
                    "wikidata_type": label,
                    "imported_via": "sparql_typed_v0.1",
                    "era_bucket": era,
                }
                external_ids = {"wikidata": wd_qid}
                geo_scope = {"country": country} if country else None

                cur.execute(
                    """INSERT INTO organization
                       (organization_id, canonical_name, alternate_names, description,
                        primary_form_id, geo_scope, start_date, start_date_precision,
                        end_date, end_date_precision, status, attributes, external_ids)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (org_id, canonical,
                     json.dumps(alt, ensure_ascii=False) if alt else None,
                     None,
                     None,
                     json.dumps(geo_scope, ensure_ascii=False) if geo_scope else None,
                     start_date, start_prec, end_date, end_prec, status,
                     json.dumps(attributes, ensure_ascii=False),
                     json.dumps(external_ids, ensure_ascii=False)),
                )

                claim_id = uid()
                cur.execute(
                    """INSERT INTO claim
                       (claim_id, entity_type, entity_id, field_path, value_kind,
                        claim_value, source_id, confidence, recorded_by, interpretation_note)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (claim_id, "organization", org_id, "canonical_name", "present",
                     json.dumps({"value": canonical}, ensure_ascii=False),
                     source_id, 0.6, "wikidata_typed_etl",
                     f"Wikidata QID {wd_qid}, type={label}"),
                )
                type_new += 1
                total_new += 1
            except Exception as e:
                print(f"  skip row: {e}", file=sys.stderr, flush=True)
                continue

        by_type[label] = {"new": type_new, "skipped_existing": type_skip, "fetched": len(rows)}
        print(f"  fetched={len(rows)} new={type_new} skipped_existing={type_skip}", flush=True)
        conn.commit()
        time.sleep(2)

    cur.execute("SELECT COUNT(*) FROM organization")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM claim")
    claims = cur.fetchone()[0]
    print()
    print("=== summary ===", flush=True)
    print(f"new orgs this run: {total_new}", flush=True)
    print(f"by type:", flush=True)
    for k, v in by_type.items():
        print(f"  {k:30s}  {v}", flush=True)
    print(f"organization total: {total}", flush=True)
    print(f"claim total: {claims}", flush=True)
    conn.close()


if __name__ == "__main__":
    main()
