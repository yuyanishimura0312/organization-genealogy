# 組織を生命として捉える系譜分析

> Organization Genealogy as Living Systems — 原初の狩猟採集バンドから現代の DAO まで、組織を生命体として捉え、機能・活動・インパクトをボトムアップに比較する長期研究プロジェクト

**ステータス**: v0.0 事前リサーチ完了 → v0.1 Phase 1 進行中 (2026-05-02)

公開ダッシュボード: <https://yuyanishimura0312.github.io/miratuku-news-v2/dashboards/org-genealogy.html>

## プロジェクト原則

- 「企業」を標準型にしない。家・宗族・修道院・ワクフ・ギルド・DAO を同じ比較面で扱う
- すべての記述を `claim` として扱い、出典・確度・解釈者・記録時点を残す
- 生存を適応の証拠にしない。生命メタファーは観察次元を増やすための限定的比喩として使う
- 5 つの罠を回避: reification / 適者生存の循環 / 個体境界の曖昧 / 機能主義の後知恵 / 生物学の過剰輸入

## ディレクトリ構成

```
organization-genealogy/
├── plan/          # 実行ロードマップと統合サマリ
│   ├── roadmap.md         # 8 四半期計画 + 6 意思決定ゲート + リスク登録簿
│   └── synthesis.md       # 第1波+第2波リサーチの統合
├── research/      # 19 リサーチノート (Stream A–L) + codex 1–7 タスク
│   ├── A_theoretical_foundations.md     # 16 理論
│   ├── B_historical_genealogy.md        # 13 形態
│   ├── C_typologies.md                  # 14 タイポロジー
│   ├── D_existing_databases.md          # 41 DB 調査
│   ├── E_innovation_theory.md           # 18 イノベ理論
│   ├── F_methodology.md                 # 19 手法
│   ├── G_non_western_states.md          # 18 非西洋国家形態
│   ├── H_marginal_movements.md          # 28 周縁・運動
│   ├── I_organizational_mortality.md    # 死亡 7 + 事例 13
│   ├── J_seshat_cliodynamics.md         # Seshat 詳細
│   ├── K_phylogenetic_network.md        # 12 系統手法
│   ├── L_institutional_power.md         # 13 制度論
│   ├── codex1_theory_critique.md        # 4 系譜の射程・限界
│   ├── codex2_data_model.md             # 概念データモデル
│   ├── codex3_east_asian_perspective.md # 東アジア視点 15+14
│   ├── codex4_ddl_v0[1-3].sql           # PostgreSQL DDL (本番ターゲット)
│   ├── codex5_wikidata_sparql.md        # SPARQL クエリ集
│   └── codex7_function_taxonomy.{md,json} # 25 機能タクソノミー
├── sql/           # SQLite サンドボックス DDL
│   └── schema_sqlite_v01.sql            # v0.1 + v0.2 + v0.3 を 1 ファイルに移植
├── etl/           # 投入スクリプト
│   ├── 01_load_function_types.py        # codex7 JSON → function_type
│   ├── 02_seed_organization_forms.py    # 53 form (Mintzberg/Hannan/Laloux/legal/historical/east_asian)
│   ├── 03_wikidata_pilot.py             # Wikidata SPARQL → claim 経由 (再試行待ち)
│   └── 04_representative_cases.py       # 5 代表ケースの全テーブル投入
└── data/
    └── og.db                            # SQLite サンドボックス
```

## 現状 (Phase 1 進行中)

| テーブル | 件数 | 内訳 |
|---|---:|---|
| `organization_form` | 53 | Mintzberg 7 / Hannan 3 / Laloux 5 / 法人格 14 / 歴史形態 15 / 東アジア 9 |
| `function_type` | 25 | Miller 20 critical subsystems + Beer VSM 5 |
| `organization` | 5 | VOC / 三井越後屋 / ベネディクト会 / ハンザ同盟 / MakerDAO |
| `organization_form_assignment` | 16 | 5 ケース × 平均 3.2 タクソノミー |
| `activity` | 10 | |
| `function_record` | 22 | |
| `impact_record` | 9 | |
| `event` | 10 | founding / dissolution / reorganization / revival / governance_change |
| `relation` | 2 | knowledge_transfer / mimetic_isomorphism |
| `source` | 9 | primary_text / secondary_literature / dataset / onchain |
| `claim` | 10 | すべて出典付き、5 値 (present/absent/partial/unknown/inapplicable) |

### 5 代表ケースのカバレッジ

| 組織 | start | end | status | form数 | 機能数 |
|---|---|---|---|---:|---:|
| ベネディクト会 | 0529 | – | active (1500年継続) | 3 | 4 |
| ハンザ同盟 | 1159 | 1669 | extinct | 3 | 3 |
| VOC | 1602 | 1799 | extinct | 3 | 7 |
| 三井越後屋 | 1673 | – | active (350年継続) | 5 | 4 |
| MakerDAO | 2017 | – | active | 2 | 4 |

## 実行方法

### サンドボックス再構築

```bash
# 1. SQLite スキーマ作成
sqlite3 data/og.db < sql/schema_sqlite_v01.sql

# 2. 25 機能タクソノミー投入
python3 etl/01_load_function_types.py

# 3. 53 形態投入
python3 etl/02_seed_organization_forms.py

# 4. 5 代表ケース注釈
python3 etl/04_representative_cases.py
```

### PostgreSQL 本番への移行

`research/codex4_ddl_v0[1-3].sql` が PostgreSQL 16 + pgvector 用の本番 DDL。SQLite サンドボックスで設計を検証後、Supabase / RDS に移行する。

```bash
psql -d organization_genealogy -f research/codex4_ddl_v01.sql
psql -d organization_genealogy -f research/codex4_ddl_v02.sql
psql -d organization_genealogy -f research/codex4_ddl_v03.sql
```

## ロードマップ

| Q | version | マイルストーン |
|---|---|---|
| Q1 | v0.0 ✓ | 事前リサーチ統合・理論立場の固定 |
| Q2 | v0.1 進行中 | claim-based DB 実装、データ取り込み (5 ケース完了、Wikidata パイロット要再試行) |
| Q3 | v0.2 | Activity/Function/Impact 分離・深掘り注釈 |
| Q4 | v0.3 | Relation/Event 実装・系譜ネットワーク試作 |
| Q5 | v0.5 | temporal facet 本格化・比較ケースブック |
| Q6 | v0.7 | 特徴抽出・ボトムアップ分類 |
| Q7 | v0.9 | 系譜推定・専門家レビュー |
| Q8 | v1.0 | 公開リリース・論文草稿 |

詳細: `plan/roadmap.md`

## 既知の課題

1. **Wikidata SPARQL タイムアウト** — broad date FILTER クエリが Wikidata 公式エンドポイントで頻繁にタイムアウト。`research/codex5_queries/` の type-specific クエリで再試行予定
2. **PostgreSQL 環境未構築** — Mac ローカルに無いため SQLite で代替中。Supabase / 軽量 Postgres 環境を後続で
3. **古代・中世データの厚み** — Seshat databank 統合が次の優先

## ライセンス

研究ノート (`research/*.md`) は CC-BY 4.0 を予定。コード (`etl/`, `sql/`) は MIT を予定。データ (`data/og.db`) は構成 source のライセンスを継承し、再配布可能なソースのみで再ビルド可能な形で公開する方針 (Phase 7 / v1.0 で確定)。

## クレジット

- Yuya Nishimura (西村優也) / NPO 法人ミラツク
- Claude Code (Opus 4.7 1M context) — 並列調査・実装・ダッシュボード
- codex CLI — 並列調査・データモデル・タクソノミー
