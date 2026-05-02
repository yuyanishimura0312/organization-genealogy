#!/usr/bin/env python3
"""系譜ネットワークの統計分析

完全注釈ケース (18) を対象に:
- 次数分布 (in / out / total degree)
- relation_type 分布
- 連結成分
- 中心性 (degree centrality)
- 時代 × タイプのクロスタブ
"""
import json
import sqlite3
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get fully annotated nodes
    rows = cur.execute("""
        SELECT o.organization_id, o.canonical_name, o.start_date, o.status
        FROM organization o
        WHERE EXISTS (SELECT 1 FROM function_record fr WHERE fr.organization_id=o.organization_id)
    """).fetchall()
    nodes = {oid: {"name": name, "start": start, "status": status}
             for oid, name, start, status in rows}
    print(f"=== Fully annotated nodes: {len(nodes)} ===\n")

    # Get edges among them
    rels = cur.execute("""
        SELECT source_organization_id, target_organization_id, relation_type, confidence, strength
        FROM relation
    """).fetchall()
    edges = [(s, t, rt, c, st) for s, t, rt, c, st in rels if s in nodes and t in nodes]
    print(f"=== Edges among annotated: {len(edges)} ===\n")

    # In / out / total degree
    in_deg = Counter()
    out_deg = Counter()
    for s, t, rt, c, st in edges:
        out_deg[s] += 1
        in_deg[t] += 1

    print("=== Degree centrality (top 10 by total) ===")
    total = [(oid, in_deg[oid] + out_deg[oid], in_deg[oid], out_deg[oid]) for oid in nodes]
    total.sort(key=lambda x: -x[1])
    print(f"{'name':40s}  total  in  out")
    for oid, t, i, o in total[:10]:
        print(f"  {nodes[oid]['name'][:38]:40s}  {t:5d}  {i:3d}  {o:3d}")

    # Relation type distribution
    print("\n=== Relation type distribution ===")
    type_count = Counter(e[2] for e in edges)
    for t, c in type_count.most_common():
        print(f"  {t:30s}  {c}")

    # Connected components (undirected)
    parent = {oid: oid for oid in nodes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    for s, t, *_ in edges:
        union(s, t)
    comps = defaultdict(list)
    for oid in nodes:
        comps[find(oid)].append(oid)
    print(f"\n=== Connected components (undirected): {len(comps)} ===")
    for i, (root, members) in enumerate(sorted(comps.items(), key=lambda x: -len(x[1]))):
        names = sorted([nodes[m]["name"][:30] for m in members], key=lambda n: n)
        print(f"  Component {i+1} ({len(members)} nodes):")
        for n in names:
            print(f"    - {n}")

    # Era × relation_type crosstab
    def era(start_date):
        if not start_date:
            return "extant"
        y = int(start_date[:4])
        if y < 500: return "ancient"
        if y < 1500: return "medieval"
        if y < 1800: return "early_modern"
        if y < 1945: return "modern"
        if y < 2000: return "postwar"
        return "contemporary"

    print("\n=== Era × relation_type crosstab (source era) ===")
    cross = defaultdict(Counter)
    for s, t, rt, *_ in edges:
        e_src = era(nodes[s]["start"])
        cross[e_src][rt] += 1
    eras = ["medieval","early_modern","modern","postwar","contemporary","extant"]
    rtypes = sorted(set(rt for _, _, rt, *_ in edges))
    print(f"{'era':14s}  " + "  ".join(f"{rt[:14]:14s}" for rt in rtypes))
    for e in eras:
        if e not in cross: continue
        line = f"{e:14s}  "
        for rt in rtypes:
            line += f"{cross[e].get(rt, 0):>14d}  "
        print(line)

    # Status of annotated nodes
    print("\n=== Status distribution of annotated nodes ===")
    sc = Counter(n["status"] for n in nodes.values())
    for s, c in sc.most_common():
        print(f"  {s:15s}  {c}")

    # Era distribution
    print("\n=== Era distribution of annotated nodes ===")
    ec = Counter(era(n["start"]) for n in nodes.values())
    for e in eras:
        if e in ec:
            print(f"  {e:15s}  {ec[e]}")

    # Save as JSON for dashboard
    out = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_relation_type": dict(type_count),
        "components": [
            {"size": len(m), "members": [nodes[oid]["name"] for oid in m]}
            for _, m in sorted(comps.items(), key=lambda x: -len(x[1]))
        ],
        "top_degree": [
            {"name": nodes[oid]["name"], "total": t, "in": i, "out": o}
            for oid, t, i, o in total[:10]
        ],
        "era_distribution": dict(ec),
        "status_distribution": dict(sc),
    }
    out_path = ROOT / "data" / "network_stats.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
