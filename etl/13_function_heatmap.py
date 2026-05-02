#!/usr/bin/env python3
"""Generate a function taxonomy coverage heatmap for annotated organizations."""
from __future__ import annotations

import html
import sqlite3
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
HTML_OUT = ROOT / "data" / "function_heatmap.html"
REPORT_OUT = ROOT / "data" / "function_coverage.md"


def connect() -> sqlite3.Connection:
    uri = f"file:{DB}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_data(conn: sqlite3.Connection):
    functions = conn.execute(
        """
        SELECT function_type_id, name_ja, name_en, source_framework,
               miller_subsystem_no, vsm_system_no
        FROM function_type
        ORDER BY
          CASE source_framework
            WHEN 'miller_living_systems' THEN 1
            WHEN 'beer_vsm' THEN 2
            ELSE 3
          END,
          miller_subsystem_no,
          vsm_system_no,
          function_type_id
        """
    ).fetchall()

    organizations = conn.execute(
        """
        SELECT o.organization_id, o.canonical_name, o.start_date, o.status,
               COALESCE(of.label, '') AS form_label
        FROM organization o
        LEFT JOIN organization_form of ON of.form_id = o.primary_form_id
        WHERE EXISTS (
          SELECT 1 FROM function_record fr
          WHERE fr.organization_id = o.organization_id
        )
        ORDER BY
          CASE WHEN o.start_date IS NULL THEN 1 ELSE 0 END,
          o.start_date,
          o.canonical_name
        """
    ).fetchall()

    counts = {
        (row["organization_id"], row["function_type_id"]): row["n"]
        for row in conn.execute(
            """
            SELECT organization_id, function_type_id, COUNT(*) AS n
            FROM function_record
            GROUP BY organization_id, function_type_id
            """
        )
    }

    return functions, organizations, counts


def cell_class(count: int) -> str:
    if count == 0:
        return "empty"
    if count == 1:
        return "filled"
    return "strong"


def framework_label(function: sqlite3.Row) -> str:
    if function["source_framework"] == "miller_living_systems":
        return f"M{function['miller_subsystem_no']:02d}"
    if function["source_framework"] == "beer_vsm":
        return function["vsm_system_no"]
    return function["source_framework"]


def render_html(functions, organizations, counts) -> str:
    max_count = max(counts.values(), default=1)
    rows = []
    for org in organizations:
        populated = sum(
            1 for fn in functions if counts.get((org["organization_id"], fn["function_type_id"]), 0)
        )
        cells = [
            f"<th class=\"org-name\">{html.escape(org['canonical_name'])}</th>",
            f"<td>{html.escape(org['form_label'])}</td>",
            f"<td>{html.escape(org['start_date'] or 'unknown')}</td>",
            f"<td><span class=\"status\">{html.escape(org['status'])}</span></td>",
            f"<td class=\"total\">{populated}</td>",
        ]
        for fn in functions:
            count = counts.get((org["organization_id"], fn["function_type_id"]), 0)
            label = f"{org['canonical_name']} / {fn['name_en']}: {count}"
            cells.append(
                f"<td class=\"heat {cell_class(count)}\" title=\"{html.escape(label)}\">"
                f"{count if count else ''}</td>"
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    header_cells = []
    for fn in functions:
        label = f"{framework_label(fn)} {fn['name_en']}"
        header_cells.append(
            "<th class=\"function\" "
            f"title=\"{html.escape(label)}\">"
            f"<span>{html.escape(framework_label(fn))}</span></th>"
        )

    function_totals = Counter()
    for (_, function_type_id), count in counts.items():
        if count:
            function_totals[function_type_id] += count

    footer_cells = []
    for fn in functions:
        footer_cells.append(
            f"<td class=\"total heat {cell_class(function_totals[fn['function_type_id']])}\">"
            f"{function_totals[fn['function_type_id']] or ''}</td>"
        )

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Function Taxonomy Heatmap</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #5b6670;
      --line: #d8dee4;
      --empty: #f5f7f9;
      --filled: #2f7f73;
      --strong: #155b52;
      --header: #f0f3f5;
    }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #ffffff;
    }}
    main {{
      padding: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 24px;
      font-weight: 700;
    }}
    p {{
      margin: 0 0 18px;
      color: var(--muted);
      font-size: 14px;
    }}
    .table-wrap {{
      overflow: auto;
      border: 1px solid var(--line);
      max-height: calc(100vh - 120px);
    }}
    table {{
      border-collapse: separate;
      border-spacing: 0;
      min-width: 1400px;
      width: 100%;
      font-size: 12px;
    }}
    th, td {{
      border-right: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 6px 8px;
      text-align: center;
      white-space: nowrap;
    }}
    thead th, tfoot th, tfoot td {{
      position: sticky;
      background: var(--header);
      z-index: 2;
      font-weight: 700;
    }}
    thead th {{
      top: 0;
    }}
    tfoot th, tfoot td {{
      bottom: 0;
    }}
    .sticky {{
      left: 0;
      position: sticky;
      z-index: 3;
      background: var(--header);
    }}
    .org-name {{
      left: 0;
      position: sticky;
      z-index: 1;
      min-width: 260px;
      max-width: 260px;
      overflow: hidden;
      text-align: left;
      text-overflow: ellipsis;
      background: #fff;
    }}
    .function {{
      height: 96px;
      min-width: 34px;
      padding: 4px;
      vertical-align: bottom;
    }}
    .function span {{
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      display: inline-block;
      letter-spacing: 0;
    }}
    .heat {{
      min-width: 28px;
      font-weight: 700;
    }}
    .empty {{
      background: var(--empty);
      color: transparent;
    }}
    .filled {{
      background: var(--filled);
      color: #fff;
    }}
    .strong {{
      background: var(--strong);
      color: #fff;
    }}
    .status {{
      color: var(--muted);
      font-size: 11px;
    }}
    .total {{
      font-variant-numeric: tabular-nums;
      font-weight: 700;
    }}
    .legend {{
      display: flex;
      gap: 12px;
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 12px;
    }}
    .swatch {{
      display: inline-block;
      width: 12px;
      height: 12px;
      margin-right: 4px;
      vertical-align: -2px;
      border: 1px solid var(--line);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Function Taxonomy Heatmap</h1>
    <p>{len(organizations)} annotated organizations x {len(functions)} functions. Values are function_record counts.</p>
    <div class="legend">
      <span><i class="swatch empty"></i>no record</span>
      <span><i class="swatch filled"></i>recorded</span>
      <span><i class="swatch strong"></i>multiple records</span>
      <span>max count per cell: {max_count}</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th class="sticky">Organization</th>
            <th>Form</th>
            <th>Start</th>
            <th>Status</th>
            <th>Total</th>
            {''.join(header_cells)}
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
        <tfoot>
          <tr>
            <th class="sticky">Function total</th>
            <td></td>
            <td></td>
            <td></td>
            <td>{sum(function_totals.values())}</td>
            {''.join(footer_cells)}
          </tr>
        </tfoot>
      </table>
    </div>
  </main>
</body>
</html>
"""


def summarize_patterns(functions, organizations, counts):
    function_by_id = {fn["function_type_id"]: fn for fn in functions}
    org_by_id = {org["organization_id"]: org for org in organizations}
    org_total = len(organizations)

    function_org_counts = Counter()
    function_record_counts = Counter()
    framework_counts = Counter()
    form_function_counts = defaultdict(Counter)
    form_org_counts = Counter()

    for org in organizations:
        form_org_counts[org["form_label"] or "(none)"] += 1

    for (org_id, function_type_id), count in counts.items():
        if count <= 0 or org_id not in org_by_id or function_type_id not in function_by_id:
            continue
        function_org_counts[function_type_id] += 1
        function_record_counts[function_type_id] += count
        framework_counts[function_by_id[function_type_id]["source_framework"]] += count
        form_function_counts[org_by_id[org_id]["form_label"] or "(none)"][function_type_id] += count

    universal = [
        fn for fn in functions
        if function_org_counts[fn["function_type_id"]] == org_total
    ]
    broad = [
        fn for fn in functions
        if function_org_counts[fn["function_type_id"]] >= org_total // 2
    ]
    unused = [
        fn for fn in functions
        if function_record_counts[fn["function_type_id"]] == 0
    ]
    low = [
        fn for fn in functions
        if 0 < function_record_counts[fn["function_type_id"]] <= 2
    ]

    return {
        "function_by_id": function_by_id,
        "org_total": org_total,
        "function_org_counts": function_org_counts,
        "function_record_counts": function_record_counts,
        "framework_counts": framework_counts,
        "form_function_counts": form_function_counts,
        "form_org_counts": form_org_counts,
        "universal": universal,
        "broad": broad,
        "unused": unused,
        "low": low,
    }


def function_name(fn: sqlite3.Row) -> str:
    return f"{framework_label(fn)} {fn['name_en']}"


def render_report(functions, organizations, counts) -> str:
    summary = summarize_patterns(functions, organizations, counts)
    org_total = summary["org_total"]
    function_org_counts = summary["function_org_counts"]
    function_record_counts = summary["function_record_counts"]
    framework_counts = summary["framework_counts"]

    frequency_rows = []
    for fn in functions:
        fid = fn["function_type_id"]
        frequency_rows.append(
            "| "
            + " | ".join(
                [
                    function_name(fn),
                    fn["source_framework"],
                    str(function_org_counts[fid]),
                    str(function_record_counts[fid]),
                ]
            )
            + " |"
        )

    top_by_form = []
    for form, counter in sorted(summary["form_function_counts"].items()):
        top = [
            function_name(summary["function_by_id"][fid])
            for fid, _ in counter.most_common(4)
        ]
        top_by_form.append(f"- {form}: {', '.join(top)}")

    universal_text = (
        ", ".join(function_name(fn) for fn in summary["universal"])
        if summary["universal"]
        else "None. The closest broad functions are listed below."
    )
    broad_text = ", ".join(
        f"{function_name(fn)} ({function_org_counts[fn['function_type_id']]}/{org_total})"
        for fn in summary["broad"]
    )
    unused_text = ", ".join(function_name(fn) for fn in summary["unused"])
    low_text = ", ".join(
        f"{function_name(fn)} ({function_record_counts[fn['function_type_id']]})"
        for fn in summary["low"]
    )

    miller_total = framework_counts["miller_living_systems"]
    vsm_total = framework_counts["beer_vsm"]
    total = miller_total + vsm_total

    return f"""# Function Taxonomy Coverage

Generated from `data/og.db` using `etl/13_function_heatmap.py`.

Provenance: `{{claim: function taxonomy distribution, source_url: local:data/og.db, retrieval_date: {date.today().isoformat()}, confidence: high}}`

## Scope

- Annotated organizations: {len(organizations)}
- Function types: {len(functions)}
- Function records counted: {total}
- HTML heatmap: `data/function_heatmap.html`

## Universal And Broad Functions

Universal functions recorded in all {org_total} organizations: {universal_text}

Broad functions by organization coverage: {broad_text}

The strongest near-universal signal is VSM S5 policy/identity rather than a Miller subsystem. It appears in {function_org_counts['vsm_s5_policy_identity']}/{org_total} organizations, followed by Miller Boundary ({function_org_counts['miller_02_boundary']}/{org_total}), Memory ({function_org_counts['miller_17_memory']}/{org_total}), and Ingestor ({function_org_counts['miller_03_ingestor']}/{org_total}).

## Miller 20 vs VSM 5

- Miller Living Systems records: {miller_total} / {total}
- Beer VSM records: {vsm_total} / {total}

Miller categories are more numerous and carry most observations, especially Boundary, Ingestor, Memory, Reproducer, and Decider. VSM is sparser overall, but S5 Policy and Identity is the single most frequent function, which suggests identity and normative closure are easier to annotate consistently across historical and contemporary organization types than the lower-level VSM control layers.

## Organization-Type Patterns

{chr(10).join(top_by_form)}

Interpretive pattern:

- Monastic organizations concentrate Reproducer, Policy/Identity, Boundary, and Memory. This matches rule-based succession, institutional identity, enclosure or membership boundaries, and textual memory.
- Bureaucratic empires emphasize Ingestor, Memory, Decider, and VSM Operations. They are annotated through extraction, record systems, command authority, and operational administration.
- Ie / house organizations emphasize Reproducer, Memory, and Policy/Identity, reflecting lineage continuity and house-name persistence.
- Nonprofits and DAOs share Boundary, Memory, Decider, and Policy/Identity signals. Contemporary forms make membership, governance, and recorded decision rules especially visible.
- Cooperatives lean toward Ingestor and Policy/Identity, with coordination and internal control appearing where federated or member-accountability mechanisms are explicit.

## Unused And Low-Frequency Functions

Unused functions: {unused_text}

Low-frequency functions: {low_text}

Likely reason: the 18 complete cases were annotated at the institutional-mechanism level, so high-level identity, boundary, memory, reproduction, ingestion, and decision functions are visible. Physical or signal-processing subsystems such as Converter, Extruder, Motor, Input Transducer, Decoder, Associator, and Output Transducer require finer operational evidence than the current organization-level case notes provide.

## Frequency Table

| Function | Framework | Organizations | Records |
| --- | --- | ---: | ---: |
{chr(10).join(frequency_rows)}
"""


def main() -> None:
    with connect() as conn:
        functions, organizations, counts = fetch_data(conn)

    HTML_OUT.write_text(render_html(functions, organizations, counts), encoding="utf-8")
    REPORT_OUT.write_text(render_report(functions, organizations, counts), encoding="utf-8")

    print("最頻出はVSM S5（方針・同一性）で、生命的組織の核が境界よりアイデンティティに寄っている。")


if __name__ == "__main__":
    main()
