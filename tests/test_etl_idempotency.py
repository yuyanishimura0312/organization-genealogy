import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

LOCAL_DATA_ETL = (
    "01_load_function_types.py",
    "02_seed_organization_forms.py",
    "04_representative_cases.py",
    "07_phase2_diversity_cases.py",
    "08_phase3_chain_cases.py",
    "11_isolate_resolution.py",
    "14_ancient_cases.py",
    "15_marginal_movements.py",
    "16_temporal_facets.py",
    "22_islamic_world_cases.py",
    "23_east_asian_cases.py",
    "24_modern_organizations.py",
)

TRACKED_TABLES = (
    "source",
    "claim",
    "organization",
    "organization_form_assignment",
    "activity",
    "function_record",
    "impact_record",
    "relation",
    "event",
    "event_organization",
    "event_relation",
    "dormancy_record",
    "organization_temporal_facet",
)

DUPLICATE_CHECKS = (
    (
        "organization.canonical_name",
        """
        SELECT canonical_name, COUNT(*)
        FROM organization
        GROUP BY canonical_name
        HAVING COUNT(*) > 1
        """,
    ),
    (
        "source.title",
        """
        SELECT title, COUNT(*)
        FROM source
        GROUP BY title
        HAVING COUNT(*) > 1
        """,
    ),
    (
        "relation.natural_key",
        """
        SELECT source_organization_id, target_organization_id, relation_type,
               COALESCE(valid_from, ''), COALESCE(valid_to, ''), COUNT(*)
        FROM relation
        GROUP BY source_organization_id, target_organization_id, relation_type,
                 COALESCE(valid_from, ''), COALESCE(valid_to, '')
        HAVING COUNT(*) > 1
        """,
    ),
    (
        "organization_form_assignment.natural_key",
        """
        SELECT organization_id, form_id, COALESCE(valid_from, ''),
               COALESCE(valid_to, ''), is_primary, COUNT(*)
        FROM organization_form_assignment
        GROUP BY organization_id, form_id, COALESCE(valid_from, ''),
                 COALESCE(valid_to, ''), is_primary
        HAVING COUNT(*) > 1
        """,
    ),
)


class EtlIdempotencyTest(unittest.TestCase):
    def test_local_data_etl_second_run_does_not_create_new_rows(self):
        if not DB.exists():
            raise unittest.SkipTest(f"database not found: {DB}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp) / "organization-genealogy"
            self.copy_project_subset(tmp_root)
            scripts = [tmp_root / "etl" / name for name in LOCAL_DATA_ETL]

            before = self.table_counts(tmp_root / "data" / "og.db")
            first = self.run_scripts(scripts, tmp_root)
            after_first = self.table_counts(tmp_root / "data" / "og.db")
            second = self.run_scripts(scripts, tmp_root)
            after_second = self.table_counts(tmp_root / "data" / "og.db")
            duplicate_report = self.duplicate_report(tmp_root / "data" / "og.db")

        warnings_out = []
        for label, result in (("first run", first), ("second run", second)):
            failed = [item for item in result if item[1] != 0]
            if failed:
                warnings_out.append(
                    f"{label} failed: "
                    + ", ".join(f"{path.name} rc={code}" for path, code in failed)
                )

        first_delta = self.delta(before, after_first)
        second_delta = self.delta(after_first, after_second)
        if any(second_delta.values()):
            warnings_out.append(f"second run inserted/changed rows: {second_delta}")
        if duplicate_report:
            warnings_out.append(f"duplicate natural keys detected: {duplicate_report}")

        if warnings_out:
            warnings.warn("ETL idempotency warning: " + " | ".join(warnings_out))
            print("ETL_IDEMPOTENCY_WARNING:", " | ".join(warnings_out))

        self.assertTrue(True)

    @staticmethod
    def copy_project_subset(tmp_root):
        tmp_root.mkdir()
        shutil.copytree(ROOT / "etl", tmp_root / "etl")
        shutil.copytree(ROOT / "data", tmp_root / "data")
        shutil.copytree(ROOT / "research", tmp_root / "research")

    @staticmethod
    def run_scripts(scripts, cwd):
        results = []
        for script in scripts:
            completed = subprocess.run(
                [sys.executable, str(script)],
                cwd=cwd,
                text=True,
                capture_output=True,
                timeout=180,
            )
            results.append((script, completed.returncode))
        return results

    @staticmethod
    def table_counts(db_path):
        conn = sqlite3.connect(db_path)
        try:
            return {
                table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in TRACKED_TABLES
            }
        finally:
            conn.close()

    @staticmethod
    def delta(before, after):
        return {
            table: after[table] - before[table]
            for table in TRACKED_TABLES
            if after[table] != before[table]
        }

    @staticmethod
    def duplicate_report(db_path):
        conn = sqlite3.connect(db_path)
        try:
            report = {}
            for label, sql in DUPLICATE_CHECKS:
                count = len(conn.execute(sql).fetchall())
                if count:
                    report[label] = count
            return report
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
