#!/usr/bin/env python3
"""License compliance audit for the organization genealogy database."""
from __future__ import annotations

import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
REPORT = ROOT / "data" / "license_compliance_report.md"
PUBLIC_SQL = ROOT / "data" / "public_subset.sql"

REDISTRIBUTION_RANK = {
    "public_redistributable": 1,
    "attribution_required": 2,
    "noncommercial": 3,
    "private": 4,
    "restricted": 5,
}

DEPENDENCY_CTE = """
WITH org_source_dependencies AS (
  SELECT c.entity_id AS organization_id, c.source_id, 'organization' AS dependency_path
  FROM claim c
  JOIN organization o ON o.organization_id = c.entity_id
  WHERE c.entity_type = 'organization' AND c.source_id IS NOT NULL

  UNION
  SELECT ofa.organization_id, c.source_id, 'organization_form_assignment' AS dependency_path
  FROM organization_form_assignment ofa
  JOIN claim c ON c.claim_id = ofa.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT ofa.organization_id, c.source_id, 'organization_form_assignment' AS dependency_path
  FROM organization_form_assignment ofa
  JOIN claim c
    ON c.entity_type = 'organization_form_assignment'
   AND c.entity_id = ofa.assignment_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT r.source_organization_id AS organization_id, c.source_id, 'relation_source' AS dependency_path
  FROM relation r
  JOIN claim c ON c.claim_id = r.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT r.target_organization_id AS organization_id, c.source_id, 'relation_target' AS dependency_path
  FROM relation r
  JOIN claim c ON c.claim_id = r.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT r.source_organization_id AS organization_id, c.source_id, 'relation_source' AS dependency_path
  FROM relation r
  JOIN claim c ON c.entity_type = 'relation' AND c.entity_id = r.relation_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT r.target_organization_id AS organization_id, c.source_id, 'relation_target' AS dependency_path
  FROM relation r
  JOIN claim c ON c.entity_type = 'relation' AND c.entity_id = r.relation_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT otf.organization_id, c.source_id, 'organization_temporal_facet' AS dependency_path
  FROM organization_temporal_facet otf
  JOIN claim c ON c.claim_id = otf.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT otf.organization_id, c.source_id, 'organization_temporal_facet' AS dependency_path
  FROM organization_temporal_facet otf
  JOIN claim c
    ON c.entity_type = 'organization_temporal_facet'
   AND c.entity_id = otf.organization_facet_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT eo.organization_id, c.source_id, 'event' AS dependency_path
  FROM event e
  JOIN event_organization eo ON eo.event_id = e.event_id
  JOIN claim c ON c.claim_id = e.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT eo.organization_id, c.source_id, 'event' AS dependency_path
  FROM event e
  JOIN event_organization eo ON eo.event_id = e.event_id
  JOIN claim c ON c.entity_type = 'event' AND c.entity_id = e.event_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT a.organization_id, c.source_id, 'activity' AS dependency_path
  FROM activity a
  JOIN claim c ON c.claim_id = a.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT a.organization_id, c.source_id, 'activity' AS dependency_path
  FROM activity a
  JOIN claim c ON c.entity_type = 'activity' AND c.entity_id = a.activity_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT ir.organization_id, c.source_id, 'impact_record' AS dependency_path
  FROM impact_record ir
  JOIN claim c ON c.claim_id = ir.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT ir.organization_id, c.source_id, 'impact_record' AS dependency_path
  FROM impact_record ir
  JOIN claim c ON c.entity_type = 'impact_record' AND c.entity_id = ir.impact_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT fr.organization_id, c.source_id, 'function_record' AS dependency_path
  FROM function_record fr
  JOIN claim c ON c.claim_id = fr.claim_id
  WHERE c.source_id IS NOT NULL

  UNION
  SELECT fr.organization_id, c.source_id, 'function_record' AS dependency_path
  FROM function_record fr
  JOIN claim c ON c.entity_type = 'function_record' AND c.entity_id = fr.function_id
  WHERE c.source_id IS NOT NULL
),
ranked_dependencies AS (
  SELECT
    d.organization_id,
    d.source_id,
    d.dependency_path,
    s.title,
    s.source_type,
    s.license,
    s.redistribution,
    CASE s.redistribution
      WHEN 'public_redistributable' THEN 1
      WHEN 'attribution_required' THEN 2
      WHEN 'noncommercial' THEN 3
      WHEN 'private' THEN 4
      WHEN 'restricted' THEN 5
      ELSE 6
    END AS restriction_rank
  FROM org_source_dependencies d
  JOIN source s ON s.source_id = d.source_id
),
organization_license AS (
  SELECT
    o.organization_id,
    o.canonical_name,
    COUNT(DISTINCT rd.source_id) AS source_count,
    COALESCE(MAX(rd.restriction_rank), 6) AS max_restriction_rank,
    CASE COALESCE(MAX(rd.restriction_rank), 6)
      WHEN 1 THEN 'public_redistributable'
      WHEN 2 THEN 'attribution_required'
      WHEN 3 THEN 'noncommercial'
      WHEN 4 THEN 'private'
      WHEN 5 THEN 'restricted'
      ELSE 'unclassified'
    END AS max_redistribution
  FROM organization o
  LEFT JOIN ranked_dependencies rd ON rd.organization_id = o.organization_id
  GROUP BY o.organization_id, o.canonical_name
),
organization_most_restrictive_source AS (
  SELECT organization_id, source_id, title, redistribution, restriction_rank
  FROM (
    SELECT
      rd.*,
      ROW_NUMBER() OVER (
        PARTITION BY rd.organization_id
        ORDER BY rd.restriction_rank DESC, rd.title, rd.source_id
      ) AS row_num
    FROM ranked_dependencies rd
  )
  WHERE row_num = 1
),
public_organizations AS (
  SELECT organization_id
  FROM organization_license
  WHERE source_count > 0 AND max_restriction_rank = 1
)
"""

PUBLIC_SUBSET_SQL = f"""-- Public subset query set generated by etl/26_license_audit.py.
-- It keeps only organizations whose full traced source dependency set is
-- public_redistributable. Run each SELECT into a table when constructing
-- a subset SQLite database.

{DEPENDENCY_CTE}
SELECT o.*
FROM organization o
JOIN public_organizations po ON po.organization_id = o.organization_id;

{DEPENDENCY_CTE}
SELECT DISTINCT s.*
FROM source s
JOIN ranked_dependencies rd ON rd.source_id = s.source_id
JOIN public_organizations po ON po.organization_id = rd.organization_id
WHERE s.redistribution = 'public_redistributable';

{DEPENDENCY_CTE}
SELECT DISTINCT c.*
FROM claim c
JOIN source s ON s.source_id = c.source_id
WHERE s.redistribution = 'public_redistributable'
  AND (
    (c.entity_type = 'organization'
      AND c.entity_id IN (SELECT organization_id FROM public_organizations))
    OR EXISTS (
      SELECT 1 FROM organization_form_assignment x
      WHERE (x.claim_id = c.claim_id
          OR (x.assignment_id = c.entity_id
          AND c.entity_type = 'organization_form_assignment'))
        AND x.organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM relation x
      WHERE (x.claim_id = c.claim_id
          OR (x.relation_id = c.entity_id
          AND c.entity_type = 'relation'))
        AND x.source_organization_id IN (SELECT organization_id FROM public_organizations)
        AND x.target_organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM organization_temporal_facet x
      WHERE (x.claim_id = c.claim_id
          OR (x.organization_facet_id = c.entity_id
          AND c.entity_type = 'organization_temporal_facet'))
        AND x.organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM event x
      JOIN event_organization eo ON eo.event_id = x.event_id
      WHERE (x.claim_id = c.claim_id
          OR (x.event_id = c.entity_id
          AND c.entity_type = 'event'))
        AND eo.organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM activity x
      WHERE (x.claim_id = c.claim_id
          OR (x.activity_id = c.entity_id
          AND c.entity_type = 'activity'))
        AND x.organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM impact_record x
      WHERE (x.claim_id = c.claim_id
          OR (x.impact_id = c.entity_id
          AND c.entity_type = 'impact_record'))
        AND x.organization_id IN (SELECT organization_id FROM public_organizations)
    )
    OR EXISTS (
      SELECT 1 FROM function_record x
      WHERE (x.claim_id = c.claim_id
          OR (x.function_id = c.entity_id
          AND c.entity_type = 'function_record'))
        AND x.organization_id IN (SELECT organization_id FROM public_organizations)
    )
  );

{DEPENDENCY_CTE}
SELECT ofa.*
FROM organization_form_assignment ofa
JOIN public_organizations po ON po.organization_id = ofa.organization_id;

{DEPENDENCY_CTE}
SELECT r.*
FROM relation r
JOIN public_organizations spo ON spo.organization_id = r.source_organization_id
JOIN public_organizations tpo ON tpo.organization_id = r.target_organization_id;

{DEPENDENCY_CTE}
SELECT e.*
FROM event e
WHERE EXISTS (
  SELECT 1
  FROM event_organization eo
  JOIN public_organizations po ON po.organization_id = eo.organization_id
  WHERE eo.event_id = e.event_id
);

{DEPENDENCY_CTE}
SELECT eo.*
FROM event_organization eo
JOIN public_organizations po ON po.organization_id = eo.organization_id;

{DEPENDENCY_CTE}
SELECT a.*
FROM activity a
JOIN public_organizations po ON po.organization_id = a.organization_id;

{DEPENDENCY_CTE}
SELECT fr.*
FROM function_record fr
JOIN public_organizations po ON po.organization_id = fr.organization_id;

{DEPENDENCY_CTE}
SELECT ir.*
FROM impact_record ir
JOIN public_organizations po ON po.organization_id = ir.organization_id;

{DEPENDENCY_CTE}
SELECT otf.*
FROM organization_temporal_facet otf
JOIN public_organizations po ON po.organization_id = otf.organization_id;
"""


def rows(cur: sqlite3.Cursor, sql: str) -> list[sqlite3.Row]:
    return cur.execute(sql).fetchall()


def md_table(headers: list[str], data: list[tuple]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in data:
        lines.append("| " + " | ".join(str(value) if value is not None else "" for value in row) + " |")
    return "\n".join(lines)


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    source_counts = rows(
        cur,
        """
        SELECT redistribution, COUNT(*) AS source_count
        FROM source
        GROUP BY redistribution
        ORDER BY
          CASE redistribution
            WHEN 'restricted' THEN 5
            WHEN 'private' THEN 4
            WHEN 'noncommercial' THEN 3
            WHEN 'attribution_required' THEN 2
            WHEN 'public_redistributable' THEN 1
            ELSE 6
          END DESC,
          redistribution
        """,
    )
    org_counts = rows(
        cur,
        DEPENDENCY_CTE
        + """
        SELECT max_redistribution, COUNT(*) AS organization_count
        FROM organization_license
        GROUP BY max_redistribution
        ORDER BY max_restriction_rank DESC, max_redistribution
        """,
    )
    total_orgs = cur.execute("SELECT COUNT(*) FROM organization").fetchone()[0]
    public_orgs = cur.execute(
        DEPENDENCY_CTE + "SELECT COUNT(*) FROM public_organizations"
    ).fetchone()[0]
    commercial_orgs = rows(
        cur,
        DEPENDENCY_CTE
        + """
        SELECT ol.organization_id, ol.canonical_name, mrs.redistribution, mrs.title
        FROM organization_license ol
        JOIN organization_most_restrictive_source mrs
          ON mrs.organization_id = ol.organization_id
        WHERE ol.max_redistribution IN ('private', 'restricted')
        ORDER BY ol.canonical_name
        """,
    )
    attribution_sources = rows(
        cur,
        """
        SELECT source_id, title, COALESCE(license, '') AS license
        FROM source
        WHERE redistribution = 'attribution_required'
        ORDER BY title
        """,
    )
    most_restrictive = cur.execute(
        DEPENDENCY_CTE
        + """
        SELECT mrs.redistribution, mrs.title, ol.canonical_name
        FROM organization_license ol
        JOIN organization_most_restrictive_source mrs
          ON mrs.organization_id = ol.organization_id
        ORDER BY ol.max_restriction_rank DESC, mrs.title, ol.canonical_name
        LIMIT 1
        """,
    ).fetchone()

    public_examples = rows(
        cur,
        DEPENDENCY_CTE
        + """
        SELECT o.organization_id, o.canonical_name
        FROM organization o
        JOIN public_organizations po ON po.organization_id = o.organization_id
        ORDER BY o.canonical_name
        LIMIT 25
        """,
    )
    dependency_paths = rows(
        cur,
        DEPENDENCY_CTE
        + """
        SELECT dependency_path, COUNT(DISTINCT organization_id) AS organization_count,
               COUNT(DISTINCT source_id) AS source_count
        FROM ranked_dependencies
        GROUP BY dependency_path
        ORDER BY organization_count DESC, dependency_path
        """,
    )

    commercial_flag = "BLOCKED" if commercial_orgs else "CLEAR"
    gate_status = "not ready" if commercial_orgs else "ready for license gate review"

    report = f"""# License Compliance Report

Generated from `data/og.db` by `etl/26_license_audit.py`.

## Source Redistribution Counts

{md_table(["redistribution", "source_count"], [(r["redistribution"], r["source_count"]) for r in source_counts])}

## Organization License Boundary

{md_table(["max_redistribution", "organization_count"], [(r["max_redistribution"], r["organization_count"]) for r in org_counts])}

- Public redistributable organization count: {public_orgs} / {total_orgs}
- Commercial/private dependency flag: {commercial_flag}
- Phase 7 / Roadmap Gate 5 license status: {gate_status}

## Publicly Publishable Scope

The public subset is limited to organizations whose traced dependency set is non-empty and has `public_redistributable` as its most restrictive redistribution tier. Current public organization examples:

{md_table(["organization_id", "canonical_name"], [(r["organization_id"], r["canonical_name"]) for r in public_examples])}

The full extraction query set is in `data/public_subset.sql`.

## Attribution Required Sources

These sources are not included in the strict public subset because their redistribution tier is `attribution_required`, but they require citation if used in derived narrative, figures, or non-strict release packages.

{md_table(["source_id", "title", "license"], [(r["source_id"], r["title"], r["license"]) for r in attribution_sources])}

## Commercial DB / Restricted Dependencies

Organizations below depend on at least one `private` or `restricted` source and must be excluded from public data redistribution or reduced to aggregate/non-reconstructive outputs.

{md_table(["organization_id", "canonical_name", "most_restrictive_redistribution", "most_restrictive_source"], [(r["organization_id"], r["canonical_name"], r["redistribution"], r["title"]) for r in commercial_orgs])}

## Dependency Paths Audited

{md_table(["dependency_path", "organization_count", "source_count"], [(r["dependency_path"], r["organization_count"], r["source_count"]) for r in dependency_paths])}

## Phase 7 / Roadmap Gate 5 Readiness

- License boundary: not ready for full public release while `private` / `restricted` dependencies remain in organization-level data.
- Public subset: ready to build with `data/public_subset.sql`, limited to {public_orgs} organizations.
- Attribution: `attribution_required` sources are enumerated above and need release-package attribution if used outside the strict public subset.
- Commercial DB condition: exclude private/restricted-derived rows from redistributed data; keep them as internal analysis, aggregate output, or reproducible instructions for licensed users only.
"""

    if most_restrictive:
        report += (
            "\n## Short Audit Result\n\n"
            f"公開可能 {public_orgs}/{total_orgs}。"
            f"最制限依存: {most_restrictive['redistribution']} "
            f"{most_restrictive['title']} "
            f"({most_restrictive['canonical_name']})。\n"
        )

    REPORT.write_text(report, encoding="utf-8")
    PUBLIC_SQL.write_text(PUBLIC_SUBSET_SQL, encoding="utf-8")

    print(f"source redistribution tiers: {dict(Counter({r['redistribution']: r['source_count'] for r in source_counts}))}")
    print(f"public organizations: {public_orgs}/{total_orgs}")
    if most_restrictive:
        print(
            "most restrictive dependency: "
            f"{most_restrictive['redistribution']} | "
            f"{most_restrictive['title']} | "
            f"{most_restrictive['canonical_name']}"
        )
    print(f"wrote {REPORT}")
    print(f"wrote {PUBLIC_SQL}")

    conn.close()


if __name__ == "__main__":
    main()
