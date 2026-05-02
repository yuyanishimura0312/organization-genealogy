# Stream K — Phylogenetic Network / 水平伝達対応の系統推定手法

## 概要

組織は M&A・スピンオフ・模倣により水平伝達 (HGT) が頻繁で、tree モデル前提の標準的 phylogenetics は直接適用困難。本書は (1) 網状進化を扱う手法群 (SplitsTree/NeighborNet, PhyloNet, NetRAX, HyDe, median-joining, TCS)、(2) 言語学・文化進化・写本学の先行例、(3) 組織分野の既存応用 (McCarthy 組織クラディスティクス、Phillips 法律事務所系譜)、(4) 形質コーディング戦略、(5) v0.5/v1.0 段階採用案を整理する。組織への直接 phylogenetic network 応用は**部分的に存在するが未確立**。

## 主要手法（12件）

| # | 名称 | 代表研究者 | 必要データ | 計算資源 | 組織応用実現性 | 典拠 |
|---|---|---|---|---|---|---|
| 1 | **NeighborNet (SplitsTree)** | Bryant & Moulton 2004; Huson | 距離行列 (n×n) | 軽量 (数百 taxa まで秒〜分) | **高**: 形質→距離化が容易、まず「組織は tree 状か網状か」を可視診断 | [Bryant & Moulton 2004](https://academic.oup.com/mbe/article/21/2/255/1187993), [Frontiers 2023 改良版](https://www.frontiersin.org/journals/bioinformatics/articles/10.3389/fbinf.2023.1178600/full) |
| 2 | **Split Decomposition / Splits graph** | Bandelt & Dress; Huson SplitsTree6 | 距離 or 二値形質 | 軽量 | **高**: 探索的解析の第一手 | [SplitsPy](https://github.com/husonlab/SplitsPy) |
| 3 | **Median-Joining Network (MJN)** | Bandelt et al. 1999 | 二値/多状態 character 行列 | 軽量 | **中〜高**: 組織形質のハプロタイプ的扱い、ancestral median ノードを推定可 | [Bandelt 1999 PubMed](https://pubmed.ncbi.nlm.nih.gov/10331250/) |
| 4 | **TCS (Statistical Parsimony)** | Templeton, Crandall, Sing | 配列 or 離散形質 | 軽量 | **中**: 短距離リネージ向き、組織の直近世代に有効 | [tcsBU](https://academic.oup.com/bioinformatics/article/32/4/627/1744448) |
| 5 | **PhyloNet (ML/Bayesian network)** | Luay Nakhleh ら (Rice) | gene trees or 配列、複数遺伝子座 | 中〜重 (数十 taxa で時間〜日) | **中**: 「複数特徴系列」を gene-tree 類似に置換できれば適用可 | [PhyloNet 2018 SystBiol](https://academic.oup.com/sysbio/article/67/4/735/4921127), [Zhu et al. 2018 PLOS CB](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005932) |
| 6 | **PhyloNetworks.jl** | Solís-Lemus, Ané | concordance factors / gene trees | 中 | **中**: Julia 製、SNaQ で reticulation 数推定 | [Solís-Lemus 2017 MBE](https://academic.oup.com/mbe/article/34/12/3292/4103410) |
| 7 | **NetRAX (ML phylogenetic network)** | Lutteropp, Kozlov, Stamatakis | partitioned MSA | 中 (RAxML-NG ベース) | **中**: 形質→疑似配列化で適用可 | [NetRAX 2021](https://www.researchgate.net/publication/354264707_NetRAX_Accurate_and_Fast_Maximum_Likelihood_Phylogenetic_Network_Inference) |
| 8 | **HyDe (Hybridization Detection)** | Blischak et al. 2018 | site pattern frequencies (3 taxa triples) | 軽〜中 | **中**: M&A の親種同定に類比、γ 推定で混合比定量 | [Blischak 2018 SystBiol](https://academic.oup.com/sysbio/article/67/5/821/4944070) |
| 9 | **D-statistic (ABBA-BABA)** | Patterson, Green et al. | 4 taxa, 配列 | 軽量 | **中**: 「組織 A は B より C と多く形質共有」検定として転用可。ただし rate variation で偽陽性高 [Frankel et al. 2023](https://academic.oup.com/sysbio/article/72/6/1357/7271365) |
| 10 | **BEAST 2 + bModelTest + SNAPPER** | Bouckaert ら | 配列 or SNP 様データ | 重 (MCMC、日単位) | **中**: 時間 calibration が組織創業年と相性良。SNAPPER は biallelic marker 専用 | [BEAST 2.5 PLOS CB](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006650), [bModelTest BMC EE 2017](https://link.springer.com/article/10.1186/s12862-017-0890-6) |
| 11 | **T-REX (HGT inference)** | Boc, Diallo, Makarenkov | 種樹+遺伝子樹 | 中 | **中**: 明示的 HGT イベント検出、組織の模倣・人材移動類比 | [T-REX 2012](https://pubmed.ncbi.nlm.nih.gov/22675075/) |
| 12 | **Phyloformer / NeuralNJ / GAN-phylo** | Nesterenko et al. 2025; 他 2025 | 訓練データ + MSA | 重 (GPU 必要) | **低〜中**: 訓練データ不足、組織には現時点で不向き。要追跡 | [Phyloformer MBE 2025](https://academic.oup.com/mbe/article/42/4/msaf051/8069202), [GAN-phylo PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10500083/), [End-to-end DL MBE 2025](https://academic.oup.com/mbe/article/42/11/msaf260/8300277) |

補助ツール: **phangorn (R)** — NeighborNet, splits, networx を R で軽量に回せる ([phangorn](https://klausvigo.github.io/phangorn/), [Networx vignette](https://cran.r-project.org/web/packages/phangorn/vignettes/Networx.html))。

理論的基盤: Andrew Francis (Western Sydney) のラベル可能ネットワーク・tree-based network 論。「ネットワークは tree+追加 arc で表現可能か」を 2-SAT で判定でき、組織のように「基本骨格は系譜的、ただし水平流入が局所的」な構造のモデル化に適する ([Francis & Steel 2015 SystBiol](https://academic.oup.com/sysbio/article/64/5/768/1686032), [Labellable Networks 2023](https://link.springer.com/article/10.1007/s11538-023-01157-0))。

## 形質コーディング戦略

組織を「taxa」、組織形態的特徴を「character」として離散化する基本戦略:

1. **二値形質 (presence/absence)**: 「事業部制を持つか」「ストックオプション制度があるか」「OKR 採用」など。最も扱いやすく、median-joining/MJN・split decomposition と相性良。前提: 各形質が独立に獲得・喪失され得る (実際は連動するため要慎重)。
2. **多状態順序形質 (Mk model 適用可)**: 「資本構造 (家族/同族→分散→上場→PE)」「意思決定形態 (個人→合議→マトリクス)」など段階性のある特徴。Pagel 1994 Mk モデルが基本枠組 [Harmon PCM 7章](https://lukejharmon.github.io/pcm/chapter7_introdiscrete/)。
3. **連続形質**: 従業員数、売上、レイヤー数等。Parins-Fukuchi 2018 [SystBiol](https://academic.oup.com/sysbio/article/67/2/328/4102005) が「連続形質は二値化より phylogenetic signal を強く保持」を示した。
4. **配列型コーディング**: 組織を「ミーム配列」として、各ポジションに事業領域・人事制度・技術スタックを並べる。RAxML-NG/NetRAX/BEAST 2 のような ML/Bayesian ツールに直接投入可。
5. **行列由来距離**: 組織アンケート・有報テキストの埋め込み距離 → NeighborNet。最も実装容易。

**暗黙の理論的前提と注意点**:
- 文字独立性の仮定 (実際は組織制度はバンドル的に伝播)。
- 同質的進化率 (Mk) — 組織変化は punctuated。relaxed clock 必須。
- ホモプラジー (収斂) と相同 (継承) の区別 — 言語学 cognate 判定に学ぶべき。
- 「個体性 (taxon の境界)」: 子会社・分社・JV を 1 taxon と数えるかでトポロジが変わる。事前に「組織種 (organizational species)」概念を定義要。
- 文化進化分野の Greenhill, Currie & Gray 2009 は「Bayesian phylogenetics は 1000 年あたり 15% borrowing でもトポロジは頑健」と示した ([Greenhill et al. 2009 ProcB](https://royalsocietypublishing.org/doi/10.1098/rspb.2008.1944))。組織の高 HGT も**完全否定要因ではない**。

## 推奨パイプライン

組織形態データ → 段階的に網状性を確認・モデル化:

```
[1] 形質行列構築
    - 二値形質 + 連続形質 + テキスト埋め込み
    - taxa = 組織 (時点スナップショット or 単一観測)

[2] 探索的網状性診断 (R/phangorn or SplitsTree6)
    - NeighborNet で splits graph 描画
    - Δ-score / Q-residual で「tree 度」測定
    - → tree 状なら従来 phylogenetics で十分; 網状なら次へ

[3] HGT イベント検出
    - HyDe: 3 taxa triple ごと γ (混合比) 推定
    - D-statistic: M&A・模倣の方向性検定
    - → 組織ごとの「親候補」を抽出

[4] 明示的ネットワーク推定
    - PhyloNet (Bayesian, 小規模 <30 taxa)
       or PhyloNetworks.jl SNaQ (中規模)
       or NetRAX (大規模)
    - reticulation 数 k を AIC/BIC で選択

[5] 時間 calibration
    - BEAST 2 + bModelTest + relaxed clock
    - 創業年・大規模再編年を tip date / node calibration として使用

[6] 検証
    - bootstrap / posterior probability
    - 既知 M&A 関係との一致率
    - 言語・文化進化の robustness 文献を参照
```

## 直接応用先行研究の有無

**部分的に存在。完全な「organizational phylogenetic network」は未確立。**

実在する先行研究:
- **Ian P. McCarthy et al. (1995, 1997, 2000)**: 製造組織のクラディスティクス。自動車組立工場の cladogram を構築し、「組織形態は分岐進化する」を実証 ([McCarthy 1995](https://www.emerald.com/insight/content/doi/10.1108/09576069510099365/full/html), [McCarthy 2000 JMTM](https://www.emerald.com/insight/content/doi/10.1108/09576060010303631/full/html), [Building a manufacturing cladogram](https://www.researchgate.net/publication/247831707_Building_a_manufacturing_cladogram))。**ただし tree 法のみで網状性は未対応**。
- **Damon J. Phillips (2002, 2005, ASQ)**: シリコンバレー法律事務所 1946–1996 の parent-progeny transfer 研究。「組織系譜 (genealogy) のスピンオフ」を計量分析、ジェンダー不平等の世代継承まで踏み込む ([Phillips 2002 ASQ](https://scholar.google.com/scholar_lookup?title=A+genealogical+approach+to+organizational+life+chances), [Phillips 2005 ASQ](https://journals.sagepub.com/doi/10.2189/asqu.2005.50.3.440))。**ただし phylogenetic ツールは使わず統計回帰**。
- **Ito 1995 SMJ**: 日本企業の親子 (parent-subsidiary) 系譜構造 ([Ito 1995](https://sms.onlinelibrary.wiley.com/doi/abs/10.1002/smj.4250151004))。
- **Toward a Phylogenetic Reconstruction of Organizational Life (Journal of Bioeconomics 2005)** — 組織の phylogenetic 再構成を提案 ([Springer Link](https://link.springer.com/article/10.1007/s10818-005-5245-5))。
- **Fairchildren (Computer History Museum)**: Fairchild Semiconductor → 100+ 半導体企業のスピンオフ家系図。学術ではないがデータ源として有用 ([CHM blog](https://computerhistory.org/blog/fairchild-and-the-fairchildren/))。

**未確立の領域**: 「組織を taxa とし NeighborNet/PhyloNet で網状進化を推定し M&A・模倣を reticulation node として明示的に検出した論文」は確認できず。**Stream K の中核仮説 = この空白を埋めること**として位置付け可能。隣接分野 (写本学 stemmatology — Spencer, Wachtel, Howe による New Testament median network ([Beyond the tree of texts](https://academic.oup.com/dsh/article-abstract/28/4/504/1076624?redirectedFrom=fulltext&login=false), [Bayesian manuscript transmission](https://academic.oup.com/dsh/article/39/1/258/7477852))) と code clone genealogy (Kim, Sazawal et al. 2005 ([Code Clone Genealogies](https://web.cs.ucla.edu/~miryung/Publications/esecfse05-clonegenealogy.pdf))) は手法的隣人。

## 我々のプロジェクトでの段階的採用案

### v0.5 (最小実装、3–6ヶ月)
- **目的**: 「組織は tree か網状か」を実証データで可視診断する。
- 形質行列: 30–50 組織 × 30–50 二値/連続形質 (有報・採用ページ・組織図から抽出)
- **手法**: phangorn (R) で NeighborNet + Δ-score、SplitsTree6 で可視化
- **派生**: median-joining network で「最近祖先組織形態」推定
- **成果物**: splits graph PDF + 「組織進化は X% 程度 reticulate」定量レポート
- **計算資源**: ノート PC で可

### v0.7 (中間、6–12ヶ月)
- HyDe で 3-taxa triples ごとに M&A・模倣の混合比 γ を計算、既知 M&A 一覧と照合し検出力評価
- D-statistic で「業界 A は業界 B より C と形質共有」の有意性検定
- 言語学 (Indo-European, Bantu) の robustness 知見を組織に適用、HGT 率の上限を推定

### v1.0 (本格、12–24ヶ月)
- PhyloNet (Bayesian network MCMC) または NetRAX で reticulation を含む明示的ネットワーク推定
- BEAST 2 + bModelTest + relaxed clock で時間 calibration (創業年・再編年が tip/node date)
- Andrew Francis の tree-based network 理論で「組織進化は tree-based か否か」を 2-SAT で判定
- 比較対象: McCarthy 製造クラディスティクス、Phillips 法律事務所系譜、Fairchildren データ

### v1.5 (発展)
- Phyloformer 等 deep learning 系の組織応用可能性を再評価 (2026 時点で訓練データ整備状況による)
- ノード embedding (テキスト + 構造) ベースの「系譜推定もどき」を baseline として並走、phylogenetic 法と比較
- topic model 由来の document phylogeny との統合 (有報・社内文書の通時 LDA → tree)

## 未確認・要追跡

- **SNAPPER の network 拡張版**: 現状は species tree 用。biallelic 組織形質への直接適用例なし。要文献追跡。
- **Dnglossia / GenPhylo**: 検索でヒットせず。実在性未確認。ユーザー指定だが捏造を避けるため**未確認と明記**。次回 WebSearch 必要。
- **Kandler の loanword model**: 検索結果は language shift / language competition の reaction-diffusion モデルが中心。「loanword 専用モデル」は別論文の可能性、要追加検索。
- **2025 以降の deep generative phylogenetics の組織応用例**: Phyloformer は配列前提、組織形質には未適用。
- **写本学 stemmatology の組織応用**: Spencer/Wachtel/Howe の median network 手法が組織文書 (規程・社内マニュアル) に転用可能か未確認。
- **「組織種 (organizational species)」の operationalization**: 子会社・JV・分社をどう数えるか — 組織論側の典拠 (Hannan-Freeman 組織生態学等) と Stream A/F との突き合わせ要。
- **網状進化下での divergence date 推定の歪み**: Greenhill et al. 2009 が「年代推定は borrowing で過小評価傾向」と指摘。組織創業年の calibration 戦略に影響。
