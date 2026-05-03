#!/usr/bin/env python3
"""Phase 4 facet 鳥瞰: 全 43 ケース × 8 facet_type のカバレッジ可視化"""
import json
import sqlite3
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT = ROOT / "data" / "facet_overview.html"

FACET_TYPES = ["governance","identity","scale","membership",
               "legitimation_basis","resource_base","territory","technology"]

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT o.organization_id, o.canonical_name,
               COALESCE(o.start_date, '0000-01-01') AS sd,
               o.end_date, o.status,
               t.facet_type, COUNT(t.organization_facet_id) as n
        FROM organization o
        LEFT JOIN organization_temporal_facet t
          ON t.organization_id = o.organization_id
        WHERE o.organization_id IN (
          SELECT DISTINCT organization_id FROM function_record
        )
        GROUP BY o.organization_id, t.facet_type
        ORDER BY sd
    """).fetchall()

    # build matrix
    orgs_seen = []
    matrix = {}
    org_meta = {}
    for org_id, name, sd, ed, status, ft, n in rows:
        if org_id not in matrix:
            matrix[org_id] = {ft_: 0 for ft_ in FACET_TYPES}
            orgs_seen.append(org_id)
            org_meta[org_id] = {"name": name, "start": sd, "end": ed, "status": status}
        if ft:
            matrix[org_id][ft] = n

    # render
    rows_html = []
    for org_id in orgs_seen:
        m = org_meta[org_id]
        cells = []
        for ft in FACET_TYPES:
            n = matrix[org_id][ft]
            if n == 0:
                cls = "n0"
                txt = ""
            elif n == 1:
                cls = "n1"
                txt = "1"
            elif n <= 3:
                cls = "n2"
                txt = str(n)
            else:
                cls = "n3"
                txt = str(n)
            cells.append(f'<td class="cell {cls}">{txt}</td>')
        sd = m["start"][:4] if m["start"] else "?"
        ed = m["end"][:4] if m["end"] else ("now" if m["status"] == "active" else "?")
        total = sum(matrix[org_id].values())
        rows_html.append(
            f'<tr><td class="org">{html.escape(m["name"])}</td>'
            f'<td class="period">{sd}–{ed}</td>'
            f'<td class="status s_{m["status"]}">{m["status"]}</td>'
            + "".join(cells) +
            f'<td class="total">{total}</td></tr>'
        )

    th = "".join(f'<th>{html.escape(ft.replace("_"," "))}</th>' for ft in FACET_TYPES)

    html_doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<title>Phase 4 facet overview — 43 cases × 8 facet types</title>
<style>
body {{ font-family: -apple-system, "Hiragino Sans", sans-serif; margin: 24px; color: #222; }}
h1 {{ font-size: 1.4rem; margin-bottom: 4px; }}
.subtitle {{ color: #666; font-size: 0.85rem; margin-bottom: 18px; }}
table {{ border-collapse: collapse; font-size: 0.78rem; }}
th, td {{ border: 1px solid #ddd; padding: 4px 8px; text-align: center; }}
th {{ background: #f5f5f0; font-weight: 600; }}
td.org {{ text-align: left; max-width: 320px; font-weight: 600; }}
td.period {{ font-family: monospace; font-size: 0.72rem; color: #555; }}
td.status {{ font-size: 0.7rem; }}
td.s_active {{ color: #2E5A3F; font-weight: 600; }}
td.s_extinct {{ color: #888; }}
td.s_transformed {{ color: #B07256; }}
td.cell {{ width: 36px; height: 24px; }}
td.cell.n0 {{ background: #fafafa; color: #ccc; }}
td.cell.n1 {{ background: #d6e5d8; color: #2E5A3F; }}
td.cell.n2 {{ background: #88b89a; color: #fff; font-weight: 600; }}
td.cell.n3 {{ background: #2E5A3F; color: #fff; font-weight: 700; }}
td.total {{ font-weight: 700; background: #f7f7f5; }}
.legend {{ margin-top: 16px; font-size: 0.78rem; color: #666; display: flex; gap: 16px; }}
.legend span.swatch {{ display: inline-block; width: 20px; height: 12px; vertical-align: middle; margin-right: 4px; border: 1px solid #ccc; }}
</style></head>
<body>
<h1>Phase 4 temporal_facet 鳥瞰 — 43 完全注釈ケース × 8 facet 軸</h1>
<p class="subtitle">セルの濃さ = facet 件数。空セル = その軸では未記録 (= 不適用 / 未調査)。<br>
全 242 facet。governance 75 / identity 43 / scale 39 / membership 21 / legitimation_basis 19 / resource_base 19 / territory 15 / technology 11。</p>
<table>
<thead><tr><th>組織</th><th>期間</th><th>状態</th>{th}<th>total</th></tr></thead>
<tbody>{''.join(rows_html)}</tbody>
</table>
<div class="legend">
<span><span class="swatch" style="background:#fafafa"></span>0 件</span>
<span><span class="swatch" style="background:#d6e5d8"></span>1 件</span>
<span><span class="swatch" style="background:#88b89a"></span>2-3 件</span>
<span><span class="swatch" style="background:#2E5A3F"></span>4 件以上</span>
</div>
</body></html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"orgs: {len(orgs_seen)}, file size: {OUT.stat().st_size} bytes")

if __name__ == "__main__":
    main()
