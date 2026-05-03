#!/usr/bin/env python3
"""生命メタファーの 5 つの罠を DB 上で監査する。

DB は読み取り専用で開き、検出結果だけを data/metaphor_traps_report.md に出力する。
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT_REPORT = ROOT / "data" / "metaphor_traps_report.md"

BIO_VERBS_EN = [
    "breathe",
    "breathes",
    "breathed",
    "breathing",
    "metabolize",
    "metabolizes",
    "metabolized",
    "metabolizing",
    "metabolise",
    "metabolises",
    "metabolised",
    "metabolising",
    "reproduce",
    "reproduces",
    "reproduced",
    "reproducing",
    "evolve",
    "evolves",
    "evolved",
    "evolving",
]
BIO_VERBS_JA = ["呼吸", "代謝", "繁殖", "再生産", "進化", "淘汰"]
ORG_SUBJECTS_EN = [
    "organization",
    "organisation",
    "institution",
    "company",
    "corporation",
    "state",
    "order",
    "guild",
    "network",
    "movement",
]
ORG_SUBJECTS_JA = ["組織", "企業", "会社", "国家", "団体", "修道会", "ギルド", "運動", "ネットワーク"]

SURVIVAL_CIRCULAR_RE = re.compile(
    r"\b(survival of the fittest|fittest survive|only the fit survive|natural selection)\b"
    r"|適者生存|優勝劣敗|生き残れなかっただけ|淘汰されただけ",
    re.IGNORECASE,
)

BOUNDARY_RE = re.compile(r"boundary|jurisdiction|legal\s+scope|territorial|境界|管轄|法域|領域", re.IGNORECASE)
JURISDICTION_RE = re.compile(
    r"(?:legal\s+jurisdiction|jurisdiction|under|governed\s+by)\s+([A-Z][A-Za-z ._-]{1,60})"
    r"|([一-龥ァ-ンーA-Za-z]{2,30})(?:法|管轄|法域)",
    re.IGNORECASE,
)
OPEN_BOUNDARY_RE = re.compile(r"open|permeable|porous|fluid|参加自由|開放|透過", re.IGNORECASE)
CLOSED_BOUNDARY_RE = re.compile(r"closed|exclusive|sealed|bounded|固定|閉鎖|排他的", re.IGNORECASE)

PHYSICAL_MILLER_TYPES = {
    "miller_03_ingestor",
    "miller_04_distributor",
    "miller_05_converter",
    "miller_06_producer",
    "miller_07_matter_energy_storage",
    "miller_08_extruder",
    "miller_09_motor",
    "miller_10_supporter",
}


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def compile_bio_patterns(name: str | None = None) -> list[re.Pattern[str]]:
    en_subject = r"\b(?:" + "|".join(re.escape(s) for s in ORG_SUBJECTS_EN) + r")s?\b"
    en_verb = r"\b(?:" + "|".join(re.escape(v) for v in BIO_VERBS_EN) + r")\b"
    ja_subject = r"(?:" + "|".join(re.escape(s) for s in ORG_SUBJECTS_JA) + r")"
    ja_verb = r"(?:" + "|".join(re.escape(v) for v in BIO_VERBS_JA) + r")"
    patterns = [
        re.compile(en_subject + r"(?:\W+\w+){0,8}?\W+" + en_verb, re.IGNORECASE),
        re.compile(ja_subject + r".{0,30}?" + ja_verb),
    ]
    if name and len(name.strip()) >= 3:
        escaped = re.escape(name.strip())
        patterns.extend(
            [
                re.compile(r"\b" + escaped + r"\b(?:\W+\w+){0,8}?\W+" + en_verb, re.IGNORECASE),
                re.compile(escaped + r".{0,30}?" + ja_verb),
            ]
        )
    return patterns


def text_hit(text: str | None, patterns: list[re.Pattern[str]]) -> str | None:
    if not text:
        return None
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


def snippet(text: str | None, max_len: int = 180) -> str:
    if not text:
        return ""
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= max_len else compact[: max_len - 1] + "..."


def detect_reification(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    rows = conn.execute(
        """
        SELECT organization_id, canonical_name, description
        FROM organization
        WHERE description IS NOT NULL AND trim(description) <> ''
        """
    ).fetchall()
    for row in rows:
        hit = text_hit(row["description"], compile_bio_patterns(row["canonical_name"]))
        if hit:
            hits.append(
                {
                    "table": "organization",
                    "record_id": row["organization_id"],
                    "organization": row["canonical_name"],
                    "field": "description",
                    "match": hit,
                    "text": snippet(row["description"]),
                }
            )

    rows = conn.execute(
        """
        SELECT a.activity_id, a.description, o.canonical_name
        FROM activity a
        JOIN organization o ON o.organization_id = a.organization_id
        WHERE a.description IS NOT NULL AND trim(a.description) <> ''
        """
    ).fetchall()
    for row in rows:
        hit = text_hit(row["description"], compile_bio_patterns(row["canonical_name"]))
        if hit:
            hits.append(
                {
                    "table": "activity",
                    "record_id": row["activity_id"],
                    "organization": row["canonical_name"],
                    "field": "description",
                    "match": hit,
                    "text": snippet(row["description"]),
                }
            )

    rows = conn.execute(
        """
        SELECT c.claim_id, c.interpretation_note, o.canonical_name
        FROM claim c
        LEFT JOIN organization o
          ON c.entity_type = 'organization' AND o.organization_id = c.entity_id
        WHERE c.interpretation_note IS NOT NULL AND trim(c.interpretation_note) <> ''
        """
    ).fetchall()
    for row in rows:
        hit = text_hit(row["interpretation_note"], compile_bio_patterns(row["canonical_name"]))
        if hit:
            hits.append(
                {
                    "table": "claim",
                    "record_id": row["claim_id"],
                    "organization": row["canonical_name"] or "",
                    "field": "interpretation_note",
                    "match": hit,
                    "text": snippet(row["interpretation_note"]),
                }
            )
    return hits


def detect_circular_survival(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    hits = []
    rows = conn.execute(
        """
        SELECT e.event_id, e.description, e.causes, e.outcomes,
               group_concat(o.canonical_name, '; ') AS organizations
        FROM event e
        LEFT JOIN event_organization eo ON eo.event_id = e.event_id
        LEFT JOIN organization o ON o.organization_id = eo.organization_id
        WHERE e.dissolution_cause = 'obsolescence'
        GROUP BY e.event_id
        """
    ).fetchall()
    for row in rows:
        text = " ".join([row["description"] or "", row["causes"] or "", row["outcomes"] or ""])
        match = SURVIVAL_CIRCULAR_RE.search(text)
        if match:
            hits.append(
                {
                    "event_id": row["event_id"],
                    "organizations": row["organizations"] or "",
                    "match": match.group(0),
                    "text": snippet(text),
                }
            )
    return hits


def claim_org_id(conn: sqlite3.Connection, claim: sqlite3.Row) -> str | None:
    entity_type = claim["entity_type"]
    entity_id = claim["entity_id"]
    if entity_type == "organization":
        return entity_id
    if entity_type == "activity":
        row = conn.execute("SELECT organization_id FROM activity WHERE activity_id = ?", (entity_id,)).fetchone()
        return row["organization_id"] if row else None
    if entity_type == "function_record":
        row = conn.execute("SELECT organization_id FROM function_record WHERE function_id = ?", (entity_id,)).fetchone()
        return row["organization_id"] if row else None
    if entity_type == "organization_form_assignment":
        row = conn.execute(
            "SELECT organization_id FROM organization_form_assignment WHERE assignment_id = ?",
            (entity_id,),
        ).fetchone()
        return row["organization_id"] if row else None
    return None


def normalize_jurisdiction(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip(" .,:;()[]{}\"'"))
    return cleaned.lower()


def detect_boundary_ambiguity(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    claims = conn.execute(
        """
        SELECT claim_id, entity_type, entity_id, field_path, claim_value, interpretation_note
        FROM claim
        WHERE lower(coalesce(field_path, '')) LIKE '%boundary%'
           OR lower(coalesce(field_path, '')) LIKE '%jurisdiction%'
           OR lower(coalesce(claim_value, '')) LIKE '%boundary%'
           OR lower(coalesce(claim_value, '')) LIKE '%jurisdiction%'
           OR claim_value LIKE '%境界%'
           OR claim_value LIKE '%管轄%'
           OR claim_value LIKE '%法域%'
           OR lower(coalesce(interpretation_note, '')) LIKE '%boundary%'
           OR lower(coalesce(interpretation_note, '')) LIKE '%jurisdiction%'
           OR interpretation_note LIKE '%境界%'
           OR interpretation_note LIKE '%管轄%'
           OR interpretation_note LIKE '%法域%'
        """
    ).fetchall()

    by_org: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        org_id = claim_org_id(conn, claim)
        if not org_id:
            continue
        text = " ".join(
            [
                claim["field_path"] or "",
                claim["claim_value"] or "",
                claim["interpretation_note"] or "",
            ]
        )
        if not BOUNDARY_RE.search(text):
            continue
        jurisdictions = []
        for match in JURISDICTION_RE.finditer(text):
            value = match.group(1) or match.group(2)
            if value:
                jurisdictions.append(normalize_jurisdiction(value))
        by_org[org_id].append(
            {
                "claim_id": claim["claim_id"],
                "text": snippet(text),
                "jurisdictions": sorted(set(jurisdictions)),
                "open": bool(OPEN_BOUNDARY_RE.search(text)),
                "closed": bool(CLOSED_BOUNDARY_RE.search(text)),
            }
        )

    hits = []
    for org_id, items in by_org.items():
        if len(items) < 2:
            continue
        jurisdictions = sorted({j for item in items for j in item["jurisdictions"]})
        has_open = any(item["open"] for item in items)
        has_closed = any(item["closed"] for item in items)
        if len(jurisdictions) < 2 and not (has_open and has_closed):
            continue
        org = conn.execute(
            "SELECT canonical_name FROM organization WHERE organization_id = ?",
            (org_id,),
        ).fetchone()
        hits.append(
            {
                "organization_id": org_id,
                "organization": org["canonical_name"] if org else "",
                "jurisdictions": jurisdictions,
                "open_closed_conflict": has_open and has_closed,
                "claims": items,
            }
        )
    return hits


def detect_functionalist_hindsight(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT fr.function_id, fr.confidence, fr.mechanism,
               o.canonical_name, ft.function_type_id, ft.name_en, ft.name_ja
        FROM function_record fr
        JOIN organization o ON o.organization_id = fr.organization_id
        JOIN function_type ft ON ft.function_type_id = fr.function_type_id
        WHERE fr.confidence >= 0.9
          AND (fr.claim_id IS NULL OR trim(fr.claim_id) = '')
        ORDER BY fr.confidence DESC, o.canonical_name, ft.function_type_id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def detect_biological_overimport(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in PHYSICAL_MILLER_TYPES)
    rows = conn.execute(
        f"""
        SELECT fr.function_id, fr.confidence, fr.mechanism,
               o.canonical_name, ft.function_type_id, ft.name_en, ft.name_ja
        FROM function_record fr
        JOIN organization o ON o.organization_id = fr.organization_id
        JOIN function_type ft ON ft.function_type_id = fr.function_type_id
        WHERE fr.function_type_id IN ({placeholders})
        ORDER BY ft.miller_subsystem_no, o.canonical_name
        """,
        sorted(PHYSICAL_MILLER_TYPES),
    ).fetchall()
    return [dict(row) for row in rows]


def markdown_table(headers: list[str], rows: list[list[Any]], limit: int = 20) -> str:
    if not rows:
        return "_No records detected._\n"
    shown = rows[:limit]
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in shown:
        out.append("| " + " | ".join(str(cell).replace("\n", " ").replace("|", "\\|") for cell in row) + " |")
    if len(rows) > limit:
        out.append(f"\n_Showing {limit} of {len(rows)} records._")
    return "\n".join(out) + "\n"


def build_report(results: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "# Metaphor Traps Audit",
        "",
        f"- Database: `{DB.relative_to(ROOT)}`",
        "- Scope: existing SQLite tables only; no DB writes.",
        "- Interpretation: detections are review candidates, not automatic proof of error.",
        "",
        "## Summary",
        "",
        "| Trap | Count |",
        "| --- | ---: |",
        f"| Reification | {len(results['reification'])} |",
        f"| Circular survival | {len(results['circular_survival'])} |",
        f"| Boundary ambiguity | {len(results['boundary_ambiguity'])} |",
        f"| Functionalist hindsight | {len(results['functionalist_hindsight'])} |",
        f"| Biological over-import usage check | {len(results['biological_overimport'])} |",
        "",
        "## 1. Reification",
        "",
        "Regex review of `organization.description`, `activity.description`, and `claim.interpretation_note` for organization subjects directly paired with biological verbs.",
        "",
    ]
    lines.append(
        markdown_table(
            ["table", "record_id", "organization", "field", "match", "text"],
            [
                [r["table"], r["record_id"], r["organization"], r["field"], r["match"], r["text"]]
                for r in results["reification"]
            ],
        )
    )
    lines.extend(
        [
            "Recommendation: replace organism-subject phrasing with explicit mechanism claims, or attach a source-backed interpretation note that marks the phrase as metaphorical.",
            "",
            "## 2. Circular Survival",
            "",
            "`event.dissolution_cause = 'obsolescence'` rows were checked for survival-of-the-fittest style explanations.",
            "",
        ]
    )
    lines.append(
        markdown_table(
            ["event_id", "organizations", "match", "text"],
            [[r["event_id"], r["organizations"], r["match"], r["text"]] for r in results["circular_survival"]],
        )
    )
    lines.extend(
        [
            "Recommendation: require a concrete causal chain such as technology shift, regulatory change, fiscal collapse, or successor institution, not a tautological selection label.",
            "",
            "## 3. Boundary Ambiguity",
            "",
            "Boundary-related claims were grouped by organization and flagged only when multiple jurisdiction values or open/closed boundary claims co-occurred.",
            "",
        ]
    )
    lines.append(
        markdown_table(
            ["organization_id", "organization", "jurisdictions", "open_closed_conflict", "claim_count"],
            [
                [
                    r["organization_id"],
                    r["organization"],
                    ", ".join(r["jurisdictions"]),
                    r["open_closed_conflict"],
                    len(r["claims"]),
                ]
                for r in results["boundary_ambiguity"]
            ],
        )
    )
    lines.extend(
        [
            "Recommendation: encode boundary claims with time validity and boundary dimension, for example legal jurisdiction, membership, territory, or operational network.",
            "",
            "## 4. Functionalist Hindsight",
            "",
            "`function_record.confidence >= 0.9` with `claim_id` NULL or empty.",
            "",
        ]
    )
    lines.append(
        markdown_table(
            ["function_id", "organization", "function_type", "confidence", "mechanism"],
            [
                [
                    r["function_id"],
                    r["canonical_name"],
                    f"{r['function_type_id']} / {r['name_en']}",
                    r["confidence"],
                    snippet(r["mechanism"]),
                ]
                for r in results["functionalist_hindsight"]
            ],
        )
    )
    lines.extend(
        [
            "Recommendation: either attach a source-backed claim or lower confidence until the mechanism has provenance.",
            "",
            "## 5. Biological Over-Import Usage Check",
            "",
            "Usage count for Miller physical processing subsystems at organization level: Ingestor, Distributor, Converter, Producer, Matter-Energy Storage, Extruder, Motor, Supporter.",
            "",
        ]
    )
    lines.append(
        markdown_table(
            ["function_id", "organization", "function_type", "confidence", "mechanism"],
            [
                [
                    r["function_id"],
                    r["canonical_name"],
                    f"{r['function_type_id']} / {r['name_en']}",
                    r["confidence"],
                    snippet(r["mechanism"]),
                ]
                for r in results["biological_overimport"]
            ],
        )
    )
    lines.extend(
        [
            "Recommendation: treat this as an inventory, not an error list. For physical-processing labels, require a human-readable organizational analogue in `mechanism`.",
            "",
        ]
    )
    return "\n".join(lines)


def run(db_path: Path = DB, out_path: Path = OUT_REPORT) -> dict[str, list[dict[str, Any]]]:
    with connect(db_path) as conn:
        results = {
            "reification": detect_reification(conn),
            "circular_survival": detect_circular_survival(conn),
            "boundary_ambiguity": detect_boundary_ambiguity(conn),
            "functionalist_hindsight": detect_functionalist_hindsight(conn),
            "biological_overimport": detect_biological_overimport(conn),
        }
    out_path.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit life-metaphor traps in og.db.")
    parser.add_argument("--db", type=Path, default=DB)
    parser.add_argument("--out", type=Path, default=OUT_REPORT)
    args = parser.parse_args()
    results = run(args.db, args.out)
    print(
        "metaphor traps audit: "
        f"reification={len(results['reification'])}, "
        f"circular_survival={len(results['circular_survival'])}, "
        f"boundary_ambiguity={len(results['boundary_ambiguity'])}, "
        f"functionalist_hindsight={len(results['functionalist_hindsight'])}, "
        f"biological_overimport={len(results['biological_overimport'])}"
    )


if __name__ == "__main__":
    main()
