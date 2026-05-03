#!/usr/bin/env python3
"""Migrate data/og.db rows into PostgreSQL.

This skeleton keeps imports safe in environments without psycopg2. Use
--dry-run to inspect SQLite extraction without opening a PostgreSQL connection.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import struct
from pathlib import Path
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import DateRange, Json, execute_values
except ImportError:
    psycopg2 = None
    DateRange = None
    Json = None
    execute_values = None

try:
    from pgvector.psycopg2 import register_vector
except ImportError:
    register_vector = None

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "data" / "og.db"

TABLE_ORDER = [
    "source",
    "claim",
    "organization_form",
    "organization",
    "organization_form_assignment",
    "function_type",
    "activity",
    "function_record",
    "impact_record",
    "relation",
    "event",
    "event_organization",
    "event_relation",
    "dormancy_record",
    "organization_temporal_facet",
]

JSON_COLUMNS = {
    "source": {"authors", "locator"},
    "claim": {"claim_value"},
    "organization_form": {"criteria"},
    "organization": {"alternate_names", "geo_scope", "attributes", "external_ids"},
    "function_type": {"observable_indicators", "era_examples"},
    "activity": {"inputs", "outputs", "scale"},
    "function_record": {"mechanism", "beneficiaries", "dependency"},
    "impact_record": {"metric_value", "affected_scope"},
    "relation": {"relation_attributes"},
    "event": {"participants", "causes", "outcomes", "location"},
    "event_relation": {"before_value", "after_value"},
    "organization_temporal_facet": {"facet_value"},
}

BOOL_COLUMNS = {
    "organization_form_assignment": {"is_primary"},
}

VECTOR_COLUMNS = {
    "organization": {"embedding"},
}

RANGE_COLUMNS = {
    "organization_form": {
        "valid_period": ("valid_period_from", "valid_period_to"),
    },
}

TARGET_TABLE = {
    # Older PostgreSQL draft DDL used "function"; the live SQLite table is
    # function_record, and the migration target should use the same name.
    "function_record": "function_record",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-db", type=Path, default=SQLITE_DB)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=500)
    return parser.parse_args()


def connect_sqlite(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def connect_postgres() -> Any:
    pg_url = os.environ.get("PG_URL")
    if not pg_url:
        raise SystemExit("PG_URL is required unless --dry-run is used")
    if psycopg2 is None:
        raise SystemExit("psycopg2 v2 is required for PostgreSQL migration")
    conn = psycopg2.connect(pg_url)
    if register_vector is not None:
        register_vector(conn)
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row["name"] for row in rows]


def parse_json(value: Any) -> Any:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return value
    return json.loads(value)


def convert_vector(value: Any) -> list[float] | None:
    if value is None:
        return None
    if isinstance(value, str):
        parsed = json.loads(value)
        if len(parsed) != 384:
            raise ValueError(f"embedding has {len(parsed)} dimensions, expected 384")
        return [float(item) for item in parsed]
    if not isinstance(value, bytes):
        raise TypeError(f"unsupported embedding type: {type(value)!r}")
    if len(value) != 384 * 4:
        raise ValueError(f"embedding blob has {len(value)} bytes, expected 1536")
    return list(struct.unpack("<384f", value))


def convert_range(lower: Any, upper: Any) -> Any:
    if lower is None and upper is None:
        return None
    if DateRange is None:
        return (lower, upper, "[)")
    return DateRange(lower, upper, "[)")


def convert_value(table: str, column: str, value: Any) -> Any:
    if column in JSON_COLUMNS.get(table, set()):
        parsed = parse_json(value)
        return Json(parsed) if Json is not None and parsed is not None else parsed
    if column in BOOL_COLUMNS.get(table, set()):
        return None if value is None else bool(value)
    if column in VECTOR_COLUMNS.get(table, set()):
        return convert_vector(value)
    return value


def build_row(table: str, row: sqlite3.Row, sqlite_columns: list[str]) -> tuple[list[str], list[Any]]:
    output: dict[str, Any] = {}
    skipped = set()

    for target_col, (lower_col, upper_col) in RANGE_COLUMNS.get(table, {}).items():
        output[target_col] = convert_range(row[lower_col], row[upper_col])
        skipped.update({lower_col, upper_col})

    for column in sqlite_columns:
        if column in skipped:
            continue
        output[column] = convert_value(table, column, row[column])

    return list(output.keys()), list(output.values())


def iter_rows(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return conn.execute(f"SELECT * FROM {table}").fetchall()


def insert_rows(pg_conn: Any, table: str, columns: list[str], rows: list[list[Any]]) -> None:
    if not rows:
        return
    target = TARGET_TABLE.get(table, table)
    column_sql = ", ".join(columns)
    template = "(" + ", ".join(["%s"] * len(columns)) + ")"
    sql = f"INSERT INTO {target} ({column_sql}) VALUES %s ON CONFLICT DO NOTHING"
    with pg_conn.cursor() as cur:
        execute_values(cur, sql, rows, template=template)


def migrate_table(
    sqlite_conn: sqlite3.Connection,
    pg_conn: Any | None,
    table: str,
    dry_run: bool,
    batch_size: int,
) -> int:
    sqlite_columns = table_columns(sqlite_conn, table)
    rows = iter_rows(sqlite_conn, table)
    if dry_run:
        return len(rows)

    pending: list[list[Any]] = []
    output_columns: list[str] | None = None
    for row in rows:
        columns, values = build_row(table, row, sqlite_columns)
        if output_columns is None:
            output_columns = columns
        pending.append(values)
        if len(pending) >= batch_size:
            insert_rows(pg_conn, table, output_columns, pending)
            pending = []
    if pending and output_columns is not None:
        insert_rows(pg_conn, table, output_columns, pending)
    return len(rows)


def main() -> None:
    args = parse_args()
    sqlite_conn = connect_sqlite(args.sqlite_db)
    pg_conn = None if args.dry_run else connect_postgres()

    try:
        total = 0
        for table in TABLE_ORDER:
            count = migrate_table(sqlite_conn, pg_conn, table, args.dry_run, args.batch_size)
            total += count
            if not args.dry_run:
                pg_conn.commit()
            print(f"{table}: {count} rows")
        print(f"total: {total} rows")
    except Exception:
        if pg_conn is not None:
            pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        if pg_conn is not None:
            pg_conn.close()


if __name__ == "__main__":
    main()
