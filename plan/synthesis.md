# 事前リサーチ統合サマリ — 組織を生命として捉える系譜分析

作成日: 2026-05-02 / 第1波 6 + 第2波 6 + codex 7 タスク (1 ハング、Claude 代替) = 19 アーティファクト統合

## 投入リソース

| 波 | 担当 | 並列数 | 完了状況 |
|---|---|---|---|
| 第1波 | Claude エージェント (Stream A〜F: 理論 / 歴史 / 類型 / DB / イノベ / 方法論) | 6 | 全完了 |
| 第1波 | codex CLI (1: 理論批判 / 2: 概念データモデル / 3: 東アジア視点) | 3 | 全完了 |
| 第2波 | Claude (Stream G〜L: 非西洋 / 周縁 / 死亡 / Seshat / phylo network / 制度論) | 6 | 全完了 |
| 第2波 | codex CLI (4: DDL / 5: SPARQL / 6: roadmap / 7: 機能タクソノミー) | 4 | 3 完了、4 (DDL) は 30+ 分ハングのため Claude が代替実装 |

## 主要発見 (Top 12)

1. **生命メタファーは単一理論ではなく 4 系譜に分かれる** — Spencer 有機体観 / Hannan-Freeman 個体群生態学 / Maturana-Luhmann オートポイエーシス / Beer サイバネティクス。codex1 の批判的整理に従い、**個体群生態学を主・他 3 系譜を補助**として組み合わせる (Spencer は批判対象)
2. **生命メタファーの 5 つの罠を同時に潰す**: reification / 適者生存の循環 / 個体境界の曖昧 / 機能主義の後知恵 / 生物学の過剰輸入
3. **西洋データバイアスが致命的**: 既存 41 DB の大半が北米・上場・現代企業に偏る → Stream G/H/codex3 で **東アジア固有形態 (家・暖簾・座・株仲間・宗族・票号・門中・会館)、非西洋国家組織 (ダホメイ Mino / 科挙 / マンサブダール / インカ ayllu)、周縁・運動 (協同組合・先住民・デジタルコモンズ) を最低比率で含める**
4. **組織の死データはほぼ存在しない** (Stream D + I) → 独自構築必須。Stinchcombe newness, Hannan inertia, Carroll-Hannan obsolescence の 3 死亡因子と dormancy 状態を扱うスキーマを v0.3 で導入
5. **Seshat の NA→Absent 撤回事件 (Whitehouse 2019 *Nature*)** から、claim_value_kind を `present | absent | partial | unknown | inapplicable` の 5 値化必須 (DDL v0.1 に実装済み)
6. **組織は M&A・模倣・分社で水平伝達が頻繁 → tree モデル不適、phylogenetic network 必要** (Stream K)。NeighborNet / SplitsTree / PhyloNetworks.jl を v0.7 で導入
7. **Miller 20 critical subsystems + Beer VSM 5 = 25 機能** が古代から DAO まで適用可能な普遍タクソノミー (codex7 で JSON 化、`codex7_function_taxonomy.json` が DDL v0.2 の `function_type` 参照表に直接ロード可能)
8. **DiMaggio-Powell の coercive / mimetic / normative isomorphism** を `relation_type` ENUM に物理化 (DDL v0.3) → 「効率的選択」に偏らず制度的同型化を捕捉
9. **Wikidata の Q43229 organization subclass tree が古代〜現代統合の最有力基盤** (CC0)。codex5 の 13 SPARQL クエリで時代別・地域別・型別バッチ取得が可能
10. **West (2017) のスケーリング指数 (企業 ~0.8 sublinear / 都市 ~1.15 superlinear) が「組織は生物に近いか都市に近いか」を計量化する軸** を提供 (Stream A)
11. **野中 SECI / 伊丹「場」/ 稲盛アメーバが Maturana オートポイエーシス + 西田場所論のハイブリッド**で、西洋系譜の補完線として機能 (codex3)
12. **Roadmap は Q1〜Q8 の 8 四半期 + 6 つの意思決定ゲート (理論 / データ / スキーマ / 分類 / 系譜 / 公開)** で進める (plan/roadmap.md)

## 実装に直結するアーティファクト

| ファイル | 用途 |
|---|---|
| `plan/roadmap.md` | フェーズ計画・マイルストーン・リスク登録簿・成功指標 |
| `research/codex2_data_model.md` | 概念データモデル (claim ベース、出典トレーサブル) |
| `research/codex4_ddl_v01.sql` | PostgreSQL 16 + pgvector 実装 (organization / source / claim / form) |
| `research/codex4_ddl_v02.sql` | activity / function / impact_record (Miller+VSM 25 機能対応) |
| `research/codex4_ddl_v03.sql` | relation / event / dormancy_record (系譜ネットワーク基盤) |
| `research/codex4_ddl_README.md` | マイグレーション順、設計判断、既知制約 |
| `research/codex5_wikidata_sparql.md` + `codex5_queries/*.sparql` | Wikidata 取り込み ETL クエリセット |
| `research/codex7_function_taxonomy.json` | 25 機能の機械可読定義 (DDL v0.2 にロード) |

## 全 19 リサーチノート構造

### 理論・批判 (5)
- `A_theoretical_foundations.md` — 16 理論、生命体的観点で整理
- `codex1_theory_critique.md` — 4 系譜の射程・限界・採用提言
- `E_innovation_theory.md` — 18 イノベ理論、機能/活動/インパクト視点
- `K_phylogenetic_network.md` — 12 系統推定手法、組織応用未確立
- `L_institutional_power.md` — 13 制度論・権力論、適応物語の対抗概念

### 歴史・形態 (4)
- `B_historical_genealogy.md` — 13 形態をバンドから DAO まで時代順
- `C_typologies.md` — 14 既存タイポロジー、共通 5 次元
- `G_non_western_states.md` — 18 非西洋国家組織形態
- `H_marginal_movements.md` — 28 周縁・運動・協同組合・先住民事例

### データ・方法論 (4)
- `D_existing_databases.md` — 41 DB、カバレッジマップ、Top 10 優先度
- `F_methodology.md` — 19 手法、推奨パイプライン、評価基準
- `I_organizational_mortality.md` — 死亡理論 7 / 事例 13 / データ源 10
- `J_seshat_cliodynamics.md` — Seshat 構造、取得方法、NA 問題

### 地域・東アジア (1)
- `codex3_east_asian_perspective.md` — 15 日本経営学 + 14 東アジア組織形態

### 設計・実装 (5)
- `codex2_data_model.md` — 概念モデル
- `codex4_ddl_v01/v02/v03.sql` + `codex4_ddl_README.md` — 実装 DDL
- `codex5_wikidata_sparql.md` + `codex5_queries/` — 取り込みクエリ
- `codex7_function_taxonomy.md/.json` — 25 機能タクソノミー
- `plan/roadmap.md` — 実行ロードマップ

## 次に取りかかれる具体タスク

Roadmap Phase 0 (v0.0 Research Synthesis) から Phase 1 (v0.1) への移行点:

1. **DDL v0.1 を実 PostgreSQL に適用** (Docker / Supabase / RDS 何でも可)
2. **`function_type` への codex7 JSON ロード** — JSON → SQL INSERT 生成スクリプト
3. **`organization_form` シードデータ投入** — Mintzberg 7, Hannan typology, Laloux 5, 法人格分類, Wikidata subclass tree
4. **Wikidata SPARQL でパイロット取得** — codex5 の `00_organization_subclass_tree.sparql` を回して claim 経由で 100 件投入
5. **代表 5 ケースの完全注釈** — VOC / 三井越後屋 / ベネディクト会 / ハンザ同盟 / MakerDAO で全テーブル使用を検証

これらは Phase 1 (期間 2-4 ヶ月想定) の最初の 2-3 週間で完了可能。

## codex 4 ハング事故の記録

codex 並列タスク #4 (DDL 生成) が ~30 分ハングし exit code 144 で失敗。他 3 codex タスクは 5-10 分で正常完了したため codex 個別の問題と判定。Claude Code が概念モデル + Stream I/J/L/codex7 の知見を統合して DDL v0.1/v0.2/v0.3 + README を直接作成した。
