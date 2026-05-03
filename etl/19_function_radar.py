#!/usr/bin/env python3
"""25 機能レーダーチャート SVG 生成

各 era から 6 代表 (ベネディクト会, Cistercians, ハンザ, VOC, Mondragón, MakerDAO) を選び、
25 機能 (Miller 20 サブシステム + Beer VSM 5 systems) を軸に半透明 polygon を重ねる。
ダーク/ライトテーマ対応。
"""
from __future__ import annotations

import math
import sqlite3
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT = ROOT / "data" / "function_vector_radar.svg"

W, H = 1200, 920

# 6 代表組織 (era 順)
REPRESENTATIVES = [
    # (organization_id, short label, era label, color)
    ("2cf732ca2e44458b8d793880b59a1b5d", "ベネディクト会", "中世初期 (529–)",     "#7d6b5c"),
    ("d9c2571497d84171ad42eb73e6c6799c", "Cistercians",   "中世盛期 (1098–)",   "#5a8a6b"),
    ("769ae2b129534516b257581907423f68", "ハンザ同盟",     "中世後期 (1159–1669)", "#c08a3e"),
    ("9e99525267034e16af5863b9db8e63e6", "VOC",           "近世 (1602–1799)",    "#b25c5c"),
    ("939cb4daeba04b9e963be147402d9e96", "Mondragón",     "現代 (1956–)",        "#4d7ea8"),
    ("464be7e725f045afa3f2bd0750c04dbe", "MakerDAO",      "現代 (2017–)",        "#9560a0"),
]


def main():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = conn.cursor()

    # Fetch 25 functions in canonical order: Miller 1-20, then VSM S1-S5
    func_rows = cur.execute(
        """
        SELECT function_type_id, name_ja, name_en, source_framework,
               miller_subsystem_no, vsm_system_no
        FROM function_type
        ORDER BY
          CASE source_framework WHEN 'miller_living_systems' THEN 1
                                WHEN 'beer_vsm' THEN 2 ELSE 3 END,
          miller_subsystem_no, vsm_system_no
        """
    ).fetchall()

    funcs = []
    for fid, ja, en, fw, mno, vsm in func_rows:
        funcs.append({
            "id": fid, "ja": ja, "en": en, "fw": fw,
            "mno": mno, "vsm": vsm,
        })
    n_axes = len(funcs)  # 25

    # Fetch function_record per representative
    org_ids = [r[0] for r in REPRESENTATIVES]
    placeholders = ",".join("?" for _ in org_ids)
    fr_rows = cur.execute(
        f"""
        SELECT organization_id, function_type_id, confidence
        FROM function_record
        WHERE organization_id IN ({placeholders})
        """,
        org_ids,
    ).fetchall()

    # value matrix: [oid][fid] = confidence (or 0)
    values = {oid: {f["id"]: 0.0 for f in funcs} for oid in org_ids}
    for oid, fid, conf in fr_rows:
        values[oid][fid] = float(conf or 0.5)

    # ---- Geometry ----
    cx, cy = W / 2, H / 2 + 20  # shift down to leave room for title
    radius = 320  # outer radius for value=1.0
    rings = [0.25, 0.5, 0.75, 1.0]

    # Angles: start at top, go clockwise, evenly spaced
    def angle_for(i):
        return -math.pi / 2 + 2 * math.pi * i / n_axes

    def axis_xy(i, val):
        a = angle_for(i)
        r = radius * val
        return cx + r * math.cos(a), cy + r * math.sin(a)

    # ---- SVG ----
    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system,BlinkMacSystemFont,&quot;Helvetica Neue&quot;,&quot;Hiragino Sans&quot;,&quot;Yu Gothic&quot;,sans-serif">'
    )
    svg.append('<style>')
    svg.append('text { font-size: 11px; }')
    svg.append('.bg { fill: #fbfaf6; }')
    svg.append('.title { font-size: 17px; font-weight: 700; fill: #1a1a1a; }')
    svg.append('.subtitle { font-size: 11.5px; fill: #555; }')
    svg.append('.axis-line { stroke: #c8c4ba; stroke-width: 0.7; }')
    svg.append('.ring { fill: none; stroke: #d8d3c4; stroke-width: 0.7; stroke-dasharray: 2 3; }')
    svg.append('.axis-label-ja { font-size: 9.5px; fill: #2a2a2a; font-weight: 500; }')
    svg.append('.axis-label-meta { font-size: 8.5px; fill: #777; font-family: ui-monospace,SFMono-Regular,Menlo,monospace; }')
    svg.append('.ring-label { font-size: 8.5px; fill: #999; font-family: ui-monospace,SFMono-Regular,Menlo,monospace; }')
    svg.append('.legend-text { font-size: 11px; fill: #2a2a2a; }')
    svg.append('.legend-meta { font-size: 9.5px; fill: #666; }')
    svg.append('.frame-label { font-size: 10.5px; font-weight: 600; fill: #6a604c; letter-spacing: 0.05em; }')
    svg.append('@media (prefers-color-scheme: dark) {')
    svg.append('  .bg { fill: #14161a; }')
    svg.append('  .title { fill: #ececec; }')
    svg.append('  .subtitle { fill: #b0b0b0; }')
    svg.append('  .axis-line { stroke: #44474e; }')
    svg.append('  .ring { stroke: #3a3d44; }')
    svg.append('  .axis-label-ja { fill: #e0e0e0; }')
    svg.append('  .axis-label-meta { fill: #9a9a9a; }')
    svg.append('  .ring-label { fill: #888; }')
    svg.append('  .legend-text { fill: #e0e0e0; }')
    svg.append('  .legend-meta { fill: #aaa; }')
    svg.append('  .frame-label { fill: #b8a98e; }')
    svg.append('}')
    svg.append('</style>')

    svg.append(f'<rect class="bg" width="{W}" height="{H}"/>')

    # Title
    svg.append(f'<text class="title" x="{W/2:.1f}" y="38" text-anchor="middle">機能ベクトル レーダーチャート</text>')
    svg.append(
        f'<text class="subtitle" x="{W/2:.1f}" y="58" text-anchor="middle">'
        f'25 機能 (Miller 生命系 20 + Beer VSM 5) × 各 era 代表 6 組織 / 値=注釈 confidence (0–1)'
        f'</text>'
    )

    # Concentric rings
    for r in rings:
        rr = radius * r
        svg.append(f'<circle class="ring" cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}"/>')
        # Ring labels at 12 o'clock direction
        svg.append(
            f'<text class="ring-label" x="{cx+3:.1f}" y="{cy - rr - 2:.1f}">{r:.2f}</text>'
        )

    # Frame separator: arc between Miller (axes 0..19) and VSM (axes 20..24)
    # Drawn as a slight halo highlighting VSM segment.
    miller_count = sum(1 for f in funcs if f["fw"] == "miller_living_systems")
    vsm_count = n_axes - miller_count
    # Draw subtle wedge backdrop for VSM segment
    a_start = angle_for(miller_count) - math.pi / n_axes
    a_end = angle_for(n_axes) - math.pi / n_axes
    arc_r = radius + 38
    inner_r = radius * 0.05
    p_x1 = cx + inner_r * math.cos(a_start); p_y1 = cy + inner_r * math.sin(a_start)
    p_x2 = cx + arc_r * math.cos(a_start);   p_y2 = cy + arc_r * math.sin(a_start)
    p_x3 = cx + arc_r * math.cos(a_end);     p_y3 = cy + arc_r * math.sin(a_end)
    p_x4 = cx + inner_r * math.cos(a_end);   p_y4 = cy + inner_r * math.sin(a_end)
    large_arc = 1 if (a_end - a_start) > math.pi else 0
    wedge = (
        f'M {p_x1:.1f} {p_y1:.1f} '
        f'L {p_x2:.1f} {p_y2:.1f} '
        f'A {arc_r:.1f} {arc_r:.1f} 0 {large_arc} 1 {p_x3:.1f} {p_y3:.1f} '
        f'L {p_x4:.1f} {p_y4:.1f} '
        f'A {inner_r:.1f} {inner_r:.1f} 0 {large_arc} 0 {p_x1:.1f} {p_y1:.1f} Z'
    )
    svg.append(f'<path d="{wedge}" fill="#d2c8b0" opacity="0.18"/>')

    # Axes lines
    for i, f in enumerate(funcs):
        x, y = axis_xy(i, 1.0)
        svg.append(
            f'<line class="axis-line" x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}"/>'
        )

    # Axis labels (positioned just outside the outer ring)
    for i, f in enumerate(funcs):
        a = angle_for(i)
        lr = radius + 14
        lx = cx + lr * math.cos(a)
        ly = cy + lr * math.sin(a)
        # Anchor based on side
        cosv = math.cos(a)
        if abs(cosv) < 0.2:
            anchor = "middle"
        elif cosv > 0:
            anchor = "start"
        else:
            anchor = "end"
        # Two-line label: name_ja + identifier
        if f["fw"] == "miller_living_systems":
            ident = f'M{f["mno"]:02d}'
        else:
            ident = f'V{f["vsm"]}'
        # Slight rotation: keep labels horizontal for readability
        svg.append(
            f'<text class="axis-label-ja" x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">'
            f'{html.escape(f["ja"])}</text>'
        )
        svg.append(
            f'<text class="axis-label-meta" x="{lx:.1f}" y="{ly+11:.1f}" text-anchor="{anchor}">'
            f'{ident}</text>'
        )

    # Frame labels (Miller / VSM) at outer arcs
    # Miller mid angle
    m_mid = (angle_for(0) + angle_for(miller_count - 1)) / 2
    mx = cx + (radius + 70) * math.cos(m_mid)
    my = cy + (radius + 70) * math.sin(m_mid)
    svg.append(f'<text class="frame-label" x="{mx:.1f}" y="{my:.1f}" text-anchor="middle">MILLER (生命系 20 サブシステム)</text>')
    v_mid = (angle_for(miller_count) + angle_for(n_axes - 1)) / 2
    vx = cx + (radius + 70) * math.cos(v_mid)
    vy = cy + (radius + 70) * math.sin(v_mid)
    svg.append(f'<text class="frame-label" x="{vx:.1f}" y="{vy:.1f}" text-anchor="middle">BEER VSM (S1–S5)</text>')

    # Polygons for each representative
    for oid, label, era, col in REPRESENTATIVES:
        pts = []
        for i, f in enumerate(funcs):
            v = values[oid][f["id"]]
            x, y = axis_xy(i, v)
            pts.append(f'{x:.1f},{y:.1f}')
        poly = " ".join(pts)
        svg.append(
            f'<polygon points="{poly}" fill="{col}" fill-opacity="0.18" '
            f'stroke="{col}" stroke-width="1.6" stroke-opacity="0.9" stroke-linejoin="round"/>'
        )
        # Vertex dots only where v > 0
        for i, f in enumerate(funcs):
            v = values[oid][f["id"]]
            if v > 0:
                x, y = axis_xy(i, v)
                svg.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}" '
                    f'stroke="#fff" stroke-width="0.8" stroke-opacity="0.7">'
                    f'<title>{html.escape(label)} / {html.escape(f["ja"])} ({f["en"]}) = {v:.2f}</title>'
                    f'</circle>'
                )

    # ---- Legend ----
    leg_x = 60
    leg_y = H - 180
    svg.append(f'<text class="frame-label" x="{leg_x}" y="{leg_y - 14}">代表組織 (era 順)</text>')
    for i, (oid, label, era, col) in enumerate(REPRESENTATIVES):
        ly = leg_y + i * 24
        # color swatch
        svg.append(
            f'<rect x="{leg_x}" y="{ly-10}" width="22" height="12" rx="2" ry="2" '
            f'fill="{col}" fill-opacity="0.5" stroke="{col}" stroke-width="1.4"/>'
        )
        # count of nonzero functions
        nz = sum(1 for f in funcs if values[oid][f["id"]] > 0)
        svg.append(
            f'<text class="legend-text" x="{leg_x + 30}" y="{ly}">{html.escape(label)}</text>'
        )
        svg.append(
            f'<text class="legend-meta" x="{leg_x + 30 + len(label)*12 + 30}" y="{ly}">'
            f'{html.escape(era)} / 機能={nz}</text>'
        )

    svg.append('</svg>')
    OUT.write_text("\n".join(svg), encoding="utf-8")

    # ---- Pairwise distance for reporting ----
    def vec(oid):
        return [values[oid][f["id"]] for f in funcs]

    def dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    print(f"wrote {OUT}")
    print(f"axes: {n_axes} (miller={miller_count}, vsm={vsm_count})")
    print(f"file size: {OUT.stat().st_size} bytes")
    print()
    print("Pairwise Euclidean distances on 25-D function vectors:")
    pairs = []
    for i in range(len(REPRESENTATIVES)):
        for j in range(i + 1, len(REPRESENTATIVES)):
            a_oid, a_lab, _, _ = REPRESENTATIVES[i]
            b_oid, b_lab, _, _ = REPRESENTATIVES[j]
            d = dist(vec(a_oid), vec(b_oid))
            pairs.append((d, a_lab, b_lab))
    pairs.sort(reverse=True)
    for d, a, b in pairs:
        print(f"  {d:.3f}  {a:<14} <-> {b}")
    conn.close()


if __name__ == "__main__":
    main()
