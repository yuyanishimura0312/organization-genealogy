# Test Harness

Run all tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

`test_schema.py` checks `data/og.db` directly for:

- fully annotated organizations, defined by existing ETL convention as organizations with at least one `function_record`, having at least one `organization_form_assignment`
- every `claim.source_id` being present and resolving to `source.source_id`
- `relation.source_organization_id != relation.target_organization_id`
- `function_record.function_type_id` resolving to `function_type.function_type_id`
- `claim.value_kind`, date precision columns, and `source.redistribution` staying within the schema ENUM values

`test_etl_idempotency.py` copies the real `data/og.db` into a temporary project subset, runs local DB-writing ETL scripts twice, and reports row-count changes or duplicate natural keys as warnings. Network ETL and visualization/report generators are excluded so the test can run offline and avoid rewriting repository artifacts.
