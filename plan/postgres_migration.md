# PostgreSQL Migration Guide

対象 SQLite DB: `data/og.db`

確認日時: 2026-05-03。`sqlite3 data/og.db '.schema'` と行数集計で、以下 15 テーブルを確認した。

| table | rows |
|---|---:|
| source | 108 |
| claim | 859 |
| organization_form | 57 |
| organization | 373 |
| organization_form_assignment | 104 |
| function_type | 25 |
| activity | 98 |
| function_record | 205 |
| impact_record | 103 |
| relation | 46 |
| event | 83 |
| event_organization | 84 |
| event_relation | 0 |
| dormancy_record | 0 |
| organization_temporal_facet | 28 |

## 型差分対応表

| SQLite | PostgreSQL | 対象・変換 |
|---|---|---|
| `TEXT PRIMARY KEY` | `UUID PRIMARY KEY` | `source_id`, `claim_id`, `organization_id` など。既存値は 32 桁 hex UUID なら PostgreSQL `uuid` に直接投入できる。 |
| `TEXT` ISO 8601 date | `DATE` | `publication_date`, `start_date`, `end_date`, `event_date`, `valid_from`, `valid_to` など。年・世紀など非 exact は precision 列を維持する。 |
| `TEXT DEFAULT CURRENT_TIMESTAMP` | `TIMESTAMPTZ DEFAULT now()` | `created_at`, `updated_at`, `recorded_at`, `accessed_at`。SQLite の naive timestamp は DB 接続側のタイムゾーン方針に合わせる。 |
| `TEXT` JSON comment | `JSONB` | `authors`, `locator`, `claim_value`, `criteria`, `alternate_names`, `geo_scope`, `attributes`, `external_ids`, `inputs`, `outputs`, `scale`, `mechanism`, `beneficiaries`, `dependency`, `metric_value`, `affected_scope`, `relation_attributes`, `participants`, `causes`, `outcomes`, `location`, `facet_value`。 |
| `CHECK (... IN (...))` | `ENUM` | `source_type`, `claim_value_kind`, `date_precision`, `org_status`, `activity_orientation`, `impact_direction`, `impact_time_horizon`, `relation_type`, `relation_directionality`, `event_type`, `dissolution_cause`。運用初期は `CHECK` のままでも可。 |
| `INTEGER CHECK (is_primary IN (0,1))` | `BOOLEAN` | `organization_form_assignment.is_primary`: `0/1` を `false/true` に変換。 |
| `REAL` | `NUMERIC(3,2)` or `DOUBLE PRECISION` | `confidence`, `strength`, `reliability_score` は `NUMERIC(3,2)`。分析値として累積計算する列は `DOUBLE PRECISION` も検討。 |
| `BLOB` | `vector(384)` | `organization.embedding`。pgvector の `vector` 拡張と Python `pgvector` パッケージを使い、384 個の float に変換する。 |
| `valid_period_from`, `valid_period_to` の `TEXT` 2 列 | `DATERANGE` | `organization_form.valid_period`。下限 inclusive、上限 exclusive の `[)` を標準にする。 |
| `valid_from`, `valid_to` の `TEXT` 2 列 | `DATE` 2 列、または用途別 `DATERANGE` | 既存 PostgreSQL DDL v0.1-v0.3 は 2 列設計。期間演算を多用するテーブルだけ `DATERANGE` へ寄せる。 |
| SQLite trigger | PostgreSQL `BEFORE UPDATE` trigger | `updated_at` と `record_version` は PostgreSQL 側で `trg_set_updated_at()` に統一。 |
| SQLite btree indexes | BRIN / GIN / HNSW | date は BRIN、JSONB は GIN、embedding は HNSW。 |

注意: `research/codex4_ddl_v02.sql` では機能表が `function`、SQLite 実DBでは `function_record`。PostgreSQL では予約語衝突と読みやすさのため `function_record` に揃えるのが無難。

## PostgreSQL 側の前提 DDL

最小前提:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS vector;
```

`ENUM` は既存 DDL の語彙を先に作る。現行 SQLite の CHECK 語彙から外れた値は確認できなかったが、投入前に `SELECT DISTINCT` で再確認する。

`organization_form.valid_period` は以下のように受ける。

```sql
valid_period DATERANGE
```

範囲変換は `daterange(valid_period_from::date, valid_period_to::date, '[)')` 相当。片側不明は unbounded range として `NULL` bound にする。

## 抽出と投入手順

1. SQLite をバックアップする。

```bash
sqlite3 data/og.db ".backup 'data/og.backup.sqlite'"
```

2. PostgreSQL スキーマを作る。

```bash
psql "$PG_URL" -f research/codex4_ddl_v01.sql
psql "$PG_URL" -f research/codex4_ddl_v02.sql
psql "$PG_URL" -f research/codex4_ddl_v03.sql
```

`organization_temporal_facet` は `sql/schema_sqlite_v05_temporal_facet.sql` には SQLite DDL だけがあるため、PostgreSQL 版 DDL を追加してから投入する。

3. dry-run で SQLite 側件数と変換対象を確認する。

```bash
python etl/20_migrate_to_postgres.py --dry-run
```

4. `PG_URL` を指定して投入する。

```bash
PG_URL="postgresql://user:password@host:5432/dbname" python etl/20_migrate_to_postgres.py
```

5. 投入後に件数と外部キーを確認する。

```sql
SELECT 'organization' AS table_name, count(*) FROM organization;
SELECT conname FROM pg_constraint WHERE contype = 'f' AND NOT convalidated;
```

大量投入時は一時的に通常 index を後作成にする。ただし外部キー制約は移行順序の検査として残す。

## テーブル投入順序

外部キー依存に合わせて以下の順序で投入する。

1. `source`
2. `claim`
3. `organization_form`
4. `organization`
5. `organization_form_assignment`
6. `function_type`
7. `activity`
8. `function_record`
9. `impact_record`
10. `relation`
11. `event`
12. `event_organization`
13. `event_relation`
14. `dormancy_record`
15. `organization_temporal_facet`

`claim.entity_id` は polymorphic UUID なので、参照先実体より前に投入できる。`claim.source_id` だけ `source` に依存する。

## pgvector と HNSW index

Python 側は `psycopg2` v2 系と `pgvector` パッケージを使う。

```bash
pip install "psycopg2-binary>=2,<3" pgvector
```

`organization.embedding` は `vector(384)`。SQLite 側 BLOB は 384 個の little-endian float32 を想定して変換し、長さが合わない値は投入を止めて確認する。

HNSW index は初期ロード時には作らない。現在の `organization` は 373 件で、HNSW の構築・メンテナンスコストの方が大きい。1 万件超え、かつ embedding 類似検索が実運用クエリになった時点で有効化する。

```sql
CREATE INDEX CONCURRENTLY idx_org_embedding_hnsw
ON organization
USING hnsw (embedding vector_cosine_ops);
```

Supabase は pgvector 対応があるが拡張有効化権限を確認する。RDS PostgreSQL はエンジンバージョンと `pgvector` extension availability を事前確認する。Docker は `pgvector/pgvector` イメージが最短。

## 想定環境比較

| 環境 | 長所 | 注意点 | 適性 |
|---|---|---|---|
| Supabase | pgvector を含むアプリ開発が速い。Auth/API/管理 UI も使える。 | extension 有効化、接続プール、バックアップ保持、リージョンを確認。大規模分析は制限に当たりやすい。 | プロトタイプ、共有閲覧、軽量 API。 |
| Amazon RDS PostgreSQL | 運用管理、バックアップ、監視、VPC 統合が強い。 | pgvector 対応バージョン確認が必須。HNSW index 構築時の I/O とメンテナンス枠に注意。 | 中長期運用、本番 DB、他 AWS 資産との統合。 |
| Docker local | DDL と ETL の再現性が高い。破壊的検証を隔離できる。 | 永続ボリューム、バックアップ、性能は自前管理。チーム共有には向かない。 | 開発、CI、移行リハーサル。 |

推奨順は `Docker local` でリハーサル、`Supabase` で共有プロトタイプ、研究 DB として継続運用する段階で `RDS`。

## dual-write vs cut-over

| 方式 | 長所 | 短所 | 今回の判断 |
|---|---|---|---|
| dual-write | SQLite と PostgreSQL を同時更新でき、段階移行しやすい。ロールバックも簡単。 | ETL/アプリの全書き込み経路に二重実装が必要。差分同期と不整合検出が増える。 | 現状は過剰。 |
| cut-over | 移行手順が単純。投入後に PostgreSQL を正本にできる。 | 切替時に短時間の書き込み停止が必要。失敗時はバックアップから戻す。 | 現在の規模では推奨。 |

現行 DB は 15 テーブル合計 2,173 行で、書き込みは ETL バッチ中心。まず cut-over で十分。dual-write はアプリから常時更新する段階、または SQLite 配布版を正本として残す要件が出た時に再検討する。

## 検証クエリ

```sql
SELECT count(*) FROM source;
SELECT count(*) FROM claim;
SELECT count(*) FROM organization;
SELECT count(*) FROM organization_temporal_facet;

SELECT organization_id
FROM organization
WHERE embedding IS NOT NULL
  AND vector_dims(embedding) <> 384;

SELECT claim_id
FROM claim c
LEFT JOIN source s ON s.source_id = c.source_id
WHERE c.source_id IS NOT NULL
  AND s.source_id IS NULL;
```

`vector_dims()` は pgvector が有効な PostgreSQL でのみ使える。
