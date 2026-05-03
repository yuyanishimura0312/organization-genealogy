#!/usr/bin/env python3
"""Generate statistics crosstabs from data/og.db."""

from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "og.db"
JSON_PATH = ROOT / "data" / "statistics.json"
REPORT_PATH = ROOT / "data" / "statistics_report.md"
REPORT_DATE = date.today().isoformat()
REPORT_YEAR = date.today().year


YEAR_RE = re.compile(r"^-?(\d{1,4})")


def fetch_dicts(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql, params)]


def parse_year(value: str | None) -> int | None:
    if not value:
        return None
    match = YEAR_RE.match(value)
    if not match:
        return None
    return int(match.group(1))


def longevity_bucket(start_date: str | None, end_date: str | None, status: str) -> str:
    start_year = parse_year(start_date)
    if start_year is None:
        return "unknown"

    end_year = parse_year(end_date)
    if end_year is None:
        if status != "active":
            return "unknown"
        end_year = REPORT_YEAR

    years = max(0, end_year - start_year)
    if years < 10:
        return "0-9 years"
    if years < 50:
        return "10-49 years"
    if years < 100:
        return "50-99 years"
    if years < 500:
        return "100-499 years"
    return "500+ years"


def org_eras(conn: sqlite3.Connection) -> dict[str, str]:
    rows = fetch_dicts(
        conn,
        """
        SELECT
          o.organization_id,
          f.label AS era
        FROM organization o
        LEFT JOIN organization_form_assignment a
          ON a.organization_id = o.organization_id
        LEFT JOIN organization_form f
          ON f.form_id = a.form_id
         AND f.taxonomy_name = 'historical_era'
        ORDER BY o.organization_id, f.label
        """,
    )
    era_labels: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["era"]:
            era_labels[row["organization_id"]].add(row["era"])
        else:
            era_labels.setdefault(row["organization_id"], set())
    return {
        organization_id: ",".join(sorted(labels)) if labels else "未分類"
        for organization_id, labels in era_labels.items()
    }


def count_rows(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    counts: Counter[tuple] = Counter(tuple(row[key] for key in keys) for row in rows)
    result = []
    for key_values, count in sorted(counts.items(), key=lambda item: (*item[0],)):
        item = dict(zip(keys, key_values))
        item["count"] = count
        result.append(item)
    return result


def organization_lifecycle(conn: sqlite3.Connection, eras: dict[str, str]) -> list[dict]:
    rows = fetch_dicts(
        conn,
        """
        SELECT organization_id, status, start_date, end_date
        FROM organization
        ORDER BY organization_id
        """,
    )
    expanded = []
    for row in rows:
        expanded.append(
            {
                "era": eras[row["organization_id"]],
                "status": row["status"],
                "longevity_years": longevity_bucket(
                    row["start_date"], row["end_date"], row["status"]
                ),
            }
        )
    return count_rows(expanded, ("era", "status", "longevity_years"))


def relation_by_era(conn: sqlite3.Connection, eras: dict[str, str]) -> list[dict]:
    rows = fetch_dicts(
        conn,
        """
        SELECT source_organization_id, relation_type
        FROM relation
        ORDER BY relation_id
        """,
    )
    expanded = [
        {
            "era": eras.get(row["source_organization_id"], "未分類"),
            "relation_type": row["relation_type"],
        }
        for row in rows
    ]
    return count_rows(expanded, ("era", "relation_type"))


def form_taxonomy_counts(conn: sqlite3.Connection) -> list[dict]:
    return fetch_dicts(
        conn,
        """
        SELECT
          f.taxonomy_name AS form_taxonomy,
          COUNT(DISTINCT a.organization_id) AS organization_count,
          COUNT(*) AS assignment_count
        FROM organization_form_assignment a
        JOIN organization_form f ON f.form_id = a.form_id
        GROUP BY f.taxonomy_name
        ORDER BY organization_count DESC, form_taxonomy
        """,
    )


def function_by_era(conn: sqlite3.Connection, eras: dict[str, str]) -> list[dict]:
    rows = fetch_dicts(
        conn,
        """
        SELECT fr.organization_id, ft.name_en AS function_type
        FROM function_record fr
        JOIN function_type ft ON ft.function_type_id = fr.function_type_id
        ORDER BY fr.function_id
        """,
    )
    expanded = [
        {
            "function_type": row["function_type"],
            "era": eras.get(row["organization_id"], "未分類"),
        }
        for row in rows
    ]
    return count_rows(expanded, ("function_type", "era"))


def source_redistribution(conn: sqlite3.Connection) -> list[dict]:
    return fetch_dicts(
        conn,
        """
        SELECT
          COALESCE(redistribution, '未設定') AS redistribution,
          source_type,
          COUNT(*) AS count
        FROM source
        GROUP BY redistribution, source_type
        ORDER BY redistribution, source_type
        """,
    )


def claim_usage(conn: sqlite3.Connection) -> list[dict]:
    return fetch_dicts(
        conn,
        """
        SELECT value_kind, entity_type, COUNT(*) AS count
        FROM claim
        GROUP BY value_kind, entity_type
        ORDER BY value_kind, entity_type
        """,
    )


def totals(conn: sqlite3.Connection) -> dict[str, int]:
    table_names = [
        "organization",
        "relation",
        "organization_form_assignment",
        "function_record",
        "source",
        "claim",
    ]
    return {
        name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in table_names
    }


def top_row(rows: list[dict], count_key: str = "count") -> dict:
    return max(rows, key=lambda row: row[count_key]) if rows else {}


def table(headers: list[str], rows: list[dict]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def interpretations(data: dict) -> dict[str, list[str]]:
    lifecycle_top = top_row(data["crosstabs"]["era_status_longevity_years"])
    relation_top = top_row(data["crosstabs"]["era_relation_type"])
    form_top = top_row(data["crosstabs"]["form_taxonomy_organization"], "organization_count")
    function_top = top_row(data["crosstabs"]["function_type_era"])
    source_top = top_row(data["crosstabs"]["source_redistribution_source_type"])
    claim_top = top_row(data["crosstabs"]["claim_value_kind_entity_type"])

    return {
        "era_status_longevity_years": [
            f"最多セルは {lifecycle_top.get('era')} × {lifecycle_top.get('status')} × {lifecycle_top.get('longevity_years')} の {lifecycle_top.get('count')} 件。",
            "開始年がない、または非 active で終了年がない組織は longevity_years を unknown に分類した。",
        ],
        "era_relation_type": [
            f"最多セルは {relation_top.get('era')} × {relation_top.get('relation_type')} の {relation_top.get('count')} 件。",
            "relation の era は source_organization_id 側の historical_era 付与から集計した。",
        ],
        "form_taxonomy_organization": [
            f"最も多く組織に付与されている form_taxonomy は {form_top.get('form_taxonomy')} で {form_top.get('organization_count')} 組織。",
            "organization_count は重複 assignment を除いた distinct organization 数。",
        ],
        "function_type_era": [
            f"最多セルは {function_top.get('function_type')} × {function_top.get('era')} の {function_top.get('count')} 件。",
            "function_record は function_type ごとに、対象組織の historical_era で集計した。",
        ],
        "source_redistribution_source_type": [
            f"最多セルは {source_top.get('redistribution')} × {source_top.get('source_type')} の {source_top.get('count')} 件。",
            "redistribution が NULL の source は 未設定 として集計した。",
        ],
        "claim_value_kind_entity_type": [
            f"最多セルは {claim_top.get('value_kind')} × {claim_top.get('entity_type')} の {claim_top.get('count')} 件。",
            "claim は value_kind と entity_type の組み合わせ別に使用パターンを数えた。",
        ],
    }


def discoveries(data: dict) -> list[str]:
    crosstabs = data["crosstabs"]
    totals_data = data["metadata"]["table_counts"]
    unclassified_lifecycle = sum(
        row["count"]
        for row in crosstabs["era_status_longevity_years"]
        if row["era"] == "未分類"
    )
    org_total = totals_data["organization"]
    unknown_longevity = sum(
        row["count"]
        for row in crosstabs["era_status_longevity_years"]
        if row["longevity_years"] == "unknown"
    )
    relation_counter = defaultdict(int)
    for row in crosstabs["era_relation_type"]:
        relation_counter[row["relation_type"]] += row["count"]
    top_relation, top_relation_count = max(relation_counter.items(), key=lambda item: item[1])
    source_public = sum(
        row["count"]
        for row in crosstabs["source_redistribution_source_type"]
        if row["redistribution"] == "public_redistributable"
    )
    present_claims = sum(
        row["count"]
        for row in crosstabs["claim_value_kind_entity_type"]
        if row["value_kind"] == "present"
    )

    return [
        f"historical_era 未分類は {unclassified_lifecycle}/{org_total} 組織で、時代分類はまだ一部のケースに偏っている。",
        f"longevity_years unknown は {unknown_longevity}/{org_total} 組織で、寿命分析の主な制約になっている。",
        f"relation_type は {top_relation} が最多で {top_relation_count}/{totals_data['relation']} 関係を占める。",
        f"public_redistributable source は {source_public}/{totals_data['source']} 件で、再配布可能な出典は少数派。",
        f"claim.value_kind は present が {present_claims}/{totals_data['claim']} 件で中心的に使われている。",
    ]


def markdown_report(data: dict) -> str:
    crosstabs = data["crosstabs"]
    interp = data["interpretations"]
    findings = data["findings"]
    metadata = data["metadata"]

    sections = [
        "# 組織系譜分析 統計クロスタブレポート",
        "",
        f"- generated_at: {metadata['generated_at']}",
        f"- database: {metadata['database']}",
        f"- table_counts: {json.dumps(metadata['table_counts'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## 1. era × status × longevity_years",
        "",
        table(["era", "status", "longevity_years", "count"], crosstabs["era_status_longevity_years"]),
        "",
        "\n".join(f"- {line}" for line in interp["era_status_longevity_years"]),
        "",
        "## 2. era × relation_type",
        "",
        table(["era", "relation_type", "count"], crosstabs["era_relation_type"]),
        "",
        "\n".join(f"- {line}" for line in interp["era_relation_type"]),
        "",
        "## 3. form_taxonomy × organization 件数",
        "",
        table(
            ["form_taxonomy", "organization_count", "assignment_count"],
            crosstabs["form_taxonomy_organization"],
        ),
        "",
        "\n".join(f"- {line}" for line in interp["form_taxonomy_organization"]),
        "",
        "## 4. function_type × era 件数",
        "",
        table(["function_type", "era", "count"], crosstabs["function_type_era"]),
        "",
        "\n".join(f"- {line}" for line in interp["function_type_era"]),
        "",
        "## 5. source.redistribution × source_type",
        "",
        table(
            ["redistribution", "source_type", "count"],
            crosstabs["source_redistribution_source_type"],
        ),
        "",
        "\n".join(f"- {line}" for line in interp["source_redistribution_source_type"]),
        "",
        "## 6. claim.value_kind × entity_type",
        "",
        table(["value_kind", "entity_type", "count"], crosstabs["claim_value_kind_entity_type"]),
        "",
        "\n".join(f"- {line}" for line in interp["claim_value_kind_entity_type"]),
        "",
        "## 総合的な発見",
        "",
        "\n".join(f"{index}. {line}" for index, line in enumerate(findings, start=1)),
        "",
    ]
    return "\n".join(sections)


def build_statistics() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        eras = org_eras(conn)
        data = {
            "metadata": {
                "generated_at": REPORT_DATE,
                "database": str(DB_PATH.relative_to(ROOT)),
                "table_counts": totals(conn),
                "notes": [
                    "era is derived from organization_form taxonomy_name='historical_era'.",
                    "Organizations without historical_era assignment are grouped as 未分類.",
                    "longevity_years is bucketed from start_date/end_date; active organizations without end_date use the report year.",
                    "Non-active organizations without end_date and organizations without start_date are grouped as unknown longevity.",
                ],
            },
            "crosstabs": {
                "era_status_longevity_years": organization_lifecycle(conn, eras),
                "era_relation_type": relation_by_era(conn, eras),
                "form_taxonomy_organization": form_taxonomy_counts(conn),
                "function_type_era": function_by_era(conn, eras),
                "source_redistribution_source_type": source_redistribution(conn),
                "claim_value_kind_entity_type": claim_usage(conn),
            },
        }
    data["interpretations"] = interpretations(data)
    data["findings"] = discoveries(data)
    return data


def main() -> None:
    data = build_statistics()
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(markdown_report(data), encoding="utf-8")
    print(f"Wrote {JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
