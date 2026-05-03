import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

VALUE_KINDS = {"present", "absent", "partial", "unknown", "inapplicable"}
DATE_PRECISIONS = {
    "exact",
    "year",
    "decade",
    "century",
    "period",
    "before",
    "after",
    "unknown",
}
REDISTRIBUTIONS = {
    "public_redistributable",
    "attribution_required",
    "noncommercial",
    "private",
    "restricted",
}

DATE_PRECISION_COLUMNS = (
    ("organization", "start_date_precision"),
    ("organization", "end_date_precision"),
    ("organization_form_assignment", "valid_from_precision"),
    ("organization_form_assignment", "valid_to_precision"),
    ("activity", "valid_from_precision"),
    ("activity", "valid_to_precision"),
    ("function_record", "valid_from_precision"),
    ("function_record", "valid_to_precision"),
    ("impact_record", "valid_from_precision"),
    ("impact_record", "valid_to_precision"),
    ("relation", "valid_from_precision"),
    ("relation", "valid_to_precision"),
    ("event", "event_date_precision"),
    ("dormancy_record", "start_date_precision"),
    ("dormancy_record", "end_date_precision"),
    ("organization_temporal_facet", "valid_from_precision"),
    ("organization_temporal_facet", "valid_to_precision"),
)


class SchemaIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DB.exists():
            raise unittest.SkipTest(f"database not found: {DB}")
        cls.conn = sqlite3.connect(DB)
        cls.conn.row_factory = sqlite3.Row
        cls.conn.execute("PRAGMA foreign_keys = ON")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def fetch_count(self, sql, params=()):
        return self.conn.execute(sql, params).fetchone()[0]

    def test_fully_annotated_organizations_have_form_assignment(self):
        missing = self.fetch_count(
            """
            SELECT COUNT(*)
            FROM organization o
            WHERE EXISTS (
                SELECT 1 FROM function_record fr
                WHERE fr.organization_id = o.organization_id
            )
              AND NOT EXISTS (
                SELECT 1 FROM organization_form_assignment ofa
                WHERE ofa.organization_id = o.organization_id
            )
            """
        )
        self.assertEqual(missing, 0)

    def test_all_claims_have_existing_source_id(self):
        missing = self.fetch_count(
            "SELECT COUNT(*) FROM claim WHERE source_id IS NULL OR source_id = ''"
        )
        dangling = self.fetch_count(
            """
            SELECT COUNT(*)
            FROM claim c
            LEFT JOIN source s ON s.source_id = c.source_id
            WHERE c.source_id IS NOT NULL
              AND c.source_id <> ''
              AND s.source_id IS NULL
            """
        )
        self.assertEqual(missing, 0)
        self.assertEqual(dangling, 0)

    def test_relation_source_target_are_distinct(self):
        invalid = self.fetch_count(
            """
            SELECT COUNT(*)
            FROM relation
            WHERE source_organization_id = target_organization_id
            """
        )
        self.assertEqual(invalid, 0)

    def test_function_record_function_type_exists(self):
        dangling = self.fetch_count(
            """
            SELECT COUNT(*)
            FROM function_record fr
            LEFT JOIN function_type ft
              ON ft.function_type_id = fr.function_type_id
            WHERE ft.function_type_id IS NULL
            """
        )
        self.assertEqual(dangling, 0)

    def test_claim_value_kind_enum(self):
        placeholders = ",".join("?" for _ in VALUE_KINDS)
        invalid = self.fetch_count(
            f"SELECT COUNT(*) FROM claim WHERE value_kind NOT IN ({placeholders})",
            tuple(VALUE_KINDS),
        )
        self.assertEqual(invalid, 0)

    def test_date_precision_enum(self):
        placeholders = ",".join("?" for _ in DATE_PRECISIONS)
        invalids = []
        for table, column in DATE_PRECISION_COLUMNS:
            count = self.fetch_count(
                f"""
                SELECT COUNT(*)
                FROM {table}
                WHERE {column} IS NOT NULL
                  AND {column} NOT IN ({placeholders})
                """,
                tuple(DATE_PRECISIONS),
            )
            if count:
                invalids.append(f"{table}.{column}: {count}")
        self.assertEqual(invalids, [])

    def test_source_redistribution_enum(self):
        placeholders = ",".join("?" for _ in REDISTRIBUTIONS)
        invalid = self.fetch_count(
            f"""
            SELECT COUNT(*)
            FROM source
            WHERE redistribution IS NOT NULL
              AND redistribution NOT IN ({placeholders})
            """,
            tuple(REDISTRIBUTIONS),
        )
        self.assertEqual(invalid, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
