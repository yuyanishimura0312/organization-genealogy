# Data Dictionary

This dictionary describes the SQLite sandbox schema for Organization Genealogy Analysis. It uses the schema in `sql/schema_sqlite_v01.sql` as the baseline and includes the current sandbox table `organization_temporal_facet`, which is present in `data/og.db`.

## Core Modeling Rules

- Every substantive assertion should be represented as a `claim`.
- `claim.entity_type` and `claim.entity_id` provide the flexible claim-to-entity link.
- Entity tables may also carry `claim_id` when a record is directly supported by one claim.
- JSON values are stored as `TEXT` in SQLite.
- UUID-like identifiers are stored as `TEXT`.
- Date values are stored as `TEXT`, with precision stored in adjacent precision columns.
- Confidence values are bounded from `0.0` to `1.0`.

## Claim Value Kinds

`claim.value_kind` has five allowed values:

| Value | Meaning | Why it matters |
| --- | --- | --- |
| `present` | The claim states that the value or feature exists. | Used for positive evidence. |
| `absent` | The claim explicitly states that the value or feature does not exist. | Keeps evidenced absence separate from missing data. |
| `partial` | The claim states partial, bounded, or uneven presence. | Handles region-, period-, unit-, or scale-limited evidence. |
| `unknown` | The claim cannot determine the value. | Prevents unknown evidence from being coded as absence. |
| `inapplicable` | The concept does not apply to the organization, period, or field. | Prevents anachronistic coding. |

The Stream J lesson is that `NA` must not be collapsed into `absent`. Historical comparative data often mixes non-observation, conceptual non-applicability, and explicit absence; the five-value vocabulary keeps those states analytically distinct.

## Claim Integration Pattern

Typical pattern:

```sql
INSERT INTO claim (
  claim_id, entity_type, entity_id, field_path, value_kind,
  claim_value, source_id, confidence, recorded_by
) VALUES (
  'claim_example',
  'organization',
  'org_example',
  'status',
  'present',
  '{"status":"active"}',
  'source_example',
  0.80,
  'researcher@example.org'
);
```

For tables with `claim_id`, the row can point directly to the claim that supports the record:

```sql
SELECT o.canonical_name, fr.function_type_id, c.confidence
FROM function_record fr
JOIN organization o ON o.organization_id = fr.organization_id
LEFT JOIN claim c ON c.claim_id = fr.claim_id;
```

## Tables

### `source`

Purpose: stores bibliographic, archival, dataset, web, on-chain, interview, oral history, ethnographic, and artifact source metadata.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `source_id` | TEXT | PRIMARY KEY | Source identifier. |
| `source_type` | TEXT | NOT NULL, CHECK enum | `primary_text`, `secondary_literature`, `dataset`, `interview`, `archive`, `artifact`, `onchain`, `web`, `oral_history`, `ethnography`. |
| `title` | TEXT | NOT NULL | Source title. |
| `authors` | TEXT | JSON array | Authors, editors, or organizations. |
| `publication_date` | TEXT | ISO 8601 | Publication date. |
| `publisher` | TEXT | Nullable | Publisher. |
| `locator` | TEXT | JSON | Page, URL, DOI, archive ID, contract address, or similar locator. |
| `accessed_at` | TEXT | ISO 8601 | Access date. |
| `reliability_score` | REAL | 0.0-1.0 or NULL | Source-level reliability score. |
| `reliability_basis` | TEXT | Nullable | Basis for reliability judgment. |
| `bias_notes` | TEXT | Nullable | Known bias, standpoint, or coverage gaps. |
| `license` | TEXT | Nullable | Source license. |
| `redistribution` | TEXT | CHECK enum | `public_redistributable`, `attribution_required`, `noncommercial`, `private`, `restricted`. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_source_type(source_type)`, `idx_source_redist(redistribution)`.

Claim integration pattern: source rows are referenced from `claim.source_id`; redistribution controls future public-data filtering.

### `claim`

Purpose: stores sourced assertions about fields, records, relations, events, functions, and other entities.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `claim_id` | TEXT | PRIMARY KEY | Claim identifier. |
| `entity_type` | TEXT | NOT NULL | Target table or entity category. |
| `entity_id` | TEXT | NOT NULL | Target record identifier. |
| `field_path` | TEXT | Nullable | Field or JSON path, such as `attributes.membership_size`. |
| `value_kind` | TEXT | NOT NULL, CHECK enum | `present`, `absent`, `partial`, `unknown`, `inapplicable`. |
| `claim_value` | TEXT | JSON | Claimed value. |
| `source_id` | TEXT | FK to `source(source_id)` ON DELETE RESTRICT | Supporting source. |
| `confidence` | REAL | NOT NULL, 0.0-1.0 | Claim-level confidence. |
| `interpretation_note` | TEXT | Nullable | Interpretation note. |
| `recorded_by` | TEXT | NOT NULL | Recorder identifier. |
| `recorded_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Recording timestamp. |
| `superseded_by` | TEXT | FK to `claim(claim_id)` | Supersession link. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_claim_entity(entity_type, entity_id)`, `idx_claim_source(source_id)`.

Claim integration pattern: this is the hub table. Other records either receive field-level claims through `entity_type/entity_id/field_path` or direct support through their `claim_id`.

### `organization_form`

Purpose: stores organization type taxonomies without forcing all types into one hierarchy.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `form_id` | TEXT | PRIMARY KEY | Form identifier. |
| `taxonomy_name` | TEXT | NOT NULL, UNIQUE with `form_code` | Taxonomy name. |
| `form_code` | TEXT | NOT NULL, UNIQUE with `taxonomy_name` | Stable code inside taxonomy. |
| `label` | TEXT | NOT NULL | Display label. |
| `parent_form_id` | TEXT | FK to `organization_form(form_id)` | Parent form. |
| `definition` | TEXT | Nullable | Definition. |
| `criteria` | TEXT | JSON | Classification criteria. |
| `valid_period_from` | TEXT | Nullable | Start of taxonomy validity. |
| `valid_period_to` | TEXT | Nullable | End of taxonomy validity. |
| `notes` | TEXT | Nullable | Notes. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_form_taxonomy(taxonomy_name)`.

Claim integration pattern: form definitions can be claimed through `claim.entity_type = 'organization_form'`; organization-specific use is supported through `organization_form_assignment.claim_id`.

### `organization`

Purpose: stores organizational units: bands, lineages, monasteries, guilds, states, companies, platforms, DAOs, and other comparable units.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `organization_id` | TEXT | PRIMARY KEY | Organization identifier. |
| `canonical_name` | TEXT | NOT NULL | Main name. |
| `alternate_names` | TEXT | JSON array | Alternate names with language tags. |
| `description` | TEXT | Nullable | Short description. |
| `primary_form_id` | TEXT | FK to `organization_form(form_id)` | Primary form. |
| `geo_scope` | TEXT | JSON | Geographic scope and uncertainty. |
| `start_date` | TEXT | Nullable | Start date. |
| `start_date_precision` | TEXT | CHECK enum or NULL | `exact`, `year`, `decade`, `century`, `period`, `before`, `after`, `unknown`. |
| `end_date` | TEXT | Nullable | End date. |
| `end_date_precision` | TEXT | CHECK enum or NULL | Same precision vocabulary. |
| `status` | TEXT | NOT NULL DEFAULT `unknown`, CHECK enum | `active`, `dormant`, `transformed`, `merged`, `split`, `extinct`, `unknown`. |
| `attributes` | TEXT | JSON | Variable attributes. |
| `embedding` | BLOB | Nullable | SQLite placeholder for future pgvector migration. |
| `external_ids` | TEXT | JSON | Wikidata, LEI, ROR, EDINET, or other IDs. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_org_form(primary_form_id)`, `idx_org_status(status)`, `idx_org_dates(start_date, end_date)`.

Claim integration pattern: core fields can be claimed through `claim.field_path`; time-varying details should use `organization_temporal_facet` or domain tables.

### `organization_form_assignment`

Purpose: links organizations to one or more forms across time.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `assignment_id` | TEXT | PRIMARY KEY | Assignment identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `form_id` | TEXT | NOT NULL, FK to `organization_form` ON DELETE RESTRICT | Assigned form. |
| `valid_from` | TEXT | Nullable | Start of assignment validity. |
| `valid_from_precision` | TEXT | Nullable | Date precision. |
| `valid_to` | TEXT | Nullable | End of assignment validity. |
| `valid_to_precision` | TEXT | Nullable | Date precision. |
| `is_primary` | INTEGER | NOT NULL DEFAULT 0, CHECK 0/1 | Primary assignment flag. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_ofa_org(organization_id)`, `idx_ofa_form(form_id)`.

Claim integration pattern: use `claim_id` when a source supports the assignment; use field-level claims for details such as period or confidence.

### `organization_temporal_facet`

Purpose: stores time-bounded organizational states such as membership, governance, resource base, territory, technology, identity, scale, and legitimation basis.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `organization_facet_id` | TEXT | PRIMARY KEY | Facet identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `valid_from` | TEXT | Nullable | Start of facet validity. |
| `valid_from_precision` | TEXT | CHECK enum or NULL | Date precision. |
| `valid_to` | TEXT | Nullable | End of facet validity. |
| `valid_to_precision` | TEXT | CHECK enum or NULL | Date precision. |
| `facet_type` | TEXT | NOT NULL, CHECK enum | `membership`, `governance`, `resource_base`, `territory`, `technology`, `identity`, `scale`, `legitimation_basis`. |
| `facet_value` | TEXT | NOT NULL, JSON | Facet value. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_otf_org(organization_id)`, `idx_otf_type(facet_type)`, `idx_otf_dates(valid_from, valid_to)`.

Claim integration pattern: use this table when the value is time-bounded or facet-specific instead of overloading `organization.attributes`.

### `function_type`

Purpose: stores the 25-function taxonomy used by `function_record`.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `function_type_id` | TEXT | PRIMARY KEY | Stable taxonomy ID. |
| `name_ja` | TEXT | NOT NULL | Japanese label. |
| `name_en` | TEXT | NOT NULL | English label. |
| `source_framework` | TEXT | NOT NULL, CHECK enum | `miller_living_systems`, `beer_vsm`, `compound`. |
| `miller_subsystem_no` | INTEGER | Nullable | Miller subsystem number. |
| `vsm_system_no` | TEXT | Nullable | Beer VSM system number. |
| `parent_function_type_id` | TEXT | FK to `function_type(function_type_id)` | Optional parent. |
| `definition` | TEXT | NOT NULL | Definition. |
| `observable_indicators` | TEXT | JSON | Observable indicators. |
| `era_examples` | TEXT | JSON | Era-specific examples. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: no explicit index beyond primary key.

Claim integration pattern: taxonomy records can be claimed through `claim.entity_type = 'function_type'`; actual organizational use belongs in `function_record`.

### `activity`

Purpose: records what an organization does: production, exchange, ritual, administration, education, military action, software development, platform operation, and other activities.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `activity_id` | TEXT | PRIMARY KEY | Activity identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `activity_type` | TEXT | NOT NULL | Activity category. |
| `domain` | TEXT | Nullable | Domain such as production, governance, ritual, knowledge, care, or military. |
| `description` | TEXT | Nullable | Activity description. |
| `inputs` | TEXT | JSON | Inputs. |
| `outputs` | TEXT | JSON | Outputs. |
| `scale` | TEXT | JSON | Scale, frequency, participants, or volume. |
| `orientation` | TEXT | NOT NULL DEFAULT `unspecified`, CHECK enum | `exploration`, `exploitation`, `mixed`, `unspecified`. |
| `valid_from` | TEXT | Nullable | Start of validity. |
| `valid_from_precision` | TEXT | Nullable | Date precision. |
| `valid_to` | TEXT | Nullable | End of validity. |
| `valid_to_precision` | TEXT | Nullable | Date precision. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_activity_org(organization_id)`, `idx_activity_type(activity_type)`.

Claim integration pattern: use `claim_id` for the activity record; use field-level claims for inputs, outputs, scale, and period.

### `function_record`

Purpose: records which living-system function an activity or mechanism performs for an organization.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `function_id` | TEXT | PRIMARY KEY | Function record identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `function_type_id` | TEXT | NOT NULL, FK to `function_type` | Function taxonomy ID. |
| `mechanism` | TEXT | JSON | Concrete mechanism, role, unit, procedure, or technology. |
| `beneficiaries` | TEXT | JSON | Beneficiaries or target groups. |
| `dependency` | TEXT | JSON | Required resources, institutions, or technologies. |
| `activity_id` | TEXT | FK to `activity(activity_id)` | Related activity. |
| `valid_from` | TEXT | Nullable | Start of validity. |
| `valid_from_precision` | TEXT | Nullable | Date precision. |
| `valid_to` | TEXT | Nullable | End of validity. |
| `valid_to_precision` | TEXT | Nullable | Date precision. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_fr_org(organization_id)`, `idx_fr_type(function_type_id)`.

Claim integration pattern: use this table for "what function was performed"; keep "what happened" in `activity`.

### `impact_record`

Purpose: records effects on external environments, members, institutions, technology, culture, ecosystems, and other scopes.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `impact_id` | TEXT | PRIMARY KEY | Impact identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `impact_domain` | TEXT | NOT NULL | Domain of impact. |
| `metric_name` | TEXT | NOT NULL | Metric or indicator name. |
| `metric_value` | TEXT | NOT NULL, JSON | Numeric, categorical, range, or estimated value. |
| `direction` | TEXT | NOT NULL, CHECK enum | `positive`, `negative`, `mixed`, `uncertain`, `descriptive`. |
| `time_horizon` | TEXT | NOT NULL, CHECK enum | `immediate`, `short_term`, `medium_term`, `long_term`, `intergenerational`. |
| `affected_scope` | TEXT | JSON | Geographic, population, or institutional scope. |
| `evaluation_method` | TEXT | Nullable | Comparison, quantitative estimate, expert assessment, or source interpretation. |
| `valid_from` | TEXT | Nullable | Start of validity. |
| `valid_from_precision` | TEXT | Nullable | Date precision. |
| `valid_to` | TEXT | Nullable | End of validity. |
| `valid_to_precision` | TEXT | Nullable | Date precision. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_impact_org(organization_id)`, `idx_impact_domain(impact_domain)`.

Claim integration pattern: metric values and interpretation should remain claim-backed, especially where impact direction is contested.

### `relation`

Purpose: stores organization-to-organization edges with type, direction, period, strength, and evidence.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `relation_id` | TEXT | PRIMARY KEY | Relation identifier. |
| `source_organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Source organization. |
| `target_organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Target organization. |
| `relation_type` | TEXT | NOT NULL, CHECK enum | Includes alliance, competition, control, subsidiary, partnership, membership, succession, spin-off, merger, acquisition, trade, funding, shareholding, knowledge transfer, institutional pressure, protocol dependency, supply chain, interlocking directorate, patronage, rivalry, schism, unknown. |
| `directionality` | TEXT | NOT NULL DEFAULT `directed`, CHECK enum | `directed`, `undirected`, `bidirectional`. |
| `valid_from` | TEXT | Nullable | Start of relation. |
| `valid_from_precision` | TEXT | Nullable | Date precision. |
| `valid_to` | TEXT | Nullable | End of relation. |
| `valid_to_precision` | TEXT | Nullable | Date precision. |
| `strength` | REAL | 0.0-1.0 or NULL | Relation strength; NULL is preferred when no basis exists. |
| `strength_basis` | TEXT | Nullable | Basis for strength value. |
| `relation_attributes` | TEXT | JSON | Relation-specific attributes. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Additional constraint: `source_organization_id <> target_organization_id`.

Indexes: `idx_rel_source(source_organization_id)`, `idx_rel_target(target_organization_id)`, `idx_rel_type(relation_type)`.

Claim integration pattern: record the edge as a relation, attach a claim for evidence, and use `event_relation` when an event changes the edge.

### `event`

Purpose: stores organizational state-change events such as founding, dissolution, merger, split, reform, crisis, governance change, platform shift, dormancy, revival, and reorganization.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `event_id` | TEXT | PRIMARY KEY | Event identifier. |
| `event_type` | TEXT | NOT NULL, CHECK enum | Founding, dissolution, merger, acquisition, split, spin-off, renaming, relocation, reform, crisis, governance change, platform shift, IPO, privatization, nationalization, dormancy start/end, revival, reorganization, unknown. |
| `event_date` | TEXT | Nullable | Event date. |
| `event_date_precision` | TEXT | NOT NULL DEFAULT `unknown` | Date precision. |
| `description` | TEXT | Nullable | Event description. |
| `participants` | TEXT | JSON | Participants. |
| `causes` | TEXT | JSON | Causes. |
| `outcomes` | TEXT | JSON | Outcomes. |
| `location` | TEXT | JSON | Location. |
| `dissolution_cause` | TEXT | CHECK enum or NULL | Bankruptcy, merger, split, wind-down, regulatory dissolution, war destruction, schism, purge, natural disaster, succession failure, obsolescence, absorption, transformation, unknown. |
| `vsr_label` | TEXT | CHECK enum or NULL | `variation`, `selection`, `retention`, `struggle`. |
| `confidence` | REAL | 0.0-1.0 or NULL | Confidence. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: `idx_event_type(event_type)`, `idx_event_date(event_date)`.

Claim integration pattern: use `claim_id` for the event assertion; connect affected organizations through `event_organization` and relation changes through `event_relation`.

### `event_organization`

Purpose: links events to participating or affected organizations.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `event_organization_id` | TEXT | PRIMARY KEY | Link identifier. |
| `event_id` | TEXT | NOT NULL, FK to `event` ON DELETE CASCADE | Event. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `role` | TEXT | NOT NULL, UNIQUE with `event_id` and `organization_id` | Role in event. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: no explicit index beyond the unique constraint and primary key.

Claim integration pattern: the event usually carries the source claim; role-specific uncertainty can be modeled as a claim on this link row.

### `event_relation`

Purpose: links events to relation changes.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `event_relation_id` | TEXT | PRIMARY KEY | Link identifier. |
| `event_id` | TEXT | NOT NULL, FK to `event` ON DELETE CASCADE | Event. |
| `relation_id` | TEXT | NOT NULL, FK to `relation` ON DELETE CASCADE | Relation. |
| `change_type` | TEXT | NOT NULL, CHECK enum | `relation_started`, `relation_ended`, `strength_changed`, `type_changed`. |
| `before_value` | TEXT | Nullable | Previous value. |
| `after_value` | TEXT | Nullable | New value. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: no explicit index beyond primary key.

Claim integration pattern: relation change evidence should be represented by claims on the event, relation, or this link row depending on granularity.

### `dormancy_record`

Purpose: records dormancy and revival patterns that are not well represented by a single death event.

| Column | Type | Constraint | Note |
| --- | --- | --- | --- |
| `dormancy_id` | TEXT | PRIMARY KEY | Dormancy identifier. |
| `organization_id` | TEXT | NOT NULL, FK to `organization` ON DELETE CASCADE | Organization. |
| `start_date` | TEXT | Nullable | Dormancy start. |
| `start_date_precision` | TEXT | Nullable | Date precision. |
| `end_date` | TEXT | Nullable | Dormancy end. |
| `end_date_precision` | TEXT | Nullable | Date precision. |
| `start_event_id` | TEXT | FK to `event(event_id)` | Starting event. |
| `end_event_id` | TEXT | FK to `event(event_id)` | Ending event. |
| `dormancy_type` | TEXT | CHECK enum or NULL | `legal_dormant`, `inactive_active_legal`, `cultural_only`, `shell`, `unknown`. |
| `notes` | TEXT | Nullable | Notes. |
| `claim_id` | TEXT | FK to `claim(claim_id)` | Supporting claim. |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Created timestamp. |
| `updated_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Updated timestamp. |
| `record_version` | INTEGER | NOT NULL DEFAULT 1 | Version counter. |

Indexes: no explicit index beyond primary key.

Claim integration pattern: use this table for dormant-but-not-dead cases; link start and end events when available.

## 25 Function Taxonomy

| ID | English label | Framework |
| --- | --- | --- |
| `miller_01_reproducer` | Reproducer | Miller Living Systems |
| `miller_02_boundary` | Boundary | Miller Living Systems |
| `miller_03_ingestor` | Ingestor | Miller Living Systems |
| `miller_04_distributor` | Distributor | Miller Living Systems |
| `miller_05_converter` | Converter | Miller Living Systems |
| `miller_06_producer` | Producer | Miller Living Systems |
| `miller_07_matter_energy_storage` | Matter-Energy Storage | Miller Living Systems |
| `miller_08_extruder` | Extruder | Miller Living Systems |
| `miller_09_motor` | Motor | Miller Living Systems |
| `miller_10_supporter` | Supporter | Miller Living Systems |
| `miller_11_input_transducer` | Input Transducer | Miller Living Systems |
| `miller_12_internal_transducer` | Internal Transducer | Miller Living Systems |
| `miller_13_channel_and_net` | Channel and Net | Miller Living Systems |
| `miller_14_timer` | Timer | Miller Living Systems |
| `miller_15_decoder` | Decoder | Miller Living Systems |
| `miller_16_associator` | Associator | Miller Living Systems |
| `miller_17_memory` | Memory | Miller Living Systems |
| `miller_18_decider` | Decider | Miller Living Systems |
| `miller_19_encoder` | Encoder | Miller Living Systems |
| `miller_20_output_transducer` | Output Transducer | Miller Living Systems |
| `vsm_s1_operations` | System 1 Operations | Beer VSM |
| `vsm_s2_coordination` | System 2 Coordination | Beer VSM |
| `vsm_s3_internal_control` | System 3 Internal Control and Audit | Beer VSM |
| `vsm_s4_intelligence_strategy` | System 4 Intelligence and Strategy | Beer VSM |
| `vsm_s5_policy_identity` | System 5 Policy and Identity | Beer VSM |

## Example Queries

Organizations by status:

```sql
SELECT status, COUNT(*) AS organization_count
FROM organization
GROUP BY status
ORDER BY organization_count DESC;
```

Claims by value kind:

```sql
SELECT value_kind, COUNT(*) AS claim_count
FROM claim
GROUP BY value_kind
ORDER BY claim_count DESC;
```

Claim-backed organization fields:

```sql
SELECT o.canonical_name, c.field_path, c.value_kind, c.confidence, s.title
FROM claim c
JOIN organization o
  ON c.entity_type = 'organization'
 AND c.entity_id = o.organization_id
LEFT JOIN source s ON s.source_id = c.source_id
ORDER BY o.canonical_name, c.field_path;
```

Function coverage by organization:

```sql
SELECT o.canonical_name, COUNT(DISTINCT fr.function_type_id) AS function_count
FROM organization o
LEFT JOIN function_record fr ON fr.organization_id = o.organization_id
GROUP BY o.organization_id, o.canonical_name
ORDER BY function_count DESC, o.canonical_name;
```

Organizations with temporal facets:

```sql
SELECT o.canonical_name, otf.facet_type, otf.valid_from, otf.valid_to, otf.confidence
FROM organization_temporal_facet otf
JOIN organization o ON o.organization_id = otf.organization_id
ORDER BY o.canonical_name, otf.facet_type, otf.valid_from;
```

Relations by type:

```sql
SELECT relation_type, COUNT(*) AS relation_count
FROM relation
GROUP BY relation_type
ORDER BY relation_count DESC;
```

Network edge list:

```sql
SELECT
  s.canonical_name AS source,
  r.relation_type,
  t.canonical_name AS target,
  r.valid_from,
  r.valid_to,
  r.strength
FROM relation r
JOIN organization s ON s.organization_id = r.source_organization_id
JOIN organization t ON t.organization_id = r.target_organization_id
ORDER BY r.relation_type, source, target;
```

Event timeline:

```sql
SELECT event_type, event_date, event_date_precision, description, vsr_label
FROM event
ORDER BY event_date, event_type;
```

Dormancy and revival cases:

```sql
SELECT o.canonical_name, d.dormancy_type, d.start_date, d.end_date, d.notes
FROM dormancy_record d
JOIN organization o ON o.organization_id = d.organization_id
ORDER BY d.start_date;
```

Publicly redistributable evidence:

```sql
SELECT c.claim_id, c.entity_type, c.field_path, s.title, s.redistribution
FROM claim c
JOIN source s ON s.source_id = c.source_id
WHERE s.redistribution = 'public_redistributable';
```
