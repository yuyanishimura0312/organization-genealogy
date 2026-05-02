# Stream F: 方法論レビュー — ボトムアップな組織分類と進化系譜推定

> 事前リサーチ（2026-05-02）。WebSearch にて確認した実在文献・ツールのみを記載。未確認は明記。

## 概要

組織を生命的存在として系譜分析するには、(1) 組織の表現学習（テキスト・ネットワーク・財務・統治構造の多モーダル特徴）、(2) ボトムアップ・クラスタリング（HDBSCAN/BERTopic 等）、(3) 進化系統推定（cultural phylogenetics の応用）、(4) シミュレーションによる反実仮想（ABM）、(5) クリオダイナミクス的歴史検証、の 5 層スタックが妥当。Hoberg-Phillips TNIC・Carley の ORA・Seshat databank・Mesa が実用基盤。最大の問題は組織の「形質（character state）」をどう離散化／連続化するかの方法論未確立。

---

## 手法カタログ（19 件）

### 1. ORA (Organizational Risk Analyzer) — 動的ネットワーク分析

- **代表研究者**: Kathleen M. Carley (CMU CASOS)
- **必要データ**: meta-network（agent / organization / knowledge / task / location / event の多モード関係）
- **計算資源**: デスクトップ可。ノード数 10^5 まで実用。
- **適用例**: 組織内 / 組織間ネットワークの構造変化追跡、key actor 抽出、disinformation 拡散
- **成熟度**: 実用（軍・諜報・学術で広範に採用）
- **典拠**: CMU CASOS Center, https://www.cmu.edu/casos-center/

### 2. Hoberg-Phillips TNIC（Text-based Network Industry Classification）

- **代表研究者**: Gerard Hoberg (USC), Gordon Phillips (Tuck/Dartmouth)
- **必要データ**: SEC EDGAR 10-K Item 1 (Business Description)。年次更新。
- **計算資源**: 中規模（1 万社 × 30 年）。Doc2Vec 版 (2025 JoF) は GPU 推奨。
- **適用例**: SIC/NAICS の上位互換として、製品市場類似度に基づく企業分類。組織進化分析の出発点。
- **成熟度**: 実用（Tuck Data Library で公開。米国上場企業のみ）
- **典拠**: https://hobergphillips.tuck.dartmouth.edu/, Hoberg & Phillips (2016) JPE; (2025) JoF

### 3. Sentence-BERT / SBERT 埋め込み

- **代表研究者**: Reimers & Gurevych (UKP Lab)
- **必要データ**: ミッションステートメント、定款、IR 資料、有価証券報告書、ESG 報告
- **計算資源**: CPU で数千件/分。GPU で 10^6 件規模も実用。HuggingFace に 15,000+ pre-trained
- **適用例**: 組織記述文の意味的類似度算出、クラスタ前段の embedding
- **成熟度**: 実用
- **典拠**: Reimers & Gurevych (2019), arXiv:1908.10084; https://sbert.net/

### 4. BERTopic — 神経トピックモデル

- **代表研究者**: Maarten Grootendorst
- **必要データ**: 任意の文書集合（短文〜中文）
- **計算資源**: SBERT + UMAP + HDBSCAN + c-TF-IDF。10^5 文書を 1 GPU で 1 時間オーダ。
- **適用例**: 組織の自己記述からトピック構造を抽出し、業界横断の機能的類型を発見
- **成熟度**: 実用
- **典拠**: Grootendorst (2022), arXiv:2203.05794

### 5. UMAP + HDBSCAN クラスタリング

- **代表研究者**: McInnes, Healy (UMAP); Campello, Moulavi, Sander (HDBSCAN)
- **必要データ**: 高次元 embedding
- **計算資源**: 10^6 点まで CPU で実用。USPS で HDBSCAN 単体比 +60pt、MNIST で 26分 → 5秒
- **適用例**: 組織 embedding のボトムアップ密度ベース分類。ノイズ点許容。
- **成熟度**: 実用
- **典拠**: umap-learn.readthedocs.io; Allaoui et al. (2020)

### 6. NetworkX / igraph — 一般ネットワーク分析

- **代表研究者**: NetworkX (Hagberg et al.); igraph (Csárdi, Nepusz)
- **必要データ**: エッジリスト（取締役兼任、株式所有、サプライチェーン、提携）
- **計算資源**: NetworkX は 10^4-10^5 ノードで快適。igraph は C 実装で 10^7 級可。
- **適用例**: interlocking directorate、コーポレート・エリート分析、コミュニティ検出
- **成熟度**: 実用
- **典拠**: networkx.org, igraph.org

### 7. Bloomberg SPLC + Compustat サプライチェーン網

- **代表研究者**: Culot et al. (2023, J. Supply Chain Management)
- **必要データ**: Bloomberg SPLC（10万社・50万関係、2006-）、Compustat 財務、WRDS 経由
- **計算資源**: Postgres / DuckDB で十分
- **適用例**: 組織間依存ネットワーク、産業生態系の系統推定
- **成熟度**: 実用（商用ライセンス必須）
- **典拠**: Culot et al. (2023), https://onlinelibrary.wiley.com/doi/10.1111/jscm.12294

### 8. Cultural Phylogenetics（文化系統学）

- **代表研究者**: Russell D. Gray, Alex Mesoudi, Thomas Currie, Fiona Jordan
- **必要データ**: 離散化された形質マトリクス（言語語彙、儀礼、政治複雑性等）
- **計算資源**: BEAST / MrBayes で 100-1000 タクサ × 数百形質、MCMC 数日
- **適用例**: Currie & Mace (2009/2011): 政治複雑性の進化の mode and tempo。組織形質への直接応用は **未検証**。
- **成熟度**: 言語・物質文化では実用、組織形態への応用は研究段階
- **典拠**: Mesoudi (2011); Gray, Drummond, Greenhill (2009 Science); Currie et al. (2010 Nature)

### 9. BEAST X / MrBayes — Bayesian phylogenetic inference

- **代表研究者**: Drummond, Rambaut, Suchard, Bouckaert (BEAST); Huelsenbeck, Ronquist (MrBayes)
- **必要データ**: aligned character matrix + 任意の時間制約
- **計算資源**: GPU 加速版あり。1000 タクサで数日〜週オーダ
- **適用例**: 組織形質を「文字状態」化すれば理論的には適用可。ただし水平伝達（M&A、模倣）が頻繁な組織では tree モデルの妥当性が問題（→ phylogenetic network が必要）
- **成熟度**: 生物・言語で実用、組織は **未検証**
- **典拠**: Suchard et al. (2025) Nature Methods; beast.community

### 10. Cliodynamics / Seshat Global History Databank

- **代表研究者**: Peter Turchin, Harvey Whitehouse, Pieter François
- **必要データ**: Seshat（500+ 政体、1500 変数、紀元前 1万年〜現代）+ CrisisDB
- **計算資源**: tabular。R/Python で十分
- **適用例**: 構造的人口論モデルでの社会危機予測、政治複雑性進化の長期時系列分析
- **成熟度**: 研究段階（データ品質と coding bias に批判あり）
- **典拠**: seshatdatabank.info, Turchin et al. (2018) Nature; csh.ac.at/peter-turchin/

### 11. Maddison Project Database

- **代表研究者**: Bolt & van Zanden (Groningen GGDC)
- **必要データ**: 公開（169 国、紀元 1 〜 2022 年の GDP per capita）
- **計算資源**: 軽量
- **適用例**: 組織を取り巻くマクロ経済環境の長期 covariate
- **成熟度**: 実用（標準データセット）
- **典拠**: rug.nl/ggdc/historicaldevelopment/maddison/, Maddison Project DB 2023

### 12. Agent-Based Modeling — Mesa / Repast / NetLogo

- **代表研究者**: Joshua Epstein & Robert Axtell (Sugarscape, 1996); Mesa (Project Mesa, 2025 Mesa 3); Repast (Argonne)
- **必要データ**: 行動ルール仕様（経験則 or 推定）
- **計算資源**: Mesa (Python) で 10^4-10^5 エージェント。Repast Java は HPC 可。NetLogo は中規模向け教育・研究。
- **適用例**: 組織の出生・死亡・分化のシミュレーション、反実仮想
- **成熟度**: 実用
- **典拠**: Epstein & Axtell (1996) "Growing Artificial Societies"; ter Hoeven (2025) JOSS

### 13. Organizational Ecology（Hannan & Freeman）

- **代表研究者**: Michael T. Hannan, John Freeman, Glenn Carroll
- **必要データ**: 組織人口の vital rates（出生・死亡）、ニッチ幅、密度
- **計算資源**: 軽量（事象履歴分析、Cox 回帰）
- **適用例**: 組織形態を「種」として扱い、density dependence、structural inertia、age dependence を検証
- **成熟度**: 実用（理論的支柱の一つ）
- **典拠**: Hannan & Freeman (1977 AJS, 1989 Harvard Univ Press)

### 14. Graph Neural Networks for firm representation

- **代表研究者**: Hamilton, Ying, Leskovec (GraphSAGE); 近年は heterogeneous GNN（HGNN-CFI 等）
- **必要データ**: ノード特徴 + エッジ（複数関係種別）
- **計算資源**: GPU 必須。10^5 ノードで数時間。
- **適用例**: 競合企業同定（HGNN-CFI, 3,371 社で実証）、株価予測、firm similarity learning
- **成熟度**: 研究段階（学術応用は増加中）
- **典拠**: Annals of Operations Research (2025) HGNN-CFI; SNAP @ Stanford

### 15. NLP for organizational culture — earnings calls / Glassdoor

- **代表研究者**: MIT SMR/Glassdoor Culture 500 (Sull, Sull, Chamberlain); Li et al. AEA paper "Communicating Corporate Culture"
- **必要データ**: 決算説明会トランスクリプト、Glassdoor 1.2M レビュー、求人記述
- **計算資源**: GPU で transformer 推論
- **適用例**: 90+ culture topic への自動分類、Wells Fargo の倫理シグナル先行検出
- **成熟度**: 実用（商用 + 研究）
- **典拠**: sloanreview.mit.edu/projects/measuring-culture-in-leading-companies/

### 16. Bibliometrics — VOSviewer / CiteSpace

- **代表研究者**: van Eck & Waltman (VOSviewer); Chaomei Chen (CiteSpace)
- **必要データ**: Web of Science / Scopus / OpenAlex の書誌
- **計算資源**: 軽量（Java desktop）
- **適用例**: 組織の研究プロファイル化、学術連携ネットワーク、知識フロー追跡
- **成熟度**: 実用
- **典拠**: vosviewer.com; CiteSpace (Drexel)

### 17. CAQDAS — NVivo / Atlas.ti / Delve

- **代表研究者**: 商用ツール群（QSR International / ATLAS.ti GmbH）
- **必要データ**: インタビュー、フィールドノート、文書
- **計算資源**: デスクトップ
- **適用例**: 組織エスノグラフィー、grounded theory、coding scheme による形質特徴抽出
- **成熟度**: 実用（質的研究の標準）
- **典拠**: Wikipedia "CAQDAS"; Lumivero NVivo; ATLAS.ti

### 18. Phylogenetic Networks（水平伝達対応）

- **代表研究者**: Daniel Huson (SplitsTree); Andrew Francis（reticulation）
- **必要データ**: 形質マトリクス（網状進化を許容）
- **計算資源**: 中規模
- **適用例**: 組織は M&A・模倣・分社が多く tree モデル不適 → SplitsTree / NeighborNet が必要
- **成熟度**: 研究段階（言語学では一部利用、組織は **未検証**）
- **典拠**: Huson & Bryant (2006) Mol Biol Evol; SplitsTree6

### 19. クラスタ検証（内部 + 外部 + 専門家）

- **代表手法**: Silhouette、Davies-Bouldin、Calinski-Harabasz（内部）；Adjusted Rand Index、NMI（外部）；Delphi / card-sort（専門家）
- **必要データ**: ラベルあり/なし両方
- **計算資源**: 軽量
- **適用例**: ボトムアップ分類の妥当性確認
- **成熟度**: 実用
- **典拠**: STHDA cluster validation; Hubert & Arabie (1985) ARI

---

## 推奨パイプライン案

```
[1] 収集
    ├─ 構造化: Compustat / Orbis / Maddison / Seshat / 帝国データバンク / 国立公文書
    ├─ テキスト: 10-K, 有価証券報告書, ミッション, 定款, IR, 求人, Glassdoor
    ├─ 関係: Bloomberg SPLC, 取締役兼任, 提携, 出資
    └─ 質的: インタビュー, 社史, アーカイブ

[2] 前処理
    ├─ 名寄せ (LEI / GLEIF / dedupe.io / Splink)
    ├─ 言語正規化 (spaCy / GiNZA / multilingual)
    ├─ 時系列整列 (panel化, 欠損補完)
    └─ 形質スキーマ設計 (規模/年齢/業種/所有/統治/原理 — Stream A と接続)

[3] 特徴抽出
    ├─ テキスト埋め込み: SBERT / E5-multilingual / 業界専用 fine-tune
    ├─ ネットワーク埋め込み: node2vec / GraphSAGE / Heterogeneous GNN
    ├─ 構造化数値: 標準化 + 業界調整
    └─ マルチモーダル統合: 連結 or contrastive learning (CLIP風)

[4] クラスタリング / 系統推定
    ├─ ボトムアップ分類: UMAP → HDBSCAN, BERTopic, Gaussian Mixture
    ├─ 階層構造: Ward / agglomerative + dynamic tree cut
    ├─ 系統推定: 形質離散化 → MrBayes/BEAST、または NeighborNet (網状)
    └─ 時間進化: Hidden Markov / state-space で transition 推定

[5] 検証
    ├─ 内部: Silhouette, DBI, CH index
    ├─ 外部: 既存分類 (SIC/NAICS/Hannan typology) との ARI
    ├─ 予測妥当性: 生存・成長・イノベーション結果の予測力
    ├─ 専門家: Delphi panel, card-sort, member checking
    └─ 反実仮想: ABM (Mesa) で生成データに対する分類の頑健性
```

---

## ツールスタック（具体提案）

| 層 | 第一候補 | 代替 | 用途 |
|---|---|---|---|
| RDB | **PostgreSQL 16 + pgvector** | DuckDB (分析専用) | tabular + ベクトル統合 |
| OLAP | **DuckDB** | ClickHouse | パネル集計、ad-hoc |
| グラフ | **Neo4j 5 (vector index 内蔵)** | Memgraph, NetworkX in-memory | interlock/SCM/系統 |
| ベクトル | **pgvector** → **Pinecone**（スケール時） | Qdrant, Weaviate | 組織 embedding 検索 |
| 言語 | **Python 3.12** + **R 4.4** | Julia (Clustering.jl) | NLP は Python、統計は R |
| NLP | sentence-transformers, spaCy/GiNZA, BERTopic | Cohere/OpenAI Embeddings API | 多言語 |
| GNN | **PyTorch Geometric** | DGL | Heterogeneous GNN |
| ABM | **Mesa 3** | NetLogo, Repast Simphony | 反実仮想 |
| 系統 | **BEAST X**, **MrBayes 3.2**, **SplitsTree6** | RevBayes | tree + network |
| 可視化 | **Gephi**, **Cytoscape**, **Observable Plot** | VOSviewer (書誌) | 出版用 |
| 質的 | **Atlas.ti 24** | NVivo, Delve, Taguette (OSS) | コーディング |
| ワークフロー | **Snakemake** or **Prefect** | Airflow | 再現可能パイプライン |
| 実験管理 | **Weights & Biases** | MLflow | embedding/clustering 試行 |

**最小起動セット**: Postgres + pgvector + DuckDB + Python (sentence-transformers, BERTopic, networkx, Mesa) — 1 ノード（128GB RAM, GPU 24GB）で 10^4-10^5 組織は実用。10^6 規模なら Neo4j + Pinecone へ拡張。

---

## 評価方法論 — 「ボトムアップ分類が妥当」の基準

ボトムアップ分類の妥当性は単一指標では決まらない。以下を **多角的に triangulate** する必要がある：

### A. 内部整合性（Internal validity）
- **Cluster cohesion / separation**: Silhouette ≥ 0.4 を粗い基準（閾値は領域依存）
- **Stability**: bootstrap / subsampling で Jaccard 類似度 ≥ 0.75
- **Density**: HDBSCAN persistence、cluster lifetime
- **次元数感受性**: UMAP n_components を変えても主構造が保たれる

### B. 外部妥当性（External validity）
- **既存分類との比較**: SIC/NAICS/Hannan-Freeman ニッチとの ARI / NMI。完全一致ではなく「**有意に部分重複しつつ新規構造を発見**」が望ましい
- **ラベル予測力**: クラスタ ID で外部ラベル（業績、生存、イノベーション、ESG）が説明できる R²

### C. 予測妥当性（Predictive validity）
- **out-of-time**: t 期で学習した分類が t+k 期の組織挙動（成長、消滅、合併）を予測
- **out-of-domain**: 米国データで学習し日本/欧州で再現可能か
- 予測精度が偶然より有意に高ければ "real" な構造

### D. 構成概念妥当性（Construct validity）
- **専門家パネル / Delphi**: 組織研究者・実務家による card-sort で複数評定者一致度（Cohen's κ ≥ 0.7）
- **Member checking**: 当該組織自身による「自分はそのクラスタに属するか」回答
- **質的読み込み**: 各クラスタの代表組織のエスノグラフィー的記述が一貫

### E. 生成的妥当性（Generative validity）
- **ABM 検証**: ボトムアップ分類が、Mesa 等で組織進化を再現するモデルでの「種」として機能するか
- **系統樹整合**: クラスタ階層が phylogenetic tree / network と矛盾しない（Robinson-Foulds 距離小）

### F. 倫理・社会的妥当性
- 分類が**スティグマ化**や差別を生まないか
- 弱小組織の声が embedding に反映されるか（公開資料に依存すると上場大企業バイアス）

**運用基準**: A〜D のうち最低 3 つで合格、かつ E または F の議論を併記。

---

## 未確認・要追跡

| # | 項目 | 状態 | 必要なフォローアップ |
|---|---|---|---|
| U1 | 組織形態への phylogenetic methods の直接応用論文 | 言語・物質文化以外で確認できず | Currie の latest publications、CulturalEvolutionSociety 検索 |
| U2 | TNIC の非米国・非上場拡張 | Tuck の公式は米国 SEC 限定 | Orbis, FactSet で類似実装の有無 |
| U3 | Seshat の coder bias 補正 | 批判文献あり（要確認） | Slingerland et al. 反論論文 |
| U4 | Repast Simphony 最新版の組織進化モデル例 | 2024-2026 のリリース未確認 | repast.github.io の changelog |
| U5 | 日本企業向け organizational embedding pre-trained モデル | 一般的多言語 SBERT で代替可能性は高いが業界特化版は未確認 | rinna, cl-tohoku, 東大 NLP の最新 |
| U6 | Heterogeneous GNN による organizational typology の代表研究 | 2025 HGNN-CFI 以外要追加調査 | KDD/ICWSM/ASONAM 過去 3 年 |
| U7 | Glassdoor データの研究利用ライセンス | 2024 年以降の方針要確認 | Coresignal 等代替データ |
| U8 | 組織 phylogenetic network ツールの実装事例 | 概念的応用は妥当だが実装ベース論文は未発見 | SplitsTree フォーラム、Andrew Francis の研究 |
| U9 | Mesa 3 の HPC スケーリング上限 | 公式ドキュメントの数値要確認 | JOSS 2025 paper の実測値 |
| U10 | 形質離散化（character coding）の組織分野ベストプラクティス | 言語学からの転用以上の指針なし | Stream A の特徴量設計と擦り合わせ |

---

## 参考リンク（一次資料）

- ORA / CASOS — https://www.cmu.edu/casos-center/
- Hoberg-Phillips Data Library — https://hobergphillips.tuck.dartmouth.edu/
- Sentence-Transformers — https://sbert.net/
- BERTopic — https://maartengr.github.io/BERTopic/
- UMAP — https://umap-learn.readthedocs.io/
- HDBSCAN — https://hdbscan.readthedocs.io/
- NetworkX — https://networkx.org/
- igraph — https://igraph.org/
- Bloomberg SPLC — https://www.bloomberg.com/professional/dataset/global-supply-chain-data/
- BEAST — http://beast.community
- MrBayes — https://nbisweden.github.io/MrBayes/
- Seshat Databank — http://seshatdatabank.info/
- Maddison Project — https://www.rug.nl/ggdc/historicaldevelopment/maddison/
- Mesa — https://github.com/projectmesa/mesa
- NetLogo — https://ccl.northwestern.edu/netlogo/
- Repast — https://repast.github.io/
- VOSviewer — https://www.vosviewer.com/
- CiteSpace — http://cluster.cis.drexel.edu/~cchen/citespace/
- Cliodynamics Journal — https://escholarship.org/uc/cliodynamics
