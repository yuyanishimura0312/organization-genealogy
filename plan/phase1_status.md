# Phase 1 (v0.1) 実装ステータス

更新日: 2026-05-02

## 完了

### 1. SQLite サンドボックス構築 ✓

- `sql/schema_sqlite_v01.sql` — PostgreSQL DDL v0.1 + v0.2 + v0.3 を SQLite 互換に移植
- 13 テーブル + 9 ENUM CHECK 制約 + 5 値 claim_value_kind の厳格化
- 名称差分: `function` → `function_record` (PG 予約語回避)、`vector(384)` → `BLOB`、`daterange` → 2 カラム化、`BRIN/GIN/HNSW` → btree

### 2. 25 機能タクソノミー投入 ✓

- `codex7_function_taxonomy.json` (25 functions) → `function_type` テーブル
- Miller 20 critical subsystems + Beer VSM 5
- 各 function に era_examples (ancient/medieval/modern/contemporary/digital) 保持

### 3. 53 organization_form シード ✓

| Taxonomy | 件数 |
|---|---:|
| `mintzberg_1989` | 7 |
| `hannan_freeman` | 3 |
| `laloux_2014` | 5 |
| `legal_form` | 14 |
| `historical_era` | 15 |
| `east_asian` | 9 |

### 4. 5 代表ケース完全注釈 ✓

5 組織で全 11 テーブルを実際に使用、claim → source のトレーサビリティ完備。

| 組織 | period | 主要発見 |
|---|---|---|
| **ベネディクト会** (529–) | 1500年継続 | 分散ネットワーク + 共通 Rule、写本による知識継承 |
| **ハンザ同盟** (1159–1669) | 510年 | unhansing 制裁、200 都市連合、ディエット型運営 |
| **VOC** (1602–1799) | 197年 | 永続法人＋公開株式＋専門経営の三位一体を初実装 |
| **三井越後屋** (1673–) | 350年継続 | 家・暖簾・別家 → 財閥 → 系列の連続変容 |
| **MakerDAO** (2017–) | 9年 | Foundation 解体による完全 DAO 化、コードベース境界 |

カバレッジ:
- form_assignment 16 (3.2 平均/組織)
- activity 10、function_record 22、impact_record 9
- event 10 (founding 5 / dissolution 3 / reorganization 1 / revival 1)
- relation 2 (knowledge_transfer ハンザ→VOC、mimetic_isomorphism VOC→MakerDAO)

## 繰越 (Phase 1 残)

### 5. Wikidata パイロット ETL ⚠️ 再試行

- `etl/03_wikidata_pilot.py` を作成、`SERVICE wikibase:label` + 6 era 対応
- **問題**: Wikidata SPARQL が broad `FILTER(YEAR(?creation) ...)` クエリで連続タイムアウト
- 試行: 古代 → 失敗、6 era → 失敗、近世以降 4 era × 20 件 → 失敗
- **対策**: `research/codex5_queries/` の type-specific クエリ (`Q188509 corporation`, `Q210980 monastic_order` 等) を使う方が確実。SPARQL 全文検索より P31 の subclass tree でフィルタする方が高速
- 再試行は別スクリプト `etl/05_wikidata_typed.py` を新規作成して対応 (次セッション)

## 累積データ (5 月 2 日時点)

```
organization_form              53
function_type                  25
organization                    5
organization_form_assignment   16
activity                       10
function_record                22
impact_record                   9
event                          10
relation                        2
source                          9
claim                          10
```

## Phase 1 完了基準への進捗

ロードマップ Phase 1 完了条件:
- [x] 全レコードが Source/Claim に紐づく構造 — 実装済
- [x] `exact`, `year`, `century`, `period`, `unknown` などの日付精度を扱える — 実装済
- [x] 近代法人以外の組織が下位扱いされずに入力できる — 5 ケースで検証済
- [ ] 200-500 件の pilot データ — 5 件のみ。Wikidata 再試行で 100+ 件追加が次の目標

## 次のアクション

1. `etl/05_wikidata_typed.py` を新規作成 — type-specific クエリ
2. ROR (Research Organization Registry) からの大学・研究機関取り込み
3. OpenAlex から学術機関の補完
4. 形態別件数の偏り検査 (ゲート 2)
5. 5 ケースのスキーマ完成度を Phase 2 移行判定の基準にする
