#!/usr/bin/env python3
"""ROR (Research Organization Registry) pilot — fast & reliable academic source.

ROR API:
  https://api.ror.org/v2/organizations?page=1&affiliation=...
  https://api.ror.org/v2/organizations?query=...

License: CC0
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

ROR_BASE = "https://api.ror.org/v2/organizations"
USER_AGENT = "OrganizationGenealogyResearch/0.1 (info@emerging-future.org)"


def uid():
    return uuid.uuid4().hex


def fetch_page(page: int = 1, query: str = None) -> dict:
    params = {"page": page}
    if query:
        params["query"] = query
    qs = urllib.parse.urlencode(params)
    url = f"{ROR_BASE}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_or_create_source(cur):
    row = cur.execute("SELECT source_id FROM source WHERE title = 'ROR (Research Organization Registry)' LIMIT 1").fetchone()
    if row:
        return row[0]
    sid = uid()
    cur.execute(
        """INSERT INTO source (source_id, source_type, title, publisher, locator,
            accessed_at, reliability_score, reliability_basis, license, redistribution)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (sid, "dataset", "ROR (Research Organization Registry)",
         "Research Organization Registry",
         json.dumps({"url": ROR_BASE}, ensure_ascii=False),
         time.strftime("%Y-%m-%d"),
         0.85,
         "学術機関の正規化 ID 体系。Crossref/OpenAlex と統合された信頼性の高いオープンデータ。",
         "CC0", "public_redistributable"),
    )
    return sid


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    source_id = get_or_create_source(cur)
    conn.commit()

    # Get form_id for academic / research org
    # No specific ROR form yet — we'll skip primary_form for now and tag via attributes

    # Fetch first 5 pages (~100 orgs/page = 500 max, take 100 total)
    new_count = 0
    skip_count = 0
    target = 100

    page = 1
    while new_count < target:
        try:
            data = fetch_page(page=page)
        except Exception as e:
            print(f"page {page} failed: {e}", flush=True)
            break

        items = data.get("items", [])
        if not items:
            break

        for it in items:
            if new_count >= target:
                break
            try:
                ror_id = it.get("id", "")  # e.g. https://ror.org/05dxps055
                ror_short = ror_id.rsplit("/", 1)[-1] if ror_id else None

                if not ror_short:
                    continue

                existing = cur.execute(
                    "SELECT organization_id FROM organization WHERE json_extract(external_ids, '$.ror') = ?",
                    (ror_short,)
                ).fetchone()
                if existing:
                    skip_count += 1
                    continue

                # ROR v2 schema: names list with types {"label/lang/value": ..., "types": ["ror_display","label","alias","acronym"]}
                names = it.get("names", [])
                canonical = None
                alt = []
                for n in names:
                    val = n.get("value")
                    lang = n.get("lang")
                    types = n.get("types", [])
                    if "ror_display" in types and not canonical:
                        canonical = val
                    elif val:
                        alt.append({"name": val, "lang": lang or "und", "type": ",".join(types)})
                if not canonical and names:
                    canonical = names[0].get("value")
                if not canonical:
                    continue

                # established year
                est = it.get("established")
                start_date = f"{est}-01-01" if est else None
                start_prec = "year" if est else "unknown"

                # status
                ror_status = it.get("status", "active")
                status = "active" if ror_status == "active" else ("dormant" if ror_status == "inactive" else "unknown")

                # locations -> country
                locations = it.get("locations", [])
                country = None
                if locations:
                    geo = locations[0].get("geonames_details", {})
                    country = geo.get("country_name")

                # types from ROR (e.g. education, healthcare, government, archive, company, facility, nonprofit, other)
                ror_types = it.get("types", [])

                org_id = uid()
                attributes = {
                    "ror_types": ror_types,
                    "imported_via": "ror_pilot_v0.1",
                    "domain": "academic_or_research",
                }
                external_ids = {"ror": ror_short}

                # Wikidata cross-link if present
                ext_links = it.get("external_ids", [])
                for el in ext_links:
                    if el.get("type") == "wikidata":
                        all_vals = el.get("all", [])
                        if all_vals:
                            external_ids["wikidata"] = all_vals[0]
                    elif el.get("type") == "isni":
                        all_vals = el.get("all", [])
                        if all_vals:
                            external_ids["isni"] = all_vals[0]

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
                     start_date, start_prec, None, None, status,
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
                     json.dumps({"value": canonical, "ror_id": ror_short}, ensure_ascii=False),
                     source_id, 0.85, "ror_pilot_etl",
                     f"ROR ID {ror_short}, types={ror_types}"),
                )
                new_count += 1
            except Exception as e:
                print(f"skip item: {e}", flush=True)
                continue

        conn.commit()
        print(f"page {page}: total_new={new_count} skip={skip_count}", flush=True)
        page += 1
        time.sleep(1)
        if page > 10:
            break

    cur.execute("SELECT COUNT(*) FROM organization")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM claim")
    claims = cur.fetchone()[0]
    print()
    print("=== ROR summary ===", flush=True)
    print(f"new orgs: {new_count}", flush=True)
    print(f"skipped (existing): {skip_count}", flush=True)
    print(f"organization total: {total}", flush=True)
    print(f"claim total: {claims}", flush=True)
    conn.close()


if __name__ == "__main__":
    main()
