#!/usr/bin/env python3
"""18 ケース ライフサイクルタイムライン SVG 生成

横軸: BC3000 〜 2030 (古代圧縮、対数ライク piecewise)
縦軸: 18 ケースを start_date 順
各ケースを bar (start→end or 現在) で表示、status で色分け
event を bar 上に dot として配置 (founding/dissolution/reorganization/revival/schism/crisis/...)
vsr_label (variation/selection/retention/struggle) で dot 色を変える
横軸に era 帯。ダーク/ライトテーマ対応。
"""
from __future__ import annotations

import math
import sqlite3
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT = ROOT / "data" / "lifecycle_timeline.svg"

# Layout
W, H = 1400, 820
PAD_L, PAD_R, PAD_T, PAD_B = 230, 60, 80, 70

YEAR_MIN = -3000
YEAR_MAX = 2030
NOW_YEAR = 2026

# Hadza は完新世以来の連続性を持つ最古ケースとして BC3000 起点とする (BC3000 を画面左端に表示する代理値)
HADZA_FALLBACK_START = -3000


def parse_year(date_str):
    """SQLite date 文字列から西暦年 (BC は負) を返す。"""
    if not date_str:
        return None
    s = date_str.strip()
    if not s or s.startswith("9999"):
        return None
    # Negative years like "-3000-01-01" or BC encoded as leading minus
    neg = False
    if s.startswith("-"):
        neg = True
        s = s[1:]
    head = s.split("-")[0]
    try:
        y = int(head)
    except Exception:
        return None
    return -y if neg else y


def year_to_x(y):
    """Piecewise log-ish mapping.

    BC3000..0  -> 0%..18%   (deep antiquity, heavily compressed)
    0..1000    -> 18%..30%  (early antiquity → early medieval)
    1000..1500 -> 30%..45%  (medieval)
    1500..1800 -> 45%..62%  (early modern)
    1800..1945 -> 62%..78%  (modern)
    1945..2030 -> 78%..100% (contemporary)
    """
    y = max(YEAR_MIN, min(YEAR_MAX, y))
    segments = [
        (-3000, 0,    0.00, 0.18),
        (0,     1000, 0.18, 0.30),
        (1000,  1500, 0.30, 0.45),
        (1500,  1800, 0.45, 0.62),
        (1800,  1945, 0.62, 0.78),
        (1945,  2030, 0.78, 1.00),
    ]
    for ys, ye, fs, fe in segments:
        if ys <= y <= ye:
            frac = fs + (fe - fs) * (y - ys) / (ye - ys)
            break
    else:
        frac = 1.0
    inner_w = W - PAD_L - PAD_R
    return PAD_L + frac * inner_w


def fmt_year(y):
    if y < 0:
        return f"BC{abs(y)}"
    return f"{y}"


def short_name(name):
    s = name
    if "(" in s:
        s = s.split("(")[0].strip()
    if "/" in s:
        s = s.split("/")[0].strip()
    return s


def main():
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT organization_id, canonical_name, start_date, end_date, status
        FROM organization
        WHERE EXISTS (SELECT 1 FROM function_record fr WHERE fr.organization_id = organization.organization_id)
        """
    ).fetchall()

    cases = []
    for oid, name, sd, ed, status in rows:
        sy = parse_year(sd)
        ey = parse_year(ed)
        if sy is None:
            sy = HADZA_FALLBACK_START
        cases.append({
            "id": oid, "name": name, "start": sy, "end": ey, "status": status,
            "events": [],
        })

    cases.sort(key=lambda c: c["start"])

    # Fetch events
    ev_rows = cur.execute(
        """
        SELECT e.event_id, e.event_type, e.event_date, e.vsr_label, e.description, eo.organization_id, eo.role
        FROM event e
        JOIN event_organization eo ON eo.event_id = e.event_id
        ORDER BY e.event_date
        """
    ).fetchall()

    by_oid = {c["id"]: c for c in cases}
    for eid, etype, edate, vsr, desc, oid, role in ev_rows:
        if oid not in by_oid:
            continue
        ey = parse_year(edate)
        if ey is None:
            continue
        by_oid[oid]["events"].append({
            "type": etype, "year": ey, "vsr": vsr, "desc": desc, "role": role,
        })

    # Layout
    n = len(cases)
    avail_h = H - PAD_T - PAD_B
    row_h = avail_h / n
    for i, c in enumerate(cases):
        c["y"] = PAD_T + (i + 0.5) * row_h

    # Color scheme (works on both light and dark via CSS overrides where needed)
    status_color = {
        "active":      "#3b8f5f",
        "extinct":     "#b07256",
        "transformed": "#c5a050",
        "dormant":     "#7f7f7f",
        "merged":      "#5a8a4a",
        "split":       "#8a70a0",
        "unknown":     "#888888",
    }

    vsr_color = {
        "variation":  "#4aa3df",   # blue   — 創発・新規性
        "selection":  "#d9534f",   # red    — 淘汰
        "retention":  "#5cb85c",   # green  — 維持・再生産
        "struggle":   "#f0ad4e",   # orange — 闘争
        None:         "#aaaaaa",
    }

    # Era bands
    eras = [
        (-3000, -500, "先史・古代初期", "#f0ece0"),
        (-500,   500, "古代",           "#ebe5d3"),
        (500,   1500, "中世",           "#f5efe8"),
        (1500,  1800, "近世",           "#ebe1d6"),
        (1800,  1945, "近代",           "#f0e8d8"),
        (1945,  2030, "現代",           "#e8e8e0"),
    ]

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system,BlinkMacSystemFont,&quot;Helvetica Neue&quot;,&quot;Hiragino Sans&quot;,&quot;Yu Gothic&quot;,sans-serif">'
    )
    svg.append('<style>')
    svg.append('text { font-size: 11px; }')
    svg.append('.bg { fill: #fbfaf6; }')
    svg.append('.title { font-size: 15px; font-weight: 700; fill: #1a1a1a; }')
    svg.append('.subtitle { font-size: 11px; fill: #555; }')
    svg.append('.case-label { font-size: 11px; fill: #1a1a1a; }')
    svg.append('.case-meta { font-size: 9.5px; fill: #6b6b6b; font-family: ui-monospace,SFMono-Regular,Menlo,monospace; }')
    svg.append('.year-tick { font-size: 9.5px; fill: #666; font-family: ui-monospace,SFMono-Regular,Menlo,monospace; }')
    svg.append('.era-label { font-size: 10.5px; fill: #8a7d6a; }')
    svg.append('.legend-text { font-size: 10px; fill: #444; }')
    svg.append('.legend-head { font-size: 10.5px; font-weight: 600; fill: #1a1a1a; }')
    svg.append('.row-stripe { fill: #00000005; }')
    svg.append('@media (prefers-color-scheme: dark) {')
    svg.append('  .bg { fill: #14161a; }')
    svg.append('  .title { fill: #ececec; }')
    svg.append('  .subtitle { fill: #b0b0b0; }')
    svg.append('  .case-label { fill: #e6e6e6; }')
    svg.append('  .case-meta { fill: #a8a8a8; }')
    svg.append('  .year-tick { fill: #aaa; }')
    svg.append('  .era-label { fill: #b8a98e; }')
    svg.append('  .legend-text { fill: #c8c8c8; }')
    svg.append('  .legend-head { fill: #ececec; }')
    svg.append('  .row-stripe { fill: #ffffff09; }')
    svg.append('  .era-band { opacity: 0.18 !important; }')
    svg.append('  .axis-line { stroke: #555 !important; }')
    svg.append('  .grid-line { stroke: #2c2f36 !important; }')
    svg.append('}')
    svg.append('</style>')

    svg.append(f'<rect class="bg" width="{W}" height="{H}"/>')

    # Title
    svg.append(f'<text class="title" x="{PAD_L}" y="28">18 組織ライフサイクル・タイムライン (BC3000 — 2030)</text>')
    svg.append(f'<text class="subtitle" x="{PAD_L}" y="46">横軸: 年代 (古代圧縮 piecewise) / 縦軸: start_date 順 / バー色=status / dot 色=VSR ラベル</text>')

    # Era bands
    for ys, ye, label, col in eras:
        xs = year_to_x(ys); xe = year_to_x(ye)
        svg.append(
            f'<rect class="era-band" x="{xs:.1f}" y="{PAD_T-12}" width="{xe-xs:.1f}" '
            f'height="{H-PAD_T-PAD_B+12}" fill="{col}" opacity="0.55"/>'
        )
        svg.append(
            f'<text class="era-label" x="{(xs+xe)/2:.1f}" y="{PAD_T-16}" text-anchor="middle">{label}</text>'
        )

    # Row stripes (alternating) + horizontal guide
    for i, c in enumerate(cases):
        if i % 2 == 0:
            svg.append(
                f'<rect class="row-stripe" x="{PAD_L}" y="{PAD_T + i*row_h:.1f}" '
                f'width="{W-PAD_L-PAD_R}" height="{row_h:.1f}"/>'
            )

    # Vertical year grid + ticks
    axis_y = H - PAD_B + 14
    svg.append(
        f'<line class="axis-line" x1="{PAD_L}" y1="{axis_y}" x2="{W-PAD_R}" y2="{axis_y}" '
        f'stroke="#999" stroke-width="1"/>'
    )
    ticks = [-3000, -1000, -500, 0, 500, 1000, 1500, 1700, 1900, 1950, 2000, 2026]
    for ty in ticks:
        x = year_to_x(ty)
        svg.append(
            f'<line class="grid-line" x1="{x:.1f}" y1="{PAD_T-12}" x2="{x:.1f}" y2="{H-PAD_B}" '
            f'stroke="#e5e1d6" stroke-width="0.7" stroke-dasharray="2 4"/>'
        )
        svg.append(
            f'<line class="axis-line" x1="{x:.1f}" y1="{axis_y-4}" x2="{x:.1f}" y2="{axis_y+4}" '
            f'stroke="#999" stroke-width="1"/>'
        )
        svg.append(
            f'<text class="year-tick" x="{x:.1f}" y="{axis_y+16}" text-anchor="middle">{fmt_year(ty)}</text>'
        )

    # Bars + events
    for c in cases:
        y = c["y"]
        x_start = year_to_x(c["start"])
        if c["end"] is None:
            x_end = year_to_x(NOW_YEAR)
            ongoing = True
        else:
            x_end = year_to_x(c["end"])
            ongoing = False
        col = status_color.get(c["status"], "#888")

        bar_h = 9
        # Lifespan bar (rounded)
        svg.append(
            f'<rect x="{x_start:.1f}" y="{y - bar_h/2:.1f}" '
            f'width="{max(2.0, x_end-x_start):.1f}" height="{bar_h}" '
            f'rx="3" ry="3" fill="{col}" opacity="0.78" stroke="{col}" stroke-width="0.5"/>'
        )
        # Ongoing arrow
        if ongoing:
            svg.append(
                f'<polygon points="{x_end:.1f},{y - bar_h/2:.1f} '
                f'{x_end+8:.1f},{y:.1f} {x_end:.1f},{y + bar_h/2:.1f}" '
                f'fill="{col}" opacity="0.85"/>'
            )

        # Hadza heritage hint (dotted bar continuing left if start < BC2000 fallback)
        if c["id"] == "dba1923c55fe480795e0b646ba72df5e":
            svg.append(
                f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{x_start:.1f}" y2="{y:.1f}" '
                f'stroke="{col}" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.45"/>'
            )

        # Left labels (case name + dates)
        nm = short_name(c["name"])
        svg.append(
            f'<text class="case-label" x="{PAD_L - 12}" y="{y+1:.1f}" text-anchor="end">'
            f'{html.escape(nm)}</text>'
        )
        if c["end"]:
            meta = f'{fmt_year(c["start"])}–{fmt_year(c["end"])}'
        else:
            meta = f'{fmt_year(c["start"])}–'
        svg.append(
            f'<text class="case-meta" x="{PAD_L - 12}" y="{y+13:.1f}" text-anchor="end">{meta}</text>'
        )

        # Events as dots
        for ev in c["events"]:
            ex = year_to_x(ev["year"])
            dot_col = vsr_color.get(ev["vsr"], "#aaaaaa")
            etype = ev["type"]
            # Symbol per event_type
            if etype == "founding":
                # filled diamond
                svg.append(
                    f'<polygon points="{ex:.1f},{y-7:.1f} {ex+5:.1f},{y:.1f} '
                    f'{ex:.1f},{y+7:.1f} {ex-5:.1f},{y:.1f}" fill="{dot_col}" '
                    f'stroke="#1a1a1a" stroke-width="0.5"/>'
                )
            elif etype == "dissolution":
                # X cross
                svg.append(
                    f'<line x1="{ex-5:.1f}" y1="{y-5:.1f}" x2="{ex+5:.1f}" y2="{y+5:.1f}" '
                    f'stroke="{dot_col}" stroke-width="2.2"/>'
                )
                svg.append(
                    f'<line x1="{ex-5:.1f}" y1="{y+5:.1f}" x2="{ex+5:.1f}" y2="{y-5:.1f}" '
                    f'stroke="{dot_col}" stroke-width="2.2"/>'
                )
            elif etype in ("reorganization", "reform", "governance_change"):
                # square
                svg.append(
                    f'<rect x="{ex-4.5:.1f}" y="{y-4.5:.1f}" width="9" height="9" '
                    f'fill="{dot_col}" stroke="#1a1a1a" stroke-width="0.5"/>'
                )
            elif etype == "revival":
                # upward triangle
                svg.append(
                    f'<polygon points="{ex:.1f},{y-6:.1f} {ex+5.5:.1f},{y+5:.1f} '
                    f'{ex-5.5:.1f},{y+5:.1f}" fill="{dot_col}" stroke="#1a1a1a" stroke-width="0.5"/>'
                )
            elif etype == "split":
                # downward triangle (schism)
                svg.append(
                    f'<polygon points="{ex-5.5:.1f},{y-5:.1f} {ex+5.5:.1f},{y-5:.1f} '
                    f'{ex:.1f},{y+6:.1f}" fill="{dot_col}" stroke="#1a1a1a" stroke-width="0.5"/>'
                )
            elif etype == "crisis":
                # starburst as small circle with ring
                svg.append(
                    f'<circle cx="{ex:.1f}" cy="{y:.1f}" r="6" fill="none" '
                    f'stroke="{dot_col}" stroke-width="1.4" stroke-dasharray="2 1.5"/>'
                )
                svg.append(
                    f'<circle cx="{ex:.1f}" cy="{y:.1f}" r="2" fill="{dot_col}"/>'
                )
            elif etype == "merger":
                # two overlapping circles
                svg.append(
                    f'<circle cx="{ex-2.5:.1f}" cy="{y:.1f}" r="4" fill="{dot_col}" '
                    f'opacity="0.85" stroke="#1a1a1a" stroke-width="0.4"/>'
                )
                svg.append(
                    f'<circle cx="{ex+2.5:.1f}" cy="{y:.1f}" r="4" fill="{dot_col}" '
                    f'opacity="0.85" stroke="#1a1a1a" stroke-width="0.4"/>'
                )
            else:
                # default circle
                svg.append(
                    f'<circle cx="{ex:.1f}" cy="{y:.1f}" r="4" fill="{dot_col}" '
                    f'stroke="#1a1a1a" stroke-width="0.4"/>'
                )
            # Tooltip
            tt = f'{fmt_year(ev["year"])} {etype} [{ev["vsr"] or "-"}] — {ev["desc"] or ""}'
            svg.append(f'<title>{html.escape(tt)}</title>')

    # ---- Legends ----
    # Status legend (bottom-left)
    lx = PAD_L
    ly = H - 30
    svg.append(f'<text class="legend-head" x="{lx}" y="{ly}">バー (status):</text>')
    items = [("active", "active"), ("extinct", "extinct"),
             ("transformed", "transformed"), ("merged", "merged"),
             ("split", "split"), ("unknown", "unknown")]
    cx = lx + 100
    for k, lab in items:
        col = status_color[k]
        svg.append(f'<rect x="{cx}" y="{ly-8}" width="14" height="9" rx="2" ry="2" fill="{col}" opacity="0.78"/>')
        svg.append(f'<text class="legend-text" x="{cx+18}" y="{ly}">{lab}</text>')
        cx += len(lab) * 6 + 38

    # VSR legend (top-right)
    lx2 = W - PAD_R - 380
    ly2 = 28
    svg.append(f'<text class="legend-head" x="{lx2}" y="{ly2}">dot 色 (VSR):</text>')
    cx2 = lx2 + 88
    for k, lab in [("variation", "variation"), ("selection", "selection"),
                   ("retention", "retention"), ("struggle", "struggle")]:
        col = vsr_color[k]
        svg.append(f'<circle cx="{cx2+5}" cy="{ly2-3}" r="5" fill="{col}" stroke="#1a1a1a" stroke-width="0.4"/>')
        svg.append(f'<text class="legend-text" x="{cx2+14}" y="{ly2}">{lab}</text>')
        cx2 += len(lab) * 7 + 22

    # Event-shape legend (top-right second row)
    lx3 = W - PAD_R - 720
    ly3 = 50
    svg.append(f'<text class="legend-head" x="{lx3}" y="{ly3}">dot 形 (event):</text>')
    cx3 = lx3 + 92
    shape_items = [
        ("◆ founding", "diamond"),
        ("× dissolution", "x"),
        ("■ reorg/reform", "square"),
        ("▲ revival", "tri-up"),
        ("▼ split/schism", "tri-down"),
        ("◌ crisis", "ring"),
        ("◎ merger", "double"),
    ]
    for label, _ in shape_items:
        svg.append(f'<text class="legend-text" x="{cx3}" y="{ly3}">{label}</text>')
        cx3 += len(label) * 6.4 + 12

    svg.append('</svg>')
    OUT.write_text("\n".join(svg), encoding="utf-8")

    # Console summary
    print(f"wrote {OUT}")
    print(f"cases: {len(cases)}")
    total_events = sum(len(c["events"]) for c in cases)
    print(f"events plotted: {total_events}")
    print(f"file size: {OUT.stat().st_size} bytes")
    conn.close()


if __name__ == "__main__":
    main()
