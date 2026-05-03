#!/usr/bin/env python3
"""Cluster organizations by 25-function binary vectors."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT = ROOT / "data" / "clustering_results.json"
HEIGHTS = (0.25, 0.50, 0.75)


@dataclass(frozen=True)
class Node:
    id: int
    members: tuple[int, ...]
    height: float
    left: int | None = None
    right: int | None = None


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_vectors(conn: sqlite3.Connection):
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
        SELECT o.organization_id, o.canonical_name
        FROM organization o
        WHERE EXISTS (
          SELECT 1 FROM function_record fr
          WHERE fr.organization_id = o.organization_id
        )
        ORDER BY o.canonical_name, o.organization_id
        """
    ).fetchall()

    rows = conn.execute(
        """
        SELECT o.organization_id, o.canonical_name, ft.function_type_id
        FROM organization o
        JOIN function_record fr ON fr.organization_id = o.organization_id
        JOIN function_type ft ON ft.function_type_id = fr.function_type_id
        WHERE EXISTS (
          SELECT 1 FROM function_record
          WHERE organization_id = o.organization_id
        )
        """
    ).fetchall()

    function_ids = [row["function_type_id"] for row in functions]
    function_index = {function_id: i for i, function_id in enumerate(function_ids)}
    organization_index = {
        row["organization_id"]: i for i, row in enumerate(organizations)
    }
    vectors = [[0 for _ in function_ids] for _ in organizations]

    for row in rows:
        org_i = organization_index[row["organization_id"]]
        fn_i = function_index[row["function_type_id"]]
        vectors[org_i][fn_i] = 1

    return functions, organizations, vectors


def jaccard_distance(a: list[int], b: list[int]) -> float:
    intersection = sum(1 for av, bv in zip(a, b) if av and bv)
    union = sum(1 for av, bv in zip(a, b) if av or bv)
    if union == 0:
        return 0.0
    return 1.0 - intersection / union


def distance_matrix(vectors: list[list[int]]) -> list[list[float]]:
    matrix = []
    for a in vectors:
        matrix.append([round(jaccard_distance(a, b), 6) for b in vectors])
    return matrix


def cluster_distance(
    a: tuple[int, ...],
    b: tuple[int, ...],
    matrix: list[list[float]],
    linkage: str,
) -> float:
    distances = [matrix[i][j] for i in a for j in b]
    if linkage == "single":
        return min(distances)
    if linkage == "complete":
        return max(distances)
    raise ValueError(f"unknown linkage: {linkage}")


def agglomerative(matrix: list[list[float]], linkage: str):
    nodes = {i: Node(i, (i,), 0.0) for i in range(len(matrix))}
    active = {i: nodes[i] for i in range(len(matrix))}
    merges = []
    next_id = len(matrix)

    while len(active) > 1:
        best_key = None
        best_pair = None
        active_ids = sorted(active)
        for pos, left_id in enumerate(active_ids):
            for right_id in active_ids[pos + 1 :]:
                left = active[left_id]
                right = active[right_id]
                distance = cluster_distance(left.members, right.members, matrix, linkage)
                key = (
                    distance,
                    min(left.members),
                    min(right.members),
                    left_id,
                    right_id,
                )
                if best_key is None or key < best_key:
                    best_key = key
                    best_pair = (left_id, right_id, distance)

        if best_pair is None:
            break

        left_id, right_id, height = best_pair
        left = active.pop(left_id)
        right = active.pop(right_id)
        members = tuple(sorted(left.members + right.members))
        node = Node(next_id, members, height, left.id, right.id)
        nodes[next_id] = node
        active[next_id] = node
        merges.append(
            {
                "left": left.id,
                "right": right.id,
                "height": round(height, 6),
                "members": list(members),
            }
        )
        next_id += 1

    root_id = next(iter(active)) if active else None
    return nodes, root_id, merges


def render_ascii(
    nodes: dict[int, Node],
    node_id: int,
    labels: list[str],
    prefix: str = "",
    is_tail: bool = True,
) -> list[str]:
    node = nodes[node_id]
    connector = "`-- " if is_tail else "|-- "
    if node.left is None or node.right is None:
        label = labels[node.members[0]]
        return [f"{prefix}{connector}{label}"]

    line = f"{prefix}{connector}h={node.height:.3f} n={len(node.members)}"
    child_prefix = prefix + ("    " if is_tail else "|   ")
    left_lines = render_ascii(nodes, node.left, labels, child_prefix, False)
    right_lines = render_ascii(nodes, node.right, labels, child_prefix, True)
    return [line] + left_lines + right_lines


def assignments_at_height(
    nodes: dict[int, Node],
    root_id: int,
    height: float,
    organizations: list[sqlite3.Row],
) -> list[dict[str, object]]:
    stack = [root_id]
    clusters = []
    while stack:
        node = nodes[stack.pop()]
        if node.height <= height or node.left is None or node.right is None:
            clusters.append(node)
        else:
            stack.append(node.right)
            stack.append(node.left)

    rows = []
    for cluster_no, node in enumerate(sorted(clusters, key=lambda n: min(n.members)), 1):
        rows.append(
            {
                "cluster_id": cluster_no,
                "height": height,
                "size": len(node.members),
                "members": [
                    {
                        "organization_id": organizations[i]["organization_id"],
                        "canonical_name": organizations[i]["canonical_name"],
                    }
                    for i in node.members
                ],
            }
        )
    return rows


def main() -> None:
    with connect() as conn:
        functions, organizations, vectors = fetch_vectors(conn)

    matrix = distance_matrix(vectors)
    labels = [row["canonical_name"] for row in organizations]
    dendrograms = {}
    cluster_assignments = {}

    for linkage in ("single", "complete"):
        nodes, root_id, merges = agglomerative(matrix, linkage)
        if root_id is None:
            ascii_tree = ""
            assignments = {str(height): [] for height in HEIGHTS}
        else:
            ascii_tree = "\n".join(render_ascii(nodes, root_id, labels))
            assignments = {
                f"{height:.2f}": assignments_at_height(
                    nodes, root_id, height, organizations
                )
                for height in HEIGHTS
            }
        dendrograms[linkage] = {"ascii": ascii_tree, "merges": merges}
        cluster_assignments[linkage] = assignments

    payload = {
        "metadata": {
            "db": str(DB.relative_to(ROOT)),
            "organization_count": len(organizations),
            "function_dimension_count": len(functions),
            "distance": "Jaccard distance on binary function vectors",
            "linkages": ["single", "complete"],
            "assignment_heights": list(HEIGHTS),
        },
        "functions": [
            {
                "function_type_id": row["function_type_id"],
                "name_ja": row["name_ja"],
                "name_en": row["name_en"],
            }
            for row in functions
        ],
        "organizations": [
            {
                "organization_id": row["organization_id"],
                "canonical_name": row["canonical_name"],
                "vector": vectors[i],
                "active_function_count": sum(vectors[i]),
            }
            for i, row in enumerate(organizations)
        ],
        "distance_matrix": {
            "organization_order": [
                row["organization_id"] for row in organizations
            ],
            "values": matrix,
        },
        "dendrograms": dendrograms,
        "cluster_assignments": cluster_assignments,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(
        f"{len(organizations)} organizations x {len(functions)} functions; "
        f"matrix {len(matrix)}x{len(matrix)}"
    )


if __name__ == "__main__":
    main()
