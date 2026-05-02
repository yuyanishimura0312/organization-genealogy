# 組織データベース概念データモデル草案

## 設計原則（6 項目）

1. 組織を固定的な実体ではなく、時点ごとに観測される状態の束として扱う。
2. 「特徴」「機能」「活動」「インパクト」を分離し、同じ組織型でも異なる働きや影響を記録できるようにする。
3. すべての記述を claim として扱い、出典、確度、解釈者、記録時点を紐づける。
4. ノードとしての組織と、エッジとしての組織間関係を同等に扱い、関係にも期間・強度・根拠を持たせる。
5. PostgreSQL の正規化テーブルで検索可能性を確保しつつ、時代・地域・研究領域ごとの差異は JSONB で吸収する。
6. 将来の graph DB、特徴ベクトル、系統推定に転用できるよう、ID、時系列、分類、特徴量の境界を明確に保つ。

## エンティティ定義

### Organization（コア属性 / temporal facet / 出典）

組織ノードの最小単位。バンド、部族、神殿経済、修道院、ギルド、国家機関、企業、DAO などを同じ枠で扱う。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `organization_id` | UUID | 内部 ID |
| `canonical_name` | text | 代表名称 |
| `alternate_names` | jsonb | 別名、現地語名、翻訳名 |
| `description` | text | 簡潔な説明 |
| `primary_form_id` | UUID | 主分類への参照 |
| `geo_scope` | jsonb | 地域、移動範囲、拠点、境界の曖昧性 |
| `start_date` | date / nullable | 推定開始日 |
| `end_date` | date / nullable | 推定終了日 |
| `date_precision` | text | `exact`, `year`, `century`, `period`, `unknown` など |
| `status` | text | `active`, `dormant`, `transformed`, `merged`, `extinct`, `unknown` |
| `attributes` | jsonb | 規模、成員資格、統治形態、所有形態などの可変属性 |
| `embedding` | vector / nullable | 将来の pgvector 用 |
| `created_at` | timestamptz | 作成日時 |
| `updated_at` | timestamptz | 更新日時 |

Temporal facet:

| field | type | 説明 |
| --- | --- | --- |
| `organization_facet_id` | UUID | 状態記録 ID |
| `organization_id` | UUID | Organization 参照 |
| `valid_from` | date / nullable | 状態の有効開始 |
| `valid_to` | date / nullable | 状態の有効終了 |
| `facet_type` | text | `membership`, `governance`, `resource_base`, `territory`, `technology`, `identity` など |
| `facet_value` | jsonb | 状態の内容 |
| `confidence` | numeric | 0.0-1.0 の確度 |
| `claim_id` | UUID | 出典つき主張への参照 |

出典:

Organization 本体に出典を直付けせず、`Claim` または `SourceAssertion` 中間テーブルを通じて、各フィールド単位または facet 単位で Source と結びつける。

### OrganizationForm（型分類）

組織型の分類体系。単一階層に固定せず、複数分類体系を併存させる。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `form_id` | UUID | 型 ID |
| `taxonomy_name` | text | 分類体系名 |
| `form_code` | text | 安定したコード |
| `label` | text | 表示名 |
| `parent_form_id` | UUID / nullable | 上位分類 |
| `definition` | text | 分類の定義 |
| `criteria` | jsonb | 判定基準 |
| `valid_period` | daterange / nullable | 分類が有効な時代範囲 |
| `notes` | text | 注意点 |

補助テーブル:

| table | 用途 |
| --- | --- |
| `organization_form_assignment` | Organization と OrganizationForm の多対多対応。期間、確度、根拠を持つ |

### Activity（活動・事業領域 / temporal）

組織が何をしているかを表す。生業、交易、儀礼、軍事、教育、金融、行政、ソフトウェア開発、プラットフォーム運営などを同じ構造で扱う。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `activity_id` | UUID | 活動 ID |
| `organization_id` | UUID | Organization 参照 |
| `activity_type` | text | 活動分類 |
| `domain` | text | 生産、交換、統治、儀礼、知識、ケア、軍事など |
| `description` | text | 活動内容 |
| `inputs` | jsonb | 資源、労働、知識、資本、データなど |
| `outputs` | jsonb | 財、サービス、規範、知識、権力、ネットワークなど |
| `valid_from` | date / nullable | 有効開始 |
| `valid_to` | date / nullable | 有効終了 |
| `scale` | jsonb | 規模、頻度、参加者数、取引量など |
| `confidence` | numeric | 確度 |
| `claim_id` | UUID | 根拠 |

### Function（機能：資源動員・調整・知識継承 etc）

活動の背後にある社会的・組織的機能を記録する。活動が「何をしたか」、Function は「何の機能を果たしたか」。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `function_id` | UUID | 機能 ID |
| `organization_id` | UUID | Organization 参照 |
| `function_type` | text | `resource_mobilization`, `coordination`, `risk_pooling`, `knowledge_transmission`, `legitimation`, `boundary_maintenance`, `innovation`, `conflict_resolution` など |
| `mechanism` | jsonb | 機能を実現する仕組み |
| `beneficiaries` | jsonb | 受益者、対象集団 |
| `dependency` | jsonb | 前提となる資源、制度、技術 |
| `valid_from` | date / nullable | 有効開始 |
| `valid_to` | date / nullable | 有効終了 |
| `confidence` | numeric | 確度 |
| `claim_id` | UUID | 根拠 |

### ImpactRecord（インパクト指標 / 影響範囲 / 評価方法）

組織が外部環境、成員、制度、技術、文化、生態系に与えた影響を記録する。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `impact_id` | UUID | インパクト ID |
| `organization_id` | UUID | Organization 参照 |
| `impact_domain` | text | 経済、政治、文化、技術、環境、人口、知識など |
| `metric_name` | text | 指標名 |
| `metric_value` | jsonb | 数値、カテゴリ、範囲、推定値 |
| `direction` | text | `positive`, `negative`, `mixed`, `uncertain`, `descriptive` |
| `affected_scope` | jsonb | 地理範囲、人口範囲、制度範囲 |
| `evaluation_method` | text | 比較、定量推定、専門家評価、史料解釈など |
| `time_horizon` | text | 短期、中期、長期、世代間など |
| `valid_from` | date / nullable | 影響開始 |
| `valid_to` | date / nullable | 影響終了 |
| `confidence` | numeric | 確度 |
| `claim_id` | UUID | 根拠 |

### Relation（組織間関係 / 種別 / 期間 / 強度）

組織間エッジ。支配、従属、同盟、競争、分派、継承、模倣、資源交換、資本関係、プロトコル依存などを扱う。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `relation_id` | UUID | 関係 ID |
| `source_organization_id` | UUID | 起点組織 |
| `target_organization_id` | UUID | 終点組織 |
| `relation_type` | text | `alliance`, `competition`, `control`, `membership`, `succession`, `spin_off`, `merger`, `trade`, `funding`, `knowledge_transfer`, `protocol_dependency` など |
| `directionality` | text | `directed`, `undirected`, `bidirectional` |
| `valid_from` | date / nullable | 関係開始 |
| `valid_to` | date / nullable | 関係終了 |
| `strength` | numeric / nullable | 0.0-1.0 の強度 |
| `strength_basis` | text | 強度の評価根拠 |
| `relation_attributes` | jsonb | 関係固有の属性 |
| `confidence` | numeric | 確度 |
| `claim_id` | UUID | 根拠 |

Graph DB 展開時は Organization を node、Relation を relationship として移行しやすい構造にする。

### Source（典拠 / 信頼度）

文献、一次史料、データベース、インタビュー、考古学的記録、Web アーカイブ、オンチェーンデータなどの典拠。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `source_id` | UUID | 出典 ID |
| `source_type` | text | `primary_text`, `secondary_literature`, `dataset`, `interview`, `archive`, `artifact`, `onchain`, `web` など |
| `title` | text | タイトル |
| `authors` | jsonb | 著者、編者、組織 |
| `publication_date` | date / nullable | 公開日 |
| `publisher` | text / nullable | 出版者 |
| `locator` | jsonb | ページ、章、URL、DOI、アーカイブ ID など |
| `accessed_at` | date / nullable | 参照日 |
| `reliability_score` | numeric | 0.0-1.0 の信頼度 |
| `reliability_basis` | text | 信頼度判断の理由 |
| `bias_notes` | text | 立場、欠落、解釈上の注意 |

Claim / SourceAssertion:

| field | type | 説明 |
| --- | --- | --- |
| `claim_id` | UUID | 主張 ID |
| `entity_type` | text | 対象テーブル名 |
| `entity_id` | UUID | 対象レコード ID |
| `field_path` | text | `attributes.membership_size` など |
| `claim_value` | jsonb | 主張内容 |
| `source_id` | UUID | Source 参照 |
| `confidence` | numeric | 主張ごとの確度 |
| `interpretation_note` | text | 解釈上の補足 |
| `recorded_by` | text | 記録者 |
| `recorded_at` | timestamptz | 記録日時 |

### Event（組織イベント / 設立・統合・分裂・消滅 etc）

組織の状態変化を表すイベント。Organization facet や Relation の更新理由としても使う。

主要フィールド案:

| field | type | 説明 |
| --- | --- | --- |
| `event_id` | UUID | イベント ID |
| `event_type` | text | `founding`, `dissolution`, `merger`, `split`, `renaming`, `relocation`, `reform`, `crisis`, `platform_shift`, `governance_change` など |
| `event_date` | date / nullable | 発生日 |
| `date_precision` | text | 日付精度 |
| `description` | text | イベント説明 |
| `participants` | jsonb | 関与組織、人物、集団 |
| `causes` | jsonb | 原因、背景 |
| `outcomes` | jsonb | 結果、生成・消滅した組織や関係 |
| `location` | jsonb | 地点・地域 |
| `confidence` | numeric | 確度 |
| `claim_id` | UUID | 根拠 |

補助テーブル:

| table | 用途 |
| --- | --- |
| `event_organization` | Event と Organization の多対多対応。役割は `founder`, `successor`, `merged_into`, `splinter`, `affected` など |
| `event_relation` | Event と Relation の対応。関係の開始・終了・強度変化を記録 |

## ER 図（テキストで関係を表現）

```text
Organization 1 --- N OrganizationTemporalFacet
Organization N --- N OrganizationForm
Organization 1 --- N Activity
Organization 1 --- N Function
Organization 1 --- N ImpactRecord
Organization 1 --- N Relation(source_organization_id)
Organization 1 --- N Relation(target_organization_id)

Event N --- N Organization
Event N --- N Relation

Source 1 --- N Claim
Claim N --- 1 Organization / OrganizationTemporalFacet / OrganizationFormAssignment
Claim N --- 1 Activity / Function / ImpactRecord / Relation / Event

OrganizationForm 1 --- N OrganizationForm(parent_form_id)
OrganizationForm 1 --- N OrganizationFormAssignment
Organization 1 --- N OrganizationFormAssignment
```

PostgreSQL では polymorphic な `Claim.entity_type + entity_id` を採用するか、厳密な外部キー制約を優先して対象別 claim table に分ける。v0.1 では前者で柔軟性を優先し、v1.0 で高頻度対象のみ専用中間テーブル化する。

## 拡張: 個体群（population）レベル集計、進化系統推定向けの特徴ベクトル

Population 集計:

| field | type | 説明 |
| --- | --- | --- |
| `population_id` | UUID | 個体群 ID |
| `population_name` | text | 集計単位名 |
| `selection_criteria` | jsonb | 時代、地域、組織型、活動、機能などの抽出条件 |
| `time_window` | daterange | 集計期間 |
| `aggregation_method` | text | 件数、比率、分布、ネットワーク指標など |
| `summary_metrics` | jsonb | 集計結果 |
| `claim_id` | UUID | 根拠 |

特徴ベクトル:

| feature group | 例 |
| --- | --- |
| `form_features` | 階層性、成員境界、法的形式、所有形態 |
| `governance_features` | 意思決定集中度、代表制、合意形成方式 |
| `resource_features` | 労働、土地、資本、データ、信仰、武力への依存 |
| `activity_features` | 生産、交易、教育、儀礼、金融、プラットフォーム運営 |
| `function_features` | 調整、動員、知識継承、リスク分散、正統化 |
| `network_features` | 中心性、関係密度、依存関係、分派数 |
| `impact_features` | 影響範囲、持続期間、制度変化、技術拡散 |

実装案:

- `organization_feature_vector` テーブルを作り、`organization_id`, `valid_from`, `valid_to`, `feature_schema_version`, `features_jsonb`, `embedding` を持たせる。
- 系統推定では Event の `split`, `merger`, `succession`, Relation の `knowledge_transfer`, `spin_off`, `protocol_dependency` を候補エッジとして使う。
- Neo4j では Organization, Event, Form を node、Relation, PARTICIPATED_IN, HAS_FORM, GENERATED_BY を relationship に対応させる。
- vector store では `description`, `attributes`, `activities`, `functions`, `impact_records`, `source notes` を用途別に embedding 化し、類似組織検索と仮説生成に使う。

## 段階的実装ロードマップ（v0.1 → v1.0）

### v0.1: 最小入力モデル

- `organization`, `organization_form`, `organization_form_assignment`, `source`, `claim` を作る。
- `attributes jsonb` と `claim` により、曖昧な歴史記述を失わず入力できる状態にする。
- 日付精度と確度を必須化し、確定日付だけを前提にしない。

### v0.2: 活動・機能・インパクトの分離

- `activity`, `function`, `impact_record` を追加する。
- Activity と Function の混同を避けるため、入力 UI または import script で別フィールドとして扱う。
- `impact_domain`, `evaluation_method`, `affected_scope` を標準化する。

### v0.3: 関係とイベント

- `relation`, `event`, `event_organization`, `event_relation` を追加する。
- 分裂、統合、継承、支配、資源交換を関係とイベントの両方から辿れるようにする。
- Relation の `strength` は必須にせず、根拠がある場合のみ記録する。

### v0.5: temporal facet の本格化

- `organization_temporal_facet` を追加し、統治、規模、資源基盤、領域、技術基盤の時系列変化を記録する。
- 同一組織の長期変化と、別組織への変換を Event で区別する。
- 期間が重なる facet を許容し、矛盾は Claim の確度と出典で管理する。

### v0.7: 集計・比較分析

- `population`, `population_membership`, `population_metric` を追加する。
- 時代、地域、組織型、機能別の集計を保存し、再計算可能な `selection_criteria` を残す。
- ネットワーク指標や多様性指標を `summary_metrics jsonb` に格納する。

### v1.0: graph / vector 展開

- `organization_feature_vector` を追加し、特徴量スキーマを version 管理する。
- Neo4j export 用に node / edge の安定 ID と relation type mapping を固定する。
- pgvector または外部 vector store 用に embedding 生成対象、再生成条件、モデル名、生成日時を記録する。
- Claim と Source の粒度を見直し、頻出フィールドには専用制約と index を追加する。
