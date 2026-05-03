# Decision Log

This log records accepted project decisions that are evidenced in the repository as of 2026-05-03. Future gates are listed only as placeholders until a decision is recorded.

## Gate 0: Theory

### ADR-001: Use organizational ecology as the primary theory

Status: accepted

Context:
The synthesis of codex1 and the broader research streams found that the "organization as life" metaphor splits into multiple lineages: Spencer's organism analogy, Hannan-Freeman organizational ecology, Maturana-Luhmann autopoiesis, and Beer cybernetics. The roadmap defines Gate 0 as the point where primary theory, auxiliary theory, and avoided narratives are fixed.

Decision:
Use Hannan-Freeman organizational ecology as the primary theory for population, founding, dissolution, inertia, and form-level comparison.

Consequences:
The project treats organizations as populations and forms rather than as literal organisms. Founding, dissolution, schism, succession, and reorganization are recorded as events that can later support ecology-style analysis. Phase 3 has event/relation data, but density, founding-rate, and mortality-rate tests are not yet possible.

References:
- `plan/synthesis.md` lines 16-27
- `plan/phase1_complete.md` lines 83-89
- `plan/phase3_complete.md` lines 171-173
- `research/codex1_theory_critique.md`

### ADR-002: Treat Spencer as a critical target

Status: accepted

Context:
codex1 and the synthesis identify Spencer's organism analogy as one of the four lineages behind the life metaphor, but also identify risks around reification, circular survival stories, boundary ambiguity, functionalist hindsight, and over-importing biology.

Decision:
Do not adopt Spencer's organism analogy as an explanatory frame. Use it as a critique target and as a checklist against progress narratives and literal organism metaphors.

Consequences:
Diagrams and prose must avoid implying that organizations are biological organisms. Survival is not treated as evidence of adaptation. Phase 3 explicitly evaluates reification, circular survival, boundary ambiguity, functionalist hindsight, and biological over-import as current risks.

References:
- `plan/synthesis.md` lines 16-20
- `plan/phase1_complete.md` lines 83-89
- `plan/phase3_complete.md` lines 161-169
- `research/codex1_theory_critique.md`

### ADR-003: Use institutional theory and resource dependence as corrective lenses

Status: accepted

Context:
A pure ecology or efficiency-selection story risks explaining all survival as adaptation. The synthesis records DiMaggio-Powell isomorphism in `relation_type`, and Phase 3 reports that contemporary relations are often mimetic rather than direct inheritance.

Decision:
Use institutional theory and resource dependence as corrective lenses. Encode institutional mechanisms in relations and treat legitimacy, dependency, and resource conditions as factors distinct from survival.

Consequences:
`relation_type` includes institutional isomorphism categories. Contemporary genealogy can record mimetic similarity and legitimacy signals without overstating direct causal inheritance. Phase 4 must further separate resource base, legitimacy, competition, and boundary facets.

References:
- `plan/synthesis.md` lines 22-24
- `plan/roadmap.md` lines 340-345
- `plan/phase3_complete.md` lines 183-185
- `research/L_institutional_power.md`

## Gate 1: Data

### ADR-004: Develop in a SQLite sandbox and target PostgreSQL for production

Status: accepted

Context:
The initial DDL was designed for PostgreSQL 16 with pgvector. Phase 1 then created a SQLite-compatible sandbox for local iteration, preserving the v0.1-v0.3 model with compatibility changes.

Decision:
Use SQLite for the development sandbox and keep PostgreSQL as the production target.

Consequences:
Local ETL and pilot analysis run against `data/og.db` using `sql/schema_sqlite_v01.sql`. PostgreSQL-specific features such as `vector`, `daterange`, BRIN/GIN/HNSW indexes, and richer constraints remain production concerns. Phase 4 includes PostgreSQL migration preparation.

References:
- `plan/synthesis.md` lines 35-40 and 77-80
- `plan/phase1_status.md` lines 7-17
- `plan/phase3_complete.md` lines 123-140
- `sql/schema_sqlite_v01.sql`
- `research/codex4_ddl_v01.sql`

### ADR-005: Use five claim.value_kind states

Status: accepted

Context:
Stream J's Seshat warning showed that treating missing values as absence can corrupt analysis. The synthesis records the NA-to-absent problem and requires a five-state value kind.

Decision:
Represent claim values as `present`, `absent`, `partial`, `unknown`, and `inapplicable`.

Consequences:
Claims distinguish unknown from absent and inapplicable. Wikidata dissolution-date gaps remain `unknown` rather than being converted into active or absent states. ETL and schema validation must preserve this distinction.

References:
- `plan/synthesis.md` lines 20-24
- `plan/phase1_status.md` lines 7-10
- `plan/phase1_complete.md` lines 49-64
- `plan/phase3_complete.md` lines 137-138
- `research/codex4_ddl_v01.sql` lines 5-12
- `sql/schema_sqlite_v01.sql` lines 12-17 and 45-63

### ADR-006: Use ROR as the primary academic-institution source and Wikidata as a complement

Status: accepted

Context:
Phase 1 reached 335 pilot organizations: 100 from ROR, 230 from typed Wikidata queries, and 5 fully annotated representative cases. Wikidata subclass expansion produced noisy results, while ROR is narrower and lower risk for academic organizations.

Decision:
Use ROR as the main source for academic institutions. Use Wikidata as a complementary broad seed source, subject to depth limits, confidence adjustment, cross-checking, and manual curation.

Consequences:
Academic-institution intake can rely on ROR for cleaner identifiers and metadata. Wikidata remains useful for broad historical and organizational coverage, but its records are not treated as authoritative classification without claim confidence and curation.

References:
- `plan/phase1_complete.md` lines 12-20 and 51-64
- `plan/phase1_complete.md` lines 76-80 and 83-89
- `plan/synthesis.md` lines 24 and 39-40
- `etl/06_ror_pilot.py`
- `research/codex5_wikidata_sparql.md`

## Gate 2: Schema

### ADR-007: Do not make the legal corporation the default organization type

Status: accepted

Context:
codex2 defines Organization as a common frame for bands, tribes, temple economies, monasteries, guilds, state agencies, firms, and DAOs. The DDL records an explicit principle that legal corporations must not be the default type.

Decision:
Model legal corporations, houses, lineages, monasteries, guilds, states, foundations, and DAOs as comparable organizations without making the corporation the standard form.

Consequences:
Organization form is handled through classification and assignment tables, not by making legal form the schema root. Phase 1 verified non-modern-corporate cases, while Phase 2/4 must continue increasing East Asian and non-corporate coverage.

References:
- `research/codex2_data_model.md` lines 14-35
- `research/codex4_ddl_v01.sql` lines 5-12
- `plan/phase1_complete.md` lines 8-13 and 83-89
- `plan/phase3_complete.md` lines 60-62

### ADR-008: Use 25 master function types with extendable sub-functions

Status: accepted

Context:
codex7 produced a machine-readable taxonomy where Miller's 20 critical subsystems and Beer's VSM S1-S5 are the 25 master functions. Extension examples preserve the master enum while adding concrete sub-functions.

Decision:
Use 25 master `function_type` values as the canonical function taxonomy and allow sub-function extensions without altering the master set.

Consequences:
Cross-era comparison uses a stable master vocabulary. Detailed domain-specific functions can be added as extensions while preserving comparability. VSR, dynamic capabilities, and exploration/exploitation are treated as temporal or cross-cutting axes, not additional master functions.

References:
- `plan/synthesis.md` lines 22 and 35-40
- `plan/phase1_status.md` lines 13-17
- `research/codex7_function_taxonomy.json`
- `research/codex7_extension_examples.json`
- `research/codex4_ddl_v02.sql` lines 35-55

### ADR-009: Implement temporal facets in v0.5 and use event-based modeling in v0.3

Status: accepted

Context:
codex2 planned relation and event tables for v0.3, with full temporal facets deferred to v0.5. Phase 3 completed event/relation-based modeling and identifies temporal facets as the next step.

Decision:
Use event and relation modeling for v0.3. Defer full `organization_temporal_facet` modeling to v0.5.

Consequences:
The current schema captures founding, dissolution, split, merger, reform, crisis, and relation evidence without prematurely modeling every time-varying attribute. Phase 4/v0.5 must add facets such as governance, resource base, territory, membership, identity, technology, and boundary.

References:
- `research/codex2_data_model.md` lines 297-307
- `plan/phase3_complete.md` lines 42-48 and 123-140
- `sql/schema_sqlite_v01.sql` lines 221-321
- `sql/schema_sqlite_v05_temporal_facet.sql`

## Gate 3: Classification

Placeholder: no accepted ADR yet.

Gate 3 will decide classification stability, relation to existing classifications, and expert interpretability. The gate is defined in `plan/roadmap.md` lines 321-326, but no repository-backed classification decision has been accepted yet.

## Gate 4: Genealogy

Placeholder: no accepted ADR yet.

Gate 4 will decide edge evidence, duration, confidence, and causal-claim strength. Phase 3 created a genealogy snapshot, but its low-confidence relation audit is explicitly deferred to Phase 4 rather than accepted as a final gate decision.

References:
- `plan/roadmap.md` lines 321-326
- `plan/phase3_complete.md` lines 132-157 and 187-189

## Gate 5: Publication

Placeholder: no accepted ADR yet.

Gate 5 will decide licensing, GDPR, Indigenous Data Sovereignty, commercial database conditions, and stigmatization risks. The gate is defined in `plan/roadmap.md` lines 321-326, but no publication decision has been accepted yet.
