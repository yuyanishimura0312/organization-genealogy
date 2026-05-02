#!/usr/bin/env python3
"""系譜ネットワーク SVG 生成

18 完全注釈ケース + 13 relation エッジを SVG で可視化。
時間軸 (X) × エッジ密度ベース Y 配置。
relation_type で線種・色を区別。
"""
import json
import math
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT = ROOT / "data" / "genealogy_network.svg"

# Layout
W, H = 1280, 720
PAD_L, PAD_R, PAD_T, PAD_B = 80, 60, 60, 80


def parse_year(date_str):
    if not date_str:
        return None
    s = date_str[:4]
    if not s or s == "9999":
        return None
    try:
        return int(s)
    except Exception:
        return None


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get only fully-annotated organizations
    rows = cur.execute("""
        SELECT o.organization_id, o.canonical_name, o.start_date, o.end_date, o.status,
               (SELECT COUNT(*) FROM relation WHERE source_organization_id=o.organization_id OR target_organization_id=o.organization_id) as edges
        FROM organization o
        WHERE EXISTS (SELECT 1 FROM function_record fr WHERE fr.organization_id=o.organization_id)
        ORDER BY o.start_date
    """).fetchall()

    nodes = []
    for r in rows:
        oid, name, sd, ed, status, edges = r
        sy = parse_year(sd)
        ey = parse_year(ed)
        if sy is None:
            sy = 2010  # Hadza fallback
        nodes.append({
            "id": oid,
            "name": name,
            "start_year": sy,
            "end_year": ey,
            "status": status,
            "edges": edges,
        })

    # X axis: log-ish year mapping (古代を圧縮しつつ 6c-21c をバランス)
    # We use a piecewise: pre-1000 compressed, 1000-2030 linear-ish
    YEAR_MIN = 500
    YEAR_MAX = 2030

    def year_to_x(y):
        if y < YEAR_MIN:
            y = YEAR_MIN
        if y > YEAR_MAX:
            y = YEAR_MAX
        # Piecewise: 500-1500 takes 30% of width, 1500-2030 takes 70%
        if y <= 1500:
            frac = 0.3 * (y - YEAR_MIN) / (1500 - YEAR_MIN)
        else:
            frac = 0.3 + 0.7 * (y - 1500) / (YEAR_MAX - 1500)
        return PAD_L + frac * (W - PAD_L - PAD_R)

    # Y placement: stagger to avoid overlap
    # group nodes by 100-year bucket and stack within
    nodes.sort(key=lambda n: n["start_year"])
    bucket = {}
    for n in nodes:
        b = (n["start_year"] // 100) * 100
        bucket.setdefault(b, []).append(n)

    avail_h = H - PAD_T - PAD_B
    rows_count = max(8, len(nodes))
    for b, ns in bucket.items():
        for i, n in enumerate(ns):
            # within-bucket stack 0..len-1
            n["_offset"] = i

    # Y position with simple horizontal-band staggering
    bands = 7
    band_h = avail_h / bands
    placed = []
    for n in nodes:
        # try band 0..bands-1
        x = year_to_x(n["start_year"])
        chosen = None
        for band in range(bands):
            y = PAD_T + (band + 0.5) * band_h
            ok = True
            for p in placed:
                if abs(p["y"] - y) < 30 and abs(p["x"] - x) < 110:
                    ok = False; break
            if ok:
                chosen = (band, y); break
        if chosen is None:
            band = len(placed) % bands
            y = PAD_T + (band + 0.5) * band_h
        else:
            band, y = chosen
        n["x"] = x
        n["y"] = y
        placed.append(n)

    # Get relations among these nodes
    node_ids = {n["id"] for n in nodes}
    rel_rows = cur.execute("""
        SELECT source_organization_id, target_organization_id, relation_type, confidence
        FROM relation
    """).fetchall()
    edges = []
    for src, tgt, rtype, conf in rel_rows:
        if src in node_ids and tgt in node_ids:
            edges.append({"src": src, "tgt": tgt, "type": rtype, "conf": conf or 0.5})

    # SVG construction
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system,system-ui,sans-serif">')
    svg.append('<style>')
    svg.append('text { font-size: 11px; }')
    svg.append('.node-label { font-size: 11.5px; font-weight: 600; fill: #1a1a1a; }')
    svg.append('.node-date { font-size: 9.5px; fill: #6b6b6b; font-family: monospace; }')
    svg.append('.year-tick { font-size: 10px; fill: #999; font-family: monospace; }')
    svg.append('.edge-label { font-size: 9px; fill: #555; }')
    svg.append('@media (prefers-color-scheme: dark) {')
    svg.append('  .bg { fill: #121212; }')
    svg.append('  .node-label { fill: #e0e0e0; }')
    svg.append('  .node-date { fill: #aaa; }')
    svg.append('  .year-tick { fill: #777; }')
    svg.append('  .edge-label { fill: #999; }')
    svg.append('}')
    svg.append('</style>')

    # Background
    svg.append(f'<rect class="bg" width="{W}" height="{H}" fill="#f7f7f5"/>')
    svg.append(f'<rect class="bg" width="{W}" height="{H}" fill="url(#bg-pattern)" opacity="0.05"/>')

    # X axis (timeline)
    axis_y = H - PAD_B + 16
    svg.append(f'<line x1="{PAD_L}" y1="{axis_y}" x2="{W-PAD_R}" y2="{axis_y}" stroke="#999" stroke-width="1"/>')
    for y_year in [500, 800, 1100, 1400, 1700, 1900, 2000, 2026]:
        x = year_to_x(y_year)
        svg.append(f'<line x1="{x}" y1="{axis_y-4}" x2="{x}" y2="{axis_y+4}" stroke="#999" stroke-width="1"/>')
        label = str(y_year) if y_year < 2000 else str(y_year)
        svg.append(f'<text class="year-tick" x="{x}" y="{axis_y+18}" text-anchor="middle">{label}</text>')

    # Era bands (light vertical bands)
    eras = [
        (500, 1500, "中世", "#f5efe8"),
        (1500, 1800, "近世", "#ebe1d6"),
        (1800, 1945, "近代", "#f0e8d8"),
        (1945, 2030, "現代", "#e8e8e0"),
    ]
    for ys, ye, label, col in eras:
        xs = year_to_x(ys); xe = year_to_x(ye)
        svg.append(f'<rect x="{xs}" y="{PAD_T-8}" width="{xe-xs}" height="{H-PAD_T-PAD_B+8}" fill="{col}" opacity="0.4"/>')
        svg.append(f'<text x="{(xs+xe)/2}" y="{PAD_T-12}" text-anchor="middle" font-size="11" fill="#888">{label}</text>')

    # Edges
    type_colors = {
        "succession": "#2e5a3f",
        "schism": "#b07256",
        "knowledge_transfer": "#4a7a8c",
        "mimetic_isomorphism": "#8a70a0",
        "competition": "#c66060",
        "merger": "#5a8a4a",
    }
    type_dasharray = {
        "succession": "",
        "schism": "6 3",
        "knowledge_transfer": "4 3",
        "mimetic_isomorphism": "3 3",
        "competition": "8 4",
    }

    nodemap = {n["id"]: n for n in nodes}
    for e in edges:
        src = nodemap[e["src"]]; tgt = nodemap[e["tgt"]]
        col = type_colors.get(e["type"], "#888")
        dash = type_dasharray.get(e["type"], "")
        opacity = max(0.3, e["conf"])
        # Curve control point
        cx = (src["x"] + tgt["x"]) / 2
        cy = (src["y"] + tgt["y"]) / 2 - 30
        path = f'M {src["x"]} {src["y"]} Q {cx} {cy} {tgt["x"]} {tgt["y"]}'
        svg.append(f'<path d="{path}" stroke="{col}" stroke-width="1.6" fill="none" opacity="{opacity:.2f}" stroke-dasharray="{dash}" marker-end="url(#arrow-{e["type"]})"/>')

    # Arrow markers
    svg.append('<defs>')
    for t, c in type_colors.items():
        svg.append(f'<marker id="arrow-{t}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">')
        svg.append(f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/>')
        svg.append('</marker>')
    svg.append('</defs>')

    # Node circles + labels
    for n in nodes:
        # Lifespan bar (start to end)
        bar_y = n["y"] + 10
        if n["end_year"]:
            x_end = year_to_x(n["end_year"])
            svg.append(f'<line x1="{n["x"]}" y1="{bar_y}" x2="{x_end}" y2="{bar_y}" stroke="#999" stroke-width="2" opacity="0.5"/>')
        else:
            x_end = year_to_x(2026)
            svg.append(f'<line x1="{n["x"]}" y1="{bar_y}" x2="{x_end}" y2="{bar_y}" stroke="#2e5a3f" stroke-width="2" opacity="0.6"/>')
            # Active marker (right edge arrow)
            svg.append(f'<text x="{x_end+3}" y="{bar_y+4}" font-size="10" fill="#2e5a3f">▶</text>')

        # Node circle
        size_radius = 6 + min(n["edges"], 5) * 1.5
        if n["status"] == "active":
            fill, stroke = "#2e5a3f", "#1d3d2a"
        elif n["status"] == "extinct":
            fill, stroke = "#b07256", "#7a4a3a"
        elif n["status"] == "transformed":
            fill, stroke = "#c5a050", "#8a7035"
        else:
            fill, stroke = "#8a8a8a", "#555"
        svg.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{size_radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')

        # Name label (shortened)
        short_name = n["name"]
        # Strip parentheticals
        if "(" in short_name:
            short_name = short_name.split("(")[0].strip()
        if "/" in short_name:
            short_name = short_name.split("/")[0].strip()
        if len(short_name) > 14:
            short_name = short_name[:13] + "…"

        # Anchor
        text_anchor = "middle"
        text_y = n["y"] - size_radius - 4
        svg.append(f'<text class="node-label" x="{n["x"]}" y="{text_y}" text-anchor="{text_anchor}">{short_name}</text>')

        # Date label
        date_str = str(n["start_year"])
        if n["end_year"]:
            date_str += f"-{n['end_year']}"
        else:
            date_str += "-"
        svg.append(f'<text class="node-date" x="{n["x"]}" y="{n["y"]+size_radius+12}" text-anchor="middle">{date_str}</text>')

    # Legend
    legend_y = 24
    legend_x = PAD_L
    svg.append(f'<text x="{legend_x}" y="{legend_y}" font-size="13" font-weight="700" fill="#1a1a1a">系譜ネットワーク (18 ノード × 13 エッジ)</text>')
    legend_y += 22
    legend_items = [
        ("succession", "継承"),
        ("schism", "分派"),
        ("knowledge_transfer", "知識伝達"),
        ("mimetic_isomorphism", "模倣的同型化"),
        ("competition", "競争"),
    ]
    for i, (t, label) in enumerate(legend_items):
        col = type_colors[t]
        dash = type_dasharray.get(t, "")
        x = legend_x + i * 145
        svg.append(f'<line x1="{x}" y1="{legend_y}" x2="{x+24}" y2="{legend_y}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>')
        svg.append(f'<text x="{x+30}" y="{legend_y+4}" font-size="10.5" fill="#444">{label}</text>')

    # Status legend (right side)
    status_x = W - PAD_R - 250
    status_y = 24
    svg.append(f'<text x="{status_x+12}" y="{status_y+4}" font-size="10.5" fill="#444">状態</text>')
    status_legend = [("#2e5a3f", "active"), ("#c5a050", "transformed"), ("#b07256", "extinct"), ("#8a8a8a", "unknown")]
    for i, (col, lab) in enumerate(status_legend):
        x = status_x + 30 + i * 65
        svg.append(f'<circle cx="{x}" cy="{status_y}" r="6" fill="{col}" stroke="#000" stroke-width="0.5" opacity="0.85"/>')
        svg.append(f'<text x="{x+10}" y="{status_y+4}" font-size="9.5" fill="#444">{lab}</text>')

    svg.append('</svg>')
    OUT.write_text("\n".join(svg), encoding="utf-8")

    print(f"wrote {OUT}")
    print(f"nodes: {len(nodes)}")
    print(f"edges shown: {len(edges)}")
    print(f"file size: {OUT.stat().st_size} bytes")
    conn.close()


if __name__ == "__main__":
    main()
