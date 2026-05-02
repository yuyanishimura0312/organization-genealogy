# Function Taxonomy Coverage

Generated from `data/og.db` using `etl/13_function_heatmap.py`.

Provenance: `{claim: function taxonomy distribution, source_url: local:data/og.db, retrieval_date: 2026-05-03, confidence: high}`

## Scope

- Annotated organizations: 18
- Function types: 25
- Function records counted: 77
- HTML heatmap: `data/function_heatmap.html`

## Universal And Broad Functions

Universal functions recorded in all 18 organizations: None. The closest broad functions are listed below.

Broad functions by organization coverage: M02 Boundary (11/18), M03 Ingestor (9/18), M17 Memory (10/18), S5 System 5 Policy and Identity (13/18)

The strongest near-universal signal is VSM S5 policy/identity rather than a Miller subsystem. It appears in 13/18 organizations, followed by Miller Boundary (11/18), Memory (10/18), and Ingestor (9/18).

## Miller 20 vs VSM 5

- Miller Living Systems records: 53 / 77
- Beer VSM records: 24 / 77

Miller categories are more numerous and carry most observations, especially Boundary, Ingestor, Memory, Reproducer, and Decider. VSM is sparser overall, but S5 Policy and Identity is the single most frequent function, which suggests identity and normative closure are easier to annotate consistently across historical and contemporary organization types than the lower-level VSM control layers.

## Organization-Type Patterns

- 501(c)(3) Nonprofit: M02 Boundary, M03 Ingestor, S5 System 5 Policy and Identity, M19 Encoder
- Cooperative: M03 Ingestor, S5 System 5 Policy and Identity, M01 Reproducer, S3 System 3 Internal Control and Audit
- DAO: M02 Boundary, M17 Memory, M18 Decider, S5 System 5 Policy and Identity
- Guild: M01 Reproducer, M17 Memory, M19 Encoder, S5 System 5 Policy and Identity
- 中世ギルド: M02 Boundary, M13 Channel and Net, S2 System 2 Coordination
- 修道院: M01 Reproducer, S5 System 5 Policy and Identity, M17 Memory, M02 Boundary
- 古代官僚制: M03 Ingestor, M17 Memory, M18 Decider, S1 System 1 Operations
- 家 (Ie): M01 Reproducer, M17 Memory, S5 System 5 Policy and Identity, M03 Ingestor
- 特許貿易会社: M02 Boundary, M03 Ingestor, M06 Producer, M17 Memory
- 狩猟採集バンド: M02 Boundary, M04 Distributor, M18 Decider, S5 System 5 Policy and Identity

Interpretive pattern:

- Monastic organizations concentrate Reproducer, Policy/Identity, Boundary, and Memory. This matches rule-based succession, institutional identity, enclosure or membership boundaries, and textual memory.
- Bureaucratic empires emphasize Ingestor, Memory, Decider, and VSM Operations. They are annotated through extraction, record systems, command authority, and operational administration.
- Ie / house organizations emphasize Reproducer, Memory, and Policy/Identity, reflecting lineage continuity and house-name persistence.
- Nonprofits and DAOs share Boundary, Memory, Decider, and Policy/Identity signals. Contemporary forms make membership, governance, and recorded decision rules especially visible.
- Cooperatives lean toward Ingestor and Policy/Identity, with coordination and internal control appearing where federated or member-accountability mechanisms are explicit.

## Unused And Low-Frequency Functions

Unused functions: M05 Converter, M08 Extruder, M09 Motor, M10 Supporter, M11 Input Transducer, M12 Internal Transducer, M14 Timer, M15 Decoder, M16 Associator, M20 Output Transducer

Low-frequency functions: M04 Distributor (2), M06 Producer (2), M07 Matter-Energy Storage (1), M13 Channel and Net (2), M19 Encoder (2), S3 System 3 Internal Control and Audit (2)

Likely reason: the 18 complete cases were annotated at the institutional-mechanism level, so high-level identity, boundary, memory, reproduction, ingestion, and decision functions are visible. Physical or signal-processing subsystems such as Converter, Extruder, Motor, Input Transducer, Decoder, Associator, and Output Transducer require finer operational evidence than the current organization-level case notes provide.

## Frequency Table

| Function | Framework | Organizations | Records |
| --- | --- | ---: | ---: |
| M01 Reproducer | miller_living_systems | 8 | 8 |
| M02 Boundary | miller_living_systems | 11 | 11 |
| M03 Ingestor | miller_living_systems | 9 | 9 |
| M04 Distributor | miller_living_systems | 2 | 2 |
| M05 Converter | miller_living_systems | 0 | 0 |
| M06 Producer | miller_living_systems | 2 | 2 |
| M07 Matter-Energy Storage | miller_living_systems | 1 | 1 |
| M08 Extruder | miller_living_systems | 0 | 0 |
| M09 Motor | miller_living_systems | 0 | 0 |
| M10 Supporter | miller_living_systems | 0 | 0 |
| M11 Input Transducer | miller_living_systems | 0 | 0 |
| M12 Internal Transducer | miller_living_systems | 0 | 0 |
| M13 Channel and Net | miller_living_systems | 2 | 2 |
| M14 Timer | miller_living_systems | 0 | 0 |
| M15 Decoder | miller_living_systems | 0 | 0 |
| M16 Associator | miller_living_systems | 0 | 0 |
| M17 Memory | miller_living_systems | 10 | 10 |
| M18 Decider | miller_living_systems | 6 | 6 |
| M19 Encoder | miller_living_systems | 2 | 2 |
| M20 Output Transducer | miller_living_systems | 0 | 0 |
| S1 System 1 Operations | beer_vsm | 3 | 3 |
| S2 System 2 Coordination | beer_vsm | 3 | 3 |
| S3 System 3 Internal Control and Audit | beer_vsm | 2 | 2 |
| S4 System 4 Intelligence and Strategy | beer_vsm | 3 | 3 |
| S5 System 5 Policy and Identity | beer_vsm | 13 | 13 |
