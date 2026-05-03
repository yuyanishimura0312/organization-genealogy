# 組織系譜分析 統計クロスタブレポート

- generated_at: 2026-05-03
- database: data/og.db
- table_counts: {"claim": 859, "function_record": 205, "organization": 373, "organization_form_assignment": 104, "relation": 46, "source": 108}

## 1. era × status × longevity_years

| era | status | longevity_years | count |
| --- | --- | --- | --- |
| DAO | active | 0-9 years | 1 |
| プラットフォーム | active | 10-49 years | 3 |
| プラットフォーム | extinct | 10-49 years | 1 |
| 中世ギルド | extinct | 50-99 years | 1 |
| 中世ギルド | extinct | 500+ years | 1 |
| 中世ギルド | extinct | unknown | 1 |
| 修道院 | active | 500+ years | 5 |
| 修道院 | extinct | 500+ years | 1 |
| 修道院 | transformed | unknown | 1 |
| 古代官僚制 | extinct | 100-499 years | 3 |
| 古代官僚制 | extinct | unknown | 3 |
| 古代官僚制 | transformed | 100-499 years | 1 |
| 古代官僚制,神殿経済 | extinct | unknown | 1 |
| 古代官僚制,近代官僚制 | extinct | 100-499 years | 1 |
| 多事業部制 (M-form),系列 | active | 50-99 years | 1 |
| 未分類 | active | 0-9 years | 2 |
| 未分類 | active | 10-49 years | 45 |
| 未分類 | active | 100-499 years | 11 |
| 未分類 | active | 50-99 years | 34 |
| 未分類 | active | 500+ years | 2 |
| 未分類 | active | unknown | 14 |
| 未分類 | extinct | 0-9 years | 4 |
| 未分類 | extinct | 100-499 years | 1 |
| 未分類 | transformed | 100-499 years | 2 |
| 未分類 | unknown | unknown | 226 |
| 氏族・部族,首長制 | active | unknown | 1 |
| 特許貿易会社 | extinct | 100-499 years | 1 |
| 狩猟採集バンド | active | unknown | 1 |
| 産業企業 (U-form) | active | 50-99 years | 1 |
| 系列,財閥 | active | 100-499 years | 1 |
| 近代官僚制 | active | 50-99 years | 2 |

- 最多セルは 未分類 × unknown × unknown の 226 件。
- 開始年がない、または非 active で終了年がない組織は longevity_years を unknown に分類した。

## 2. era × relation_type

| era | relation_type | count |
| --- | --- | --- |
| プラットフォーム | mimetic_isomorphism | 1 |
| プラットフォーム | subsidiary | 1 |
| 中世ギルド | knowledge_transfer | 2 |
| 中世ギルド | mimetic_isomorphism | 2 |
| 修道院 | knowledge_transfer | 2 |
| 修道院 | mimetic_isomorphism | 4 |
| 修道院 | normative_pressure | 2 |
| 修道院 | schism | 1 |
| 修道院 | succession | 2 |
| 古代官僚制 | knowledge_transfer | 5 |
| 古代官僚制 | mimetic_isomorphism | 4 |
| 古代官僚制,神殿経済 | mimetic_isomorphism | 1 |
| 古代官僚制,近代官僚制 | knowledge_transfer | 1 |
| 古代官僚制,近代官僚制 | supply_chain | 1 |
| 未分類 | knowledge_transfer | 4 |
| 未分類 | mimetic_isomorphism | 6 |
| 氏族・部族,首長制 | normative_pressure | 1 |
| 特許貿易会社 | mimetic_isomorphism | 1 |
| 産業企業 (U-form) | mimetic_isomorphism | 1 |
| 系列,財閥 | competition | 1 |
| 系列,財閥 | knowledge_transfer | 1 |
| 近代官僚制 | knowledge_transfer | 1 |
| 近代官僚制 | normative_pressure | 1 |

- 最多セルは 未分類 × mimetic_isomorphism の 6 件。
- relation の era は source_organization_id 側の historical_era 付与から集計した。

## 3. form_taxonomy × organization 件数

| form_taxonomy | organization_count | assignment_count |
| --- | --- | --- |
| historical_era | 32 | 37 |
| legal_form | 23 | 23 |
| mintzberg_1989 | 22 | 24 |
| east_asian | 7 | 11 |
| laloux_2014 | 7 | 7 |
| hannan_freeman | 2 | 2 |

- 最も多く組織に付与されている form_taxonomy は historical_era で 32 組織。
- organization_count は重複 assignment を除いた distinct organization 数。

## 4. function_type × era 件数

| function_type | era | count |
| --- | --- | --- |
| Boundary | DAO | 1 |
| Boundary | プラットフォーム | 4 |
| Boundary | 中世ギルド | 3 |
| Boundary | 修道院 | 3 |
| Boundary | 古代官僚制 | 2 |
| Boundary | 未分類 | 7 |
| Boundary | 氏族・部族,首長制 | 1 |
| Boundary | 特許貿易会社 | 1 |
| Boundary | 狩猟採集バンド | 1 |
| Boundary | 系列,財閥 | 1 |
| Boundary | 近代官僚制 | 1 |
| Channel and Net | プラットフォーム | 1 |
| Channel and Net | 中世ギルド | 1 |
| Channel and Net | 修道院 | 1 |
| Channel and Net | 古代官僚制 | 1 |
| Channel and Net | 未分類 | 1 |
| Converter | 古代官僚制 | 1 |
| Decider | DAO | 1 |
| Decider | プラットフォーム | 3 |
| Decider | 中世ギルド | 1 |
| Decider | 修道院 | 1 |
| Decider | 古代官僚制 | 4 |
| Decider | 古代官僚制,近代官僚制 | 1 |
| Decider | 未分類 | 2 |
| Decider | 氏族・部族,首長制 | 1 |
| Decider | 特許貿易会社 | 1 |
| Decider | 狩猟採集バンド | 1 |
| Decider | 産業企業 (U-form) | 1 |
| Decider | 近代官僚制 | 2 |
| Decoder | プラットフォーム | 1 |
| Decoder | 古代官僚制 | 1 |
| Decoder | 古代官僚制,神殿経済 | 1 |
| Decoder | 近代官僚制 | 1 |
| Distributor | 修道院 | 1 |
| Distributor | 古代官僚制 | 1 |
| Distributor | 古代官僚制,神殿経済 | 1 |
| Distributor | 古代官僚制,近代官僚制 | 1 |
| Distributor | 狩猟採集バンド | 1 |
| Distributor | 近代官僚制 | 1 |
| Encoder | プラットフォーム | 3 |
| Encoder | 古代官僚制 | 2 |
| Encoder | 未分類 | 2 |
| Encoder | 近代官僚制 | 1 |
| Ingestor | プラットフォーム | 1 |
| Ingestor | 中世ギルド | 1 |
| Ingestor | 修道院 | 2 |
| Ingestor | 古代官僚制 | 6 |
| Ingestor | 古代官僚制,神殿経済 | 1 |
| Ingestor | 古代官僚制,近代官僚制 | 1 |
| Ingestor | 未分類 | 6 |
| Ingestor | 特許貿易会社 | 1 |
| Ingestor | 近代官僚制 | 1 |
| Input Transducer | プラットフォーム | 1 |
| Input Transducer | 未分類 | 1 |
| Internal Transducer | 多事業部制 (M-form),系列 | 1 |
| Internal Transducer | 産業企業 (U-form) | 1 |
| Matter-Energy Storage | 中世ギルド | 1 |
| Matter-Energy Storage | 修道院 | 2 |
| Matter-Energy Storage | 古代官僚制,神殿経済 | 1 |
| Memory | DAO | 1 |
| Memory | プラットフォーム | 1 |
| Memory | 中世ギルド | 1 |
| Memory | 修道院 | 4 |
| Memory | 古代官僚制 | 5 |
| Memory | 古代官僚制,神殿経済 | 1 |
| Memory | 古代官僚制,近代官僚制 | 1 |
| Memory | 多事業部制 (M-form),系列 | 1 |
| Memory | 未分類 | 7 |
| Memory | 氏族・部族,首長制 | 1 |
| Memory | 特許貿易会社 | 1 |
| Memory | 系列,財閥 | 1 |
| Output Transducer | 未分類 | 1 |
| Producer | プラットフォーム | 1 |
| Producer | 修道院 | 1 |
| Producer | 古代官僚制 | 2 |
| Producer | 多事業部制 (M-form),系列 | 1 |
| Producer | 未分類 | 1 |
| Producer | 特許貿易会社 | 1 |
| Reproducer | 中世ギルド | 1 |
| Reproducer | 修道院 | 7 |
| Reproducer | 古代官僚制 | 2 |
| Reproducer | 多事業部制 (M-form),系列 | 1 |
| Reproducer | 未分類 | 5 |
| Reproducer | 産業企業 (U-form) | 1 |
| Reproducer | 系列,財閥 | 1 |
| Reproducer | 近代官僚制 | 1 |
| System 1 Operations | 古代官僚制 | 2 |
| System 1 Operations | 特許貿易会社 | 1 |
| System 1 Operations | 産業企業 (U-form) | 1 |
| System 2 Coordination | 中世ギルド | 2 |
| System 2 Coordination | 修道院 | 1 |
| System 2 Coordination | 古代官僚制 | 1 |
| System 2 Coordination | 未分類 | 3 |
| System 2 Coordination | 近代官僚制 | 1 |
| System 3 Internal Control and Audit | 古代官僚制 | 2 |
| System 3 Internal Control and Audit | 古代官僚制,近代官僚制 | 1 |
| System 3 Internal Control and Audit | 多事業部制 (M-form),系列 | 1 |
| System 3 Internal Control and Audit | 未分類 | 1 |
| System 4 Intelligence and Strategy | プラットフォーム | 1 |
| System 4 Intelligence and Strategy | 修道院 | 2 |
| System 4 Intelligence and Strategy | 古代官僚制 | 1 |
| System 4 Intelligence and Strategy | 未分類 | 2 |
| System 4 Intelligence and Strategy | 特許貿易会社 | 1 |
| System 4 Intelligence and Strategy | 近代官僚制 | 2 |
| System 5 Policy and Identity | DAO | 1 |
| System 5 Policy and Identity | プラットフォーム | 4 |
| System 5 Policy and Identity | 中世ギルド | 1 |
| System 5 Policy and Identity | 修道院 | 6 |
| System 5 Policy and Identity | 古代官僚制 | 2 |
| System 5 Policy and Identity | 古代官僚制,神殿経済 | 1 |
| System 5 Policy and Identity | 多事業部制 (M-form),系列 | 1 |
| System 5 Policy and Identity | 未分類 | 10 |
| System 5 Policy and Identity | 氏族・部族,首長制 | 1 |
| System 5 Policy and Identity | 狩猟採集バンド | 1 |
| System 5 Policy and Identity | 産業企業 (U-form) | 1 |
| System 5 Policy and Identity | 系列,財閥 | 1 |
| System 5 Policy and Identity | 近代官僚制 | 1 |

- 最多セルは System 5 Policy and Identity × 未分類 の 10 件。
- function_record は function_type ごとに、対象組織の historical_era で集計した。

## 5. source.redistribution × source_type

| redistribution | source_type | count |
| --- | --- | --- |
| attribution_required | dataset | 1 |
| attribution_required | primary_text | 5 |
| attribution_required | secondary_literature | 54 |
| attribution_required | web | 8 |
| private | dataset | 1 |
| public_redistributable | dataset | 2 |
| public_redistributable | onchain | 1 |
| public_redistributable | primary_text | 9 |
| public_redistributable | secondary_literature | 2 |
| public_redistributable | web | 5 |
| restricted | primary_text | 1 |
| restricted | secondary_literature | 19 |

- 最多セルは attribution_required × secondary_literature の 54 件。
- redistribution が NULL の source は 未設定 として集計した。

## 6. claim.value_kind × entity_type

| value_kind | entity_type | count |
| --- | --- | --- |
| inapplicable | organization | 1 |
| partial | activity | 3 |
| partial | event | 7 |
| partial | function_record | 1 |
| partial | impact_record | 2 |
| partial | organization | 18 |
| partial | organization_form_assignment | 47 |
| partial | relation | 39 |
| present | activity | 4 |
| present | event | 1 |
| present | function_record | 1 |
| present | impact_record | 2 |
| present | organization | 684 |
| present | organization_form_assignment | 14 |
| present | organization_temporal_facet | 28 |
| present | relation | 7 |

- 最多セルは present × organization の 684 件。
- claim は value_kind と entity_type の組み合わせ別に使用パターンを数えた。

## 総合的な発見

1. historical_era 未分類は 341/373 組織で、時代分類はまだ一部のケースに偏っている。
2. longevity_years unknown は 248/373 組織で、寿命分析の主な制約になっている。
3. relation_type は mimetic_isomorphism が最多で 20/46 関係を占める。
4. public_redistributable source は 19/108 件で、再配布可能な出典は少数派。
5. claim.value_kind は present が 741/859 件で中心的に使われている。
