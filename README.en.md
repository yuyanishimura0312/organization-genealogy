# Organization Genealogy Analysis

Organization Genealogy Analysis is a long-range comparative research project that treats organizations as living units: not as firms by default, and not as literal organisms, but as historical units that maintain boundaries, mobilize resources, process information, reproduce forms, go dormant, revive, split, merge, and disappear.

The project compares bands, lineages, monasteries, waqf, guilds, state agencies, corporations, platforms, and DAOs on the same analytical surface. Its core rule is claim-first modeling: every substantive statement should be recorded as a sourced claim with confidence, interpretation context, and provenance.

## Theoretical Position

The primary frame is Hannan and Freeman's population ecology of organizations. It gives the project a workable comparative unit: organizational individuals, populations, niches, founding, mortality, density, legitimacy, and selection.

Luhmann, Beer, and DiMaggio-Powell are auxiliary frames:

- Luhmann helps analyze organizational boundary, decision, communication, and self-reproduction without reducing organizations to people or legal shells.
- Beer helps operationalize viability, coordination, feedback, autonomy, intelligence, and policy through the Viable System Model.
- DiMaggio and Powell help prevent efficiency-only explanations by foregrounding mimetic, normative, and coercive institutional pressures.

Spencer is treated critically. His organismic social theory is useful as a historical warning about reification, progress narratives, functionalism, and teleological evolution, not as the main analytic tool.

## Five Traps To Avoid

1. Reification: treating an organization or society as if it were a literal living body.
2. Circular survivalism: calling a surviving organization adaptive, then using survival as the proof of adaptation.
3. Ambiguous individual boundaries: assuming legal personality, membership, assets, decision boundaries, brands, and communication boundaries always coincide.
4. Functionalist hindsight: explaining institutions by their visible current function while ignoring authority, legitimacy, coercion, accident, and imitation.
5. Over-importing biology: moving concepts such as selection, evolution, niche, self-organization, adaptation, immunity, metabolism, reproduction, and death into organizational analysis without limiting the analogy.

## Data Summary

Current project snapshot:

| Metric | Count |
| --- | ---: |
| Organizations | 348 |
| Claims | 374 |
| Fully annotated cases | 18 |
| Relations | 16 |
| Network components | 3 |

These counts are the only dataset-level counts used in this English README. See `docs/data_dictionary.md` for schema details.

## Schema Overview

The SQLite sandbox schema is claim-based and organized around four layers:

| Layer | Tables | Purpose |
| --- | --- | --- |
| Provenance | `source`, `claim` | Store source metadata and field-level claims. |
| Organizational units and forms | `organization`, `organization_form`, `organization_form_assignment`, `organization_temporal_facet` | Represent organizations, typologies, assignments, and time-bounded facets. |
| Activity, function, impact | `activity`, `function_type`, `function_record`, `impact_record` | Separate what an organization does, what living-system function it performs, and what changes it produces. |
| Change and network | `relation`, `event`, `event_organization`, `event_relation`, `dormancy_record` | Represent inter-organizational edges, state transitions, and dormancy/revival cycles. |

The central integration pattern is `claim.entity_type + claim.entity_id`. Some tables also carry a direct `claim_id` for records whose existence or value is supported by a specific claim.

The claim value vocabulary is intentionally five-valued: `present`, `absent`, `partial`, `unknown`, and `inapplicable`. This keeps absence, missing data, partial presence, and non-applicability separate.

## License Plan

The planned license structure is:

- Research notes: CC BY 4.0.
- Code and SQL: MIT.
- Data: governed by the licenses of underlying sources, with public release limited to records that can be rebuilt from redistributable sources.

The final release license will be fixed at the public release stage.

## Citation

Preferred citation placeholder:

> Nishimura, Yuya. Organization Genealogy Analysis: Organization Genealogy as Living Systems. NPO Miratuku, in progress.

## Contributing

Contribution guidelines are not finalized. Planned requirements:

- Add or revise data through sourced claims.
- Do not add unsourced analytical assertions.
- Preserve the distinction between `present`, `absent`, `partial`, `unknown`, and `inapplicable`.
- Respect source redistribution constraints.
- Keep theoretical claims tied to the relevant research notes or external sources.
