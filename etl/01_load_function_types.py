#!/usr/bin/env python3
"""Load codex7 function taxonomy (25 Miller + VSM functions) into function_type table."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
TAXONOMY = ROOT / "research" / "codex7_function_taxonomy.json"


def main():
    data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    funcs = data["functions"]
    assert len(funcs) == 25, f"expected 25 functions, got {len(funcs)}"

    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    inserted = 0
    for f in funcs:
        cur.execute(
            """INSERT INTO function_type
               (function_type_id, name_ja, name_en, source_framework,
                miller_subsystem_no, vsm_system_no, parent_function_type_id,
                definition, observable_indicators, era_examples)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(function_type_id) DO UPDATE SET
                 name_ja=excluded.name_ja,
                 name_en=excluded.name_en,
                 source_framework=excluded.source_framework,
                 miller_subsystem_no=excluded.miller_subsystem_no,
                 vsm_system_no=excluded.vsm_system_no,
                 definition=excluded.definition,
                 observable_indicators=excluded.observable_indicators,
                 era_examples=excluded.era_examples,
                 updated_at=CURRENT_TIMESTAMP""",
            (
                f["function_id"],
                f["name_ja"],
                f["name_en"],
                f["source_framework"],
                f.get("miller_number"),
                f.get("vsm_number"),
                None,  # parent — codex7 uses synthetic parent IDs not in this table
                f["definition"],
                json.dumps(f.get("indicators", []), ensure_ascii=False),
                json.dumps(f.get("era_examples", {}), ensure_ascii=False),
            ),
        )
        inserted += 1

    conn.commit()
    print(f"loaded {inserted} function_type rows")

    cur.execute("SELECT COUNT(*) FROM function_type")
    print(f"function_type total: {cur.fetchone()[0]}")
    cur.execute("SELECT function_type_id, name_ja FROM function_type ORDER BY miller_subsystem_no NULLS LAST, vsm_system_no")
    for row in cur.fetchall():
        print(f"  {row[0]:40s}  {row[1]}")
    conn.close()


if __name__ == "__main__":
    sys.exit(main() or 0)
