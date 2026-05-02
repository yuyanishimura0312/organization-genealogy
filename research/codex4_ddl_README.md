# DDL v0.1 / v0.2 / v0.3 — マイグレーション・運用ノート

作成日: 2026-05-02 / Claude Code 作成 (codex 4 ハング後の代替実装)

## マイグレーション順

```
psql -d organization_genealogy -f codex4_ddl_v01.sql   # claim-based core
psql -d organization_genealogy -f codex4_ddl_v02.sql   # activity / function / impact
psql -d organization_genealogy -f codex4_ddl_v03.sql   # relation / event / dormancy
```

各ファイルは前バージョンの存在を前提とし、独立に適用できない。`v01` は extension 作成と ENUM 定義を含むため必ず先に。

## 各バージョンのテーブル一覧

| バージョン | 追加テーブル | 目的 |
|---|---|---|
| v0.1 | `source`, `claim`, `organization_form`, `organization`, `organization_form_assignment` | claim ベースの最小モデル |
| v0.2 | `function_type`, `activity`, `function`, `impact_record` | 「何をしたか / 何の機能を果たしたか / 何が変わったか」の分離 |
| v0.3 | `relation`, `event`, `event_organization`, `event_relation`, `dormancy_record` | 組織間関係と状態遷移、休眠 |

## 設計上のトレードオフと根拠

### Polymorphic Claim (entity_type + entity_id)

`claim.entity_type` と `entity_id` で対象を指す。厳密な FK 制約は使わない代わりに柔軟性を確保。  
**理由**: 古代史料の場合「対象が Organization なのか Activity なのか曖昧」というケースが多い。コアモデルが固まる v1.0 で頻出対象に専用中間テーブルへ昇格させる。  
**実装制約**: アプリ層で `entity_type` の値域 ('organization', 'activity', 'function', 'impact_record', 'relation', 'event', 'organization_form_assignment', 'dormancy_record') を validation する。

### claim.value_kind の 5 値化

`present / absent / partial / unknown / inapplicable` を ENUM 化。  
**理由**: Stream J (Seshat) で確認した通り、Whitehouse et al. 2019 *Nature* の "Moralizing Gods Precede Complex Societies" は **`NA` を `Absent` として扱った coding 慣行が原因で撤回された**。我々のプロジェクトで同じ罠を踏まないため最初から区別する。  
- `present`: 「存在する」と claim
- `absent`: 「明示的に存在しない」と claim (例: ある時代のある組織が「文書記録を持たない」と判明)
- `partial`: 「一部存在する」(規模・期間・地域に限定)
- `unknown`: 「データがない、判断できない」
- `inapplicable`: 「概念がその時代・組織には適用できない」(例: 「IPO 株価」を中世修道院に問うのは inapplicable)

### date_precision の必須化

`exact / year / decade / century / period / before / after / unknown` を ENUM 化し、すべての日付列にペアで持たせる。  
**理由**: 「シトー会創立 1098 年」と「ベネディクト会創立 6 世紀頃」を同じ DATE 列で扱うと精度情報が消える。

### redistribution カラム (source)

`public_redistributable / attribution_required / noncommercial / private / restricted` を CHECK 制約で限定。  
**理由**: Roadmap Phase 7 の公開ゲートで `redistribution = 'public_redistributable'` のみを公開対象にできるよう、ソース投入時点でラベル化する。

### function_type を文字列 ID + 参照テーブルに

`function_type_id` を ENUM ではなく `TEXT PRIMARY KEY` の参照テーブルにした。  
**理由**: codex7 の 25 機能タクソノミーが将来拡張・修正される可能性が高く、ENUM だと migration コストが高い。`function_type` レコードに `era_examples` JSONB を持たせ、運用中に追記可能。

### Relation の strength NULL 許容

`strength NUMERIC(3,2)` は NULL 許容 + CHECK で 0.0-1.0 範囲。  
**理由**: 「ハンザ同盟とリューベックの関係強度 0.8」のような後付け数値は捏造になる。根拠ある場合のみ記録、ない場合は NULL のまま `relation_type` だけで保持。

### dormancy_record を Event とは別テーブルに

`event` だけでは「再活性化された老舗」「眠っている宗族」「シェルカンパニー」の状態を表現しづらいため別途。  
**理由**: Stream I (organizational mortality) — 「死」ではなく「休眠 → 復活」のサイクルが歴史的に多数（イエズス会の禁圧→復活、戦前財閥の解体→系列再編、Mondragón の協同組合危機）。

### embedding を Organization に直付け

`organization.embedding vector(384)` を最初から確保（HNSW インデックスはコメントアウトで残す）。  
**理由**: Stream F の推奨パイプラインで SBERT (384次元) が標準。pgvector で類似組織検索を v0.7 で活用するのに、後から ALTER TABLE するのは大規模データで重い。

## 運用注意

### 入力ルール (品質ゲート)

1. **すべての主張は `claim` を経由**。`organization.attributes` への直接 INSERT は v0.1 ではテストでのみ可、本番は claim 経由。
2. **`recorded_by` は必須**。人間 + AI を区別する (`"yuya@emerging-future.org"`, `"claude-code@2026-05-02"`, `"codex@2026-05-02"`)。
3. **`confidence` の目安**: 一次史料 + 複数源確認 ≥ 0.9 / 単一二次文献 ≈ 0.6-0.8 / Wikipedia 等 ≈ 0.4-0.6 / ChatGPT などの生成系 < 0.3 (本来非推奨)。
4. **`alternate_names` の言語タグ**: BCP 47 で記録 (`ja`, `en`, `zh-Hans`, `ar` 等)。文字システム差異を後で扱える。

### インデックス戦略

- **BRIN (Block Range INdex)** を時系列カラムに採用。`start_date`, `end_date`, `valid_from`, `valid_to`, `event_date`, `recorded_at` 等は範囲クエリが多く、BRIN がディスク効率に優れる。
- **GIN** は JSONB と alternate_names の検索用。
- **HNSW** はコメントアウトで残置。データ量が ~1万件を超えてから ALTER で有効化を推奨。

### 既知の制約・将来課題

| # | 制約 | v? で対応予定 |
|---|---|---|
| 1 | function_type の親子階層は depth 制限なし → 循環参照を検出する制約は別途 | v0.5 でアプリ側 validation 追加 |
| 2 | `geo_scope` JSONB が PostGIS の `geometry` ではない | v0.7 で PostGIS 統合検討 |
| 3 | claim の polymorphic 参照は CASCADE しない (entity 削除時に孤児 claim) | v0.5 でアプリ側 cleanup ジョブ |
| 4 | event_organization.role はフリーテキスト | v0.5 で標準ロールセットを ENUM 化 |
| 5 | record_version は楽観的ロックには不十分 (UPDATE 競合検出ロジック未実装) | v0.7 でアプリ層に実装 |

### バックアップとマイグレーション

- 各バージョンの DDL 適用前に `pg_dump --schema-only` で現状を保存。
- ENUM への値追加は ALTER TYPE で OK (例: `ALTER TYPE relation_type ADD VALUE 'data_sharing';`)。
- ENUM からの値削除は不可 (新 ENUM 作成 + ALTER COLUMN で乗り換え必要)。

## codex2 概念モデルからの差分

codex2 の data_model.md と比べた主な差分:

1. `claim_value_kind` を 5 値化 (Stream J の発見)
2. `redistribution` を source に追加 (Roadmap 公開ゲート対応)
3. `function_type` を ENUM ではなく参照テーブル化 (拡張性)
4. `dissolution_cause` ENUM を Event に追加 (Stream I)
5. `vsr_label` を Event に追加 (codex7 横断軸の物理化)
6. `dormancy_record` を新設 (Stream I)
7. `embedding` を Organization に最初から確保 (運用効率)
8. mimetic / normative / coercive を relation_type に追加 (Stream L: DiMaggio-Powell)

## 次の実装ステップ

1. **function_type への codex7 25 機能 INSERT** — `codex7_function_taxonomy.json` から SQL 生成
2. **organization_form への seed** — Mintzberg 7, Hannan-Freeman, Laloux 5, Wikidata Q43229 subclass tree
3. **Wikidata SPARQL → claim 経由 INSERT のサンプル ETL** — codex5 のクエリを使う
4. **テストデータ**: VOC (1602-1799), 三井越後屋 (1673-), ベネディクト会 (529-), ハンザ同盟 (12c-17c), MakerDAO (2017-) の 5 件で全機能を検証

これらは Roadmap Phase 1 (v0.1) のアクティビティに該当する。
