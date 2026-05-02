#!/usr/bin/env python3
"""Wikidata SPARQL pilot ETL.

Pull representative organizations across eras (ancient / medieval / modern / contemporary / digital)
and insert via claim-based pattern.

Endpoint: https://query.wikidata.org/sparql
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


# Query template: organizations with creation_date in a given era,
# with English & Japanese labels if available.
def build_query(min_year: int, max_year: int, limit: int = 30) -> str:
    return f"""
SELECT DISTINCT ?org ?orgLabel ?orgLabelJa ?orgLabelEn ?creation ?dissolution ?country ?countryLabel ?instanceLabel WHERE {{
  ?org wdt:P31/wdt:P279* wd:Q43229 ;
       wdt:P571 ?creation ;
       wdt:P31 ?instance .
  FILTER(YEAR(?creation) >= {min_year} && YEAR(?creation) < {max_year})
  OPTIONAL {{ ?org wdt:P576 ?dissolution }}
  OPTIONAL {{ ?org wdt:P17 ?country . ?country rdfs:label ?countryLabel . FILTER(LANG(?countryLabel) = "ja") }}
  OPTIONAL {{ ?org rdfs:label ?orgLabelJa . FILTER(LANG(?orgLabelJa) = "ja") }}
  OPTIONAL {{ ?org rdfs:label ?orgLabelEn . FILTER(LANG(?orgLabelEn) = "en") }}
  OPTIONAL {{ ?instance rdfs:label ?instanceLabel . FILTER(LANG(?instanceLabel) = "en") }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ja,en" . }}
}}
LIMIT {limit}
"""


def sparql_get(query: str, retry: int = 2) -> list:
    qs = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{WD_ENDPOINT}?{qs}"
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/sparql-results+json",
    })
    last_err = None
    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["results"]["bindings"]
        except Exception as e:
            last_err = e
            print(f"  [warn] attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(3)
    raise RuntimeError(f"sparql failed: {last_err}")


def get_or_create_wikidata_source(cur):
    """Wikidata 自体を Source として登録 (1 回だけ)。"""
    row = cur.execute(
        "SELECT source_id FROM source WHERE title = ? LIMIT 1",
        ("Wikidata SPARQL endpoint",),
    ).fetchone()
    if row:
        return row[0]
    sid = uid()
    cur.execute(
        """INSERT INTO source
           (source_id, source_type, title, publisher, locator,
            accessed_at, reliability_score, reliability_basis, license, redistribution)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            sid,
            "dataset",
            "Wikidata SPARQL endpoint",
            "Wikimedia Foundation",
            json.dumps({"url": WD_ENDPOINT}, ensure_ascii=False),
            time.strftime("%Y-%m-%d"),
            0.6,
            "コミュニティ編集の構造化データ。出典付き statement の確度は claim 単位で再評価が必要。",
            "CC0",
            "public_redistributable",
        ),
    )
    return sid


ERAS = [
    # 古代・中世は SPARQL タイムアウトが多い (P571 + 範囲 FILTER のスキャンが重い) ので
    # まずは近世以降に限定。古代/中世は別途 type-specific クエリで取り込む方針。
    ("early_modern",   1500,   1800, 20),
    ("modern",         1800,   1945, 20),
    ("contemporary",   1945,   2010, 20),
    ("digital",        2010,   2026, 20),
]


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    source_id = get_or_create_wikidata_source(cur)
    conn.commit()

    total_orgs = 0
    by_era = {}

    for era_name, min_y, max_y, limit in ERAS:
        print(f"\n--- {era_name} ({min_y} to {max_y}) ---")
        try:
            rows = sparql_get(build_query(min_y, max_y, limit))
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            by_era[era_name] = 0
            continue

        era_count = 0
        for r in rows:
            try:
                qid_uri = r["org"]["value"]
                qid = qid_uri.rsplit("/", 1)[-1]

                # check if already exists by external_id
                existing = cur.execute(
                    "SELECT organization_id FROM organization "
                    "WHERE json_extract(external_ids, '$.wikidata') = ?",
                    (qid,),
                ).fetchone()
                if existing:
                    continue

                label_ja = r.get("orgLabelJa", {}).get("value")
                label_en = r.get("orgLabelEn", {}).get("value")
                fallback = r.get("orgLabel", {}).get("value", qid)
                canonical = label_ja or label_en or fallback

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

                country = r.get("countryLabel", {}).get("value")
                instance_label = r.get("instanceLabel", {}).get("value")

                org_id = uid()
                attributes = {
                    "wikidata_instance": instance_label,
                    "imported_via": "sparql_pilot_v0.1",
                    "era_bucket": era_name,
                }
                external_ids = {"wikidata": qid}
                geo_scope = {"country": country} if country else None

                cur.execute(
                    """INSERT INTO organization
                       (organization_id, canonical_name, alternate_names, description,
                        primary_form_id, geo_scope, start_date, start_date_precision,
                        end_date, end_date_precision, status, attributes, external_ids)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        org_id, canonical,
                        json.dumps(alt, ensure_ascii=False) if alt else None,
                        instance_label,
                        None,  # primary_form_id, set later
                        json.dumps(geo_scope, ensure_ascii=False) if geo_scope else None,
                        start_date, start_prec,
                        end_date, end_prec,
                        status,
                        json.dumps(attributes, ensure_ascii=False),
                        json.dumps(external_ids, ensure_ascii=False),
                    ),
                )

                # record claim for the canonical_name
                claim_id = uid()
                cur.execute(
                    """INSERT INTO claim
                       (claim_id, entity_type, entity_id, field_path, value_kind,
                        claim_value, source_id, confidence, recorded_by, interpretation_note)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        claim_id, "organization", org_id, "canonical_name",
                        "present",
                        json.dumps({"value": canonical}, ensure_ascii=False),
                        source_id, 0.6,
                        "wikidata_pilot_etl",
                        f"Wikidata QID {qid}, era={era_name}",
                    ),
                )
                era_count += 1
                total_orgs += 1
            except Exception as e:
                print(f"  skip row due to error: {e}", file=sys.stderr)
                continue

        by_era[era_name] = era_count
        print(f"  inserted {era_count}")
        time.sleep(2)  # be nice to Wikidata

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM organization")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM claim")
    claims = cur.fetchone()[0]
    print()
    print(f"=== summary ===")
    print(f"new orgs this run: {total_orgs}")
    print(f"by era: {by_era}")
    print(f"organization total: {total}")
    print(f"claim total: {claims}")
    conn.close()


if __name__ == "__main__":
    main()
