# Organization Genealogy API Examples

Assume `API_BASE` points to the deployed base URL. The current repository has no deployed REST API; these examples describe the Phase 6 / v0.7+ interface.

Known sandbox IDs used below were checked in `data/og.db`:

- VOC: `9e99525267034e16af5863b9db8e63e6`
- Benedictines: `2cf732ca2e44458b8d793880b59a1b5d`
- Cistercians: `d9c2571497d84171ad42eb73e6c6799c`
- Cluny: `dfb63f4c58a146ba99c30686d317401a`
- Rule of St. Benedict public source: `8ad49f7c9c384ef395450a46c0952325`

## curl examples

List extinct organizations active around 1700:

```bash
curl "$API_BASE/v1/organizations?era=1700&status=extinct&page=1&limit=20"
```

Get VOC detail:

```bash
curl "$API_BASE/v1/organizations/9e99525267034e16af5863b9db8e63e6"
```

Get all visible VOC function records:

```bash
curl "$API_BASE/v1/organizations/9e99525267034e16af5863b9db8e63e6/functions"
```

Expected shape:

```json
{
  "data": [
    {
      "function_id": "string",
      "organization_id": "9e99525267034e16af5863b9db8e63e6",
      "function_type_id": "miller_02_boundary",
      "function_type": {
        "function_type_id": "miller_02_boundary",
        "name_en": "Boundary"
      },
      "mechanism": {},
      "beneficiaries": {},
      "dependency": {},
      "confidence": 0.0,
      "claim": {
        "claim_id": "string",
        "source_id": "string",
        "confidence": 0.0
      }
    }
  ]
}
```

Current sandbox VOC function types are `miller_02_boundary`, `miller_03_ingestor`, `miller_06_producer`, `miller_17_memory`, `miller_18_decider`, `vsm_s1_operations`, and `vsm_s4_intelligence_strategy`.

Benedictine succession chain, one hop at a time:

```bash
curl "$API_BASE/v1/organizations/2cf732ca2e44458b8d793880b59a1b5d/relations?relation_type=succession"
```

Current sandbox succession rows from the Benedictines:

```json
{
  "data": [
    {
      "relation_id": "1a68128971394201ad4aa8bae718b94a",
      "source_organization_id": "2cf732ca2e44458b8d793880b59a1b5d",
      "target_organization_id": "dfb63f4c58a146ba99c30686d317401a",
      "relation_type": "succession",
      "valid_from": "0910-09-11"
    },
    {
      "relation_id": "783a2782667f436999fa7c35afcd5923",
      "source_organization_id": "2cf732ca2e44458b8d793880b59a1b5d",
      "target_organization_id": "d9c2571497d84171ad42eb73e6c6799c",
      "relation_type": "succession",
      "valid_from": "1098-03-21"
    }
  ]
}
```

Network projection for the same succession edges:

```bash
curl "$API_BASE/v1/genealogy/network?root_organization_id=2cf732ca2e44458b8d793880b59a1b5d&relation_type=succession&direction=outgoing&depth=2"
```

Year-specific state using Phase 4 temporal facets:

```bash
curl "$API_BASE/v1/organizations/9e99525267034e16af5863b9db8e63e6/temporal-facets?at=1700-01-01"
```

Governance-only temporal facets:

```bash
curl "$API_BASE/v1/organizations/9e99525267034e16af5863b9db8e63e6/temporal-facets?facet_type=governance"
```

List public sources only:

```bash
curl "$API_BASE/v1/sources?source_type=primary_text"
```

Get public claims for the Rule of St. Benedict source:

```bash
curl "$API_BASE/v1/sources/8ad49f7c9c384ef395450a46c0952325/claims"
```

Private API key pattern for future private access:

```bash
curl -H "X-API-Key: $ORG_GENEALOGY_API_KEY" "$API_BASE/v1/private/..."
```

The public endpoints above do not require this header.

## SQL to API correspondence

Public organization list:

```sql
SELECT DISTINCT o.*
FROM organization o
JOIN claim c
  ON c.entity_type = 'organization'
 AND c.entity_id = o.organization_id
JOIN source s
  ON s.source_id = c.source_id
WHERE s.redistribution = 'public_redistributable'
  AND o.status = :status
  AND (:era IS NULL OR (
    (o.start_date IS NULL OR o.start_date <= :era_date)
    AND (o.end_date IS NULL OR o.end_date > :era_date)
  ))
ORDER BY o.canonical_name
LIMIT :limit OFFSET (:page - 1) * :limit;
```

API:

```bash
curl "$API_BASE/v1/organizations?status=extinct&era=1700-01-01&page=1&limit=50"
```

Organization detail:

```sql
SELECT o.*
FROM organization o
WHERE o.organization_id = :organization_id
  AND EXISTS (
    SELECT 1
    FROM claim c
    JOIN source s ON s.source_id = c.source_id
    WHERE c.entity_type = 'organization'
      AND c.entity_id = o.organization_id
      AND s.redistribution = 'public_redistributable'
  );
```

API:

```bash
curl "$API_BASE/v1/organizations/:organization_id"
```

VOC function records:

```sql
SELECT fr.*, ft.*
FROM function_record fr
JOIN function_type ft
  ON ft.function_type_id = fr.function_type_id
JOIN claim c
  ON c.claim_id = fr.claim_id
JOIN source s
  ON s.source_id = c.source_id
WHERE fr.organization_id = '9e99525267034e16af5863b9db8e63e6'
  AND s.redistribution = 'public_redistributable'
ORDER BY ft.function_type_id;
```

API:

```bash
curl "$API_BASE/v1/organizations/9e99525267034e16af5863b9db8e63e6/functions"
```

Benedictine succession chain:

```sql
SELECT r.*, target.canonical_name AS target_name
FROM relation r
JOIN organization target
  ON target.organization_id = r.target_organization_id
JOIN claim c
  ON c.claim_id = r.claim_id
JOIN source s
  ON s.source_id = c.source_id
WHERE r.source_organization_id = '2cf732ca2e44458b8d793880b59a1b5d'
  AND r.relation_type = 'succession'
  AND s.redistribution = 'public_redistributable'
ORDER BY r.valid_from;
```

API:

```bash
curl "$API_BASE/v1/organizations/2cf732ca2e44458b8d793880b59a1b5d/relations?relation_type=succession"
```

Year-specific state with temporal facets:

```sql
SELECT facet_type, facet_value, confidence, valid_from, valid_to
FROM organization_temporal_facet f
JOIN claim c
  ON c.claim_id = f.claim_id
JOIN source s
  ON s.source_id = c.source_id
WHERE f.organization_id = :organization_id
  AND (f.valid_from IS NULL OR f.valid_from <= :at)
  AND (f.valid_to IS NULL OR f.valid_to > :at)
  AND s.redistribution = 'public_redistributable'
ORDER BY facet_type;
```

API:

```bash
curl "$API_BASE/v1/organizations/:organization_id/temporal-facets?at=1700-01-01"
```

Public sources:

```sql
SELECT *
FROM source
WHERE redistribution = 'public_redistributable'
ORDER BY title
LIMIT :limit OFFSET (:page - 1) * :limit;
```

API:

```bash
curl "$API_BASE/v1/sources?page=1&limit=50"
```

Claims for a public source:

```sql
SELECT c.*
FROM claim c
JOIN source s
  ON s.source_id = c.source_id
WHERE c.source_id = :source_id
  AND s.redistribution = 'public_redistributable'
  AND c.superseded_by IS NULL
ORDER BY c.recorded_at DESC
LIMIT :limit OFFSET (:page - 1) * :limit;
```

API:

```bash
curl "$API_BASE/v1/sources/:source_id/claims?page=1&limit=50"
```
