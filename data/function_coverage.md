# Function Taxonomy Coverage

Generated from `data/og.db` using `etl/13_function_heatmap.py`.

Provenance: `{claim: function taxonomy distribution, source_url: local:data/og.db, retrieval_date: 2026-05-03, confidence: high}`

## Scope

- Annotated organizations: 43
- Function types: 25
- Function records counted: 205
- HTML heatmap: `data/function_heatmap.html`

## Universal And Broad Functions

Universal functions recorded in all 43 organizations: None. The closest broad functions are listed below.

Broad functions by organization coverage: M02 Boundary (25/43), M17 Memory (25/43), S5 System 5 Policy and Identity (31/43)

The strongest near-universal signal is VSM S5 policy/identity rather than a Miller subsystem. It appears in 31/43 organizations, followed by Miller Boundary (25/43), Memory (25/43), and Ingestor (20/43).

## Miller 20 vs VSM 5

- Miller Living Systems records: 148 / 205
- Beer VSM records: 57 / 205

Miller categories are more numerous and carry most observations, especially Boundary, Ingestor, Memory, Reproducer, and Decider. VSM is sparser overall, but S5 Policy and Identity is the single most frequent function, which suggests identity and normative closure are easier to annotate consistently across historical and contemporary organization types than the lower-level VSM control layers.

## Organization-Type Patterns

- (none): M02 Boundary, M11 Input Transducer, M17 Memory, M19 Encoder
- 501(c)(3) Nonprofit: M02 Boundary, M03 Ingestor, S5 System 5 Policy and Identity, M19 Encoder
- Cooperative: M03 Ingestor, S5 System 5 Policy and Identity, M01 Reproducer, M06 Producer
- DAO: M02 Boundary, M17 Memory, M18 Decider, S5 System 5 Policy and Identity
- Guild: M01 Reproducer, M17 Memory, S5 System 5 Policy and Identity, M02 Boundary
- Missionary: M02 Boundary, S5 System 5 Policy and Identity, M06 Producer, M01 Reproducer
- Monastic Order: M01 Reproducer, M13 Channel and Net, M17 Memory, S4 System 4 Intelligence and Strategy
- Waqf: M01 Reproducer, M03 Ingestor, S5 System 5 Policy and Identity, M04 Distributor
- アメーバ経営 (Inamori Amoeba Management): M01 Reproducer, M12 Internal Transducer, M18 Decider, S1 System 1 Operations
- プラットフォーム: M02 Boundary, M18 Decider, S5 System 5 Policy and Identity, M19 Encoder
- 中世ギルド: M02 Boundary, M13 Channel and Net, S2 System 2 Coordination
- 会合衆 (日本中世自治都市の評議会): M02 Boundary, M03 Ingestor, M18 Decider, S2 System 2 Coordination
- 修道院: M01 Reproducer, S5 System 5 Policy and Identity, M17 Memory, M02 Boundary
- 古代官僚制: M03 Ingestor, M17 Memory, M18 Decider, S3 System 3 Internal Control and Audit
- 商幫 (中国同郷商人連合): M02 Boundary, M13 Channel and Net, M17 Memory, S2 System 2 Coordination
- 家 (Ie): M01 Reproducer, M17 Memory, S5 System 5 Policy and Identity, M03 Ingestor
- 株式会社 (KK): M01 Reproducer, M06 Producer, M12 Internal Transducer, M17 Memory
- 氏族・部族: M02 Boundary, M17 Memory, M18 Decider, S5 System 5 Policy and Identity
- 特許貿易会社: M02 Boundary, M03 Ingestor, M06 Producer, M17 Memory
- 狩猟採集バンド: M02 Boundary, M04 Distributor, M18 Decider, S5 System 5 Policy and Identity
- 神殿経済: M03 Ingestor, M04 Distributor, M07 Matter-Energy Storage, M15 Decoder
- 近代官僚制: M18 Decider, S4 System 4 Intelligence and Strategy, M01 Reproducer, M03 Ingestor
- 郷約 (ベトナム村落規約): M02 Boundary, M17 Memory, S2 System 2 Coordination, S5 System 5 Policy and Identity
- 門中 (朝鮮): M01 Reproducer, M02 Boundary, M17 Memory, S5 System 5 Policy and Identity

Interpretive pattern:

- Monastic organizations concentrate Reproducer, Policy/Identity, Boundary, and Memory. This matches rule-based succession, institutional identity, enclosure or membership boundaries, and textual memory.
- Bureaucratic empires emphasize Ingestor, Memory, Decider, and VSM Operations. They are annotated through extraction, record systems, command authority, and operational administration.
- Ie / house organizations emphasize Reproducer, Memory, and Policy/Identity, reflecting lineage continuity and house-name persistence.
- Nonprofits and DAOs share Boundary, Memory, Decider, and Policy/Identity signals. Contemporary forms make membership, governance, and recorded decision rules especially visible.
- Cooperatives lean toward Ingestor and Policy/Identity, with coordination and internal control appearing where federated or member-accountability mechanisms are explicit.

## Unused And Low-Frequency Functions

Unused functions: M08 Extruder, M09 Motor, M10 Supporter, M14 Timer, M16 Associator

Low-frequency functions: M05 Converter (1), M11 Input Transducer (2), M12 Internal Transducer (2), M20 Output Transducer (1)

Likely reason: the 18 complete cases were annotated at the institutional-mechanism level, so high-level identity, boundary, memory, reproduction, ingestion, and decision functions are visible. Physical or signal-processing subsystems such as Converter, Extruder, Motor, Input Transducer, Decoder, Associator, and Output Transducer require finer operational evidence than the current organization-level case notes provide.

## Frequency Table

| Function | Framework | Organizations | Records |
| --- | --- | ---: | ---: |
| M01 Reproducer | miller_living_systems | 19 | 19 |
| M02 Boundary | miller_living_systems | 25 | 25 |
| M03 Ingestor | miller_living_systems | 20 | 20 |
| M04 Distributor | miller_living_systems | 6 | 6 |
| M05 Converter | miller_living_systems | 1 | 1 |
| M06 Producer | miller_living_systems | 7 | 7 |
| M07 Matter-Energy Storage | miller_living_systems | 4 | 4 |
| M08 Extruder | miller_living_systems | 0 | 0 |
| M09 Motor | miller_living_systems | 0 | 0 |
| M10 Supporter | miller_living_systems | 0 | 0 |
| M11 Input Transducer | miller_living_systems | 2 | 2 |
| M12 Internal Transducer | miller_living_systems | 2 | 2 |
| M13 Channel and Net | miller_living_systems | 5 | 5 |
| M14 Timer | miller_living_systems | 0 | 0 |
| M15 Decoder | miller_living_systems | 4 | 4 |
| M16 Associator | miller_living_systems | 0 | 0 |
| M17 Memory | miller_living_systems | 25 | 25 |
| M18 Decider | miller_living_systems | 19 | 19 |
| M19 Encoder | miller_living_systems | 8 | 8 |
| M20 Output Transducer | miller_living_systems | 1 | 1 |
| S1 System 1 Operations | beer_vsm | 4 | 4 |
| S2 System 2 Coordination | beer_vsm | 8 | 8 |
| S3 System 3 Internal Control and Audit | beer_vsm | 5 | 5 |
| S4 System 4 Intelligence and Strategy | beer_vsm | 9 | 9 |
| S5 System 5 Policy and Identity | beer_vsm | 31 | 31 |
