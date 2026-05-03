# Phase 4 (v0.5) 完了レポート

完了日: 2026-05-03
ステータス: **Phase 4 完了基準達成** → Phase 5 (v0.7 特徴抽出・クラスタリング) 移行可能

## ロードマップ完了条件 vs 実績

| 条件 | 結果 |
|---|---|
| temporal_facet を全完全注釈ケースに展開 | ✓ 43/43 ケースに 242 facet (Phase 3 まで 28 → 242) |
| facet_type 8 軸の網羅 | ✓ 全 8 タイプ使用 (governance 75 / identity 43 / scale 39 / membership 21 / legitimation_basis 19 / resource_base 19 / territory 15 / technology 11) |
| 出典トレース | ✓ 全 facet が claim → source を持ち、source 数 108 → 204 |
| 古代-現代の通時カバー | ✓ BC3500 ウルク → 2026 MakerDAO の 5,500 年スパンで facet スライス |
| 並列実行 | ✓ Claude 7 並列チームで分担 (古代5/中世宗教教育8/前近代国家4/近世5/近代5/現代6/デジタル&extant5) |

## 実行プロセス: 7 並列 Claude チーム

| チーム | 担当 | ETL ファイル | 投入 facet 数 |
|---|---|---|---|
| A | 古代 5 (Eanna, 宰相, legio, collegia, agoge) | etl/30_phase4_ancient_facets.py | 28 |
| B | 中世宗教教育 8 (Bayt al-Hikma, 比叡山, Cluny, 安東権氏, Al-Azhar, Bologna, Cistercians, Naqshbandi) | etl/31_phase4_medieval_religious_facets.py | 45 |
| C | 前近代国家 4 (Hansa, Timar, Inca, Mansabdari) | etl/32_phase4_premodern_states_facets.py | 27 |
| D | 近世 5 (郷約, 山西, 堺, Süleymaniye, 鴻池) | etl/33_phase4_early_modern_facets.py | 26 |
| E | 近代 5 (ICRC, Toyota, UN, Mondragón, DARPA) | etl/34_phase4_modern_facets.py | 30 |
| F | 現代 6 (京セラ, BPP, Greenpeace, SEWA, Grameen, Linux Kernel) | etl/35_phase4_contemporary_facets.py | 30 |
| G | デジタル/extant 5 (Anonymous, WMF, Linux Foundation, Hadza, Iroquois) | etl/36_phase4_digital_extant_facets.py | 28 |

合計 214 新規 facet + Phase 3 までの 28 = **242 facet**

## 数字サマリ

| 指標 | Phase 3 完了 → Phase 4 完了 |
|---|---|
| 組織 (合計) | 373 → 373 |
| 完全注釈ケース | 43 → 43 |
| temporal_facet | 28 → **242** (8.6 倍) |
| organization_temporal_facet 投入対象 | 5/43 → 43/43 |
| claim | 859 → 1,073 |
| source | 108 → 204 (倍増) |

## 並列チームから報告された注目発見

### 古代 (Team A)
1. **collegia の自由結社 → 強制 corpora 転換** (3-4c): Codex Theodosianus による職業 corpora 世襲強制は、自発的互助結社が国家統制機構へ反転する稀少事例 (membership 2 段階 + governance 4 段階で記録)
2. **agoge のローマ期『再構築』** (Kennell 1995): ローマ期 agoge は古典期の連続ではなく、ヘレニズム末期-ローマ期に観光化された ritual 再演として再構築。連続性論への重要修正

### 中世宗教教育 (Team B)
1. **アル・アズハル の正統性反転**: legitimation_basis が「ファーティマ朝シーア派 (972-1171)」→「スンニ派 (1171-)」と教義そのものが反転しながら同一機関として千年継続。組織の連続性が legitimation の一貫性に依存しない稀少例
2. **Cluny vs シトー会のガバナンス対比**: Cluny は中央集権ピラミッド、シトー会は filiation 連邦 (Carta Caritatis 1119、母院-娘院 visitation + 年次 General Chapter)。同じ修道会形式で「中央集権 vs 連邦」の組織形態が世代をまたいで実験された中世の組織イノベーション

### 前近代国家 (Team C)
1. **Timar と Mansabdari の構造的同型**: 共に「土地税収を軍事動員と引き換えに分配する prebendal 体制」として同型。Mansabdari の zat/sawar 二重ランク制が地位インフレを内包し be-jagiri 危機 (1681-) に至る一方、Timar は一代限り原則で類似危機を遅延
2. **ハンザの『領土なき広域組織』**: Kontor 4 拠点の治外法権 vs インカ qhapaq ñan (王道) 網が機能的に対比可能

### 近世 (Team D)
1. **鴻池家の 3 段ジャンプ**: 酒造 (1600s) → 両替商 (1656) → 三和銀行系譜 (1933)、resource/identity が連続変容しつつ法人実体が三菱UFJまで継続。「組織の死と転生」の好例で status=transformed が 3 度の質的飛躍を含む
2. **スレイマニエの waqf 自給→国営化反転**: 1557-1839 はスルタン寄進による完全自給経済 (mosque + medrese 4 + 病院 + 炊き出し)、Tanzimat (1839) 中央集権化、共和国 (1923) 国営化 + medrese 廃止 (1924) と、自律的宗教複合体が国家管理対象へ転倒

### 近代 (Team E)
1. **ICRC の正統性 facet 二層構造**: Geneva Conventions (1864-) を恒常的正統性源泉とする一方、WWII 期 (1939-1949) を独立 facet として「ホロコースト沈黙批判による中立性危機」を記録。同一 facet_type で恒常層と危機層が時間的に重なる構造
2. **DARPA の名称往復 (ARPA→DARPA→ARPA→DARPA)**: 1972/1993/1996 改名は単なる rebranding ではなく、デュアルユース vs 国防専念の自己定義の揺れマーカー

### 現代 (Team F)
1. **SEWA Bank (1974) は Grameen Bank (1983) に 9 年先行**: Yunus 物語が支配的だが、女性自営業者 4,000 人共同出資の協同組合銀行は SEWA が先。Trade Union + Cooperative Federation の二層構造も独自
2. **BPP の identity facet 転換 (1969-)**: 「武装防衛」から「Survival Programs」へ。同時期に governance 軸では FBI COINTELPRO 弾圧と Newton-Cleaver 分裂が並行進行、identity と governance の軌道分離が観察可能

### デジタル/extant (Team G)
1. **governance facet が最多 (10/28)**: WMF の ED/CEO 4 期、Linux の merger→umbrella 移行、MakerDAO 同様の DAO 系の段階分化、Iroquois の dual governance など、デジタル/伝統を問わず統治形態の変容が時系列分析の中心軸
2. **Anonymous の "diffuse" facet (2013-, open-end)**: brand 継続性と組織実体希薄化の並走を valid_to=NULL で表現。確定的 'end' を識別困難な分散型組織への temporal_facet 設計の有効性を確認

## facet_type 分布の解釈

```
governance         75  (全 facet の 31%)
identity           43  (18%)
scale              39  (16%)
membership         21
legitimation_basis 19
resource_base      19
territory          15
technology         11
```

- **governance 偏重 (31%)** は、組織変容を「統治形態の再編」として観察した結果。Mintzberg/Aldrich/Williamson の組織理論との整合性
- **technology 軸が最も希薄 (11)** は、技術変化を組織変容として記録する難しさを示す。Phase 5 の機能ベクトル分析で要再検証
- **territory 15 件は前近代国家・帝国に偏在** (Inca, Mansabdari, Hansa, Timar 等)。現代多国籍企業の territory はむしろ "global" と一括化されがちで脱領域化を反映

## 設計上の発見

### temporal_facet の有用性
- **同一 facet_type で複数スライス共存可能** (例: ICRC の legitimation_basis を恒常層 + 危機層で並列記録)
- **valid_to=NULL の柔軟運用**: Anonymous の "diffuse" 状態のような open-end 継続を扱える
- **precision メタデータの活用**: 古代史は century/period が中心、近代は year/exact

### Stream J 教訓の維持
- 全 facet で `value_kind` を 5 値 (present/absent/partial/unknown/inapplicable) で記録、'unknown' を 'absent' に潰さず
- 不確実な facet は confidence < 0.6 + interpretation_note 明記

### IDSov 配慮
- Hadza (Marlowe 2010) と Iroquois (Mann 2000 + Six Nations 公式) の facet 11 件全てに `interpretation_note` で IDSov 配慮を明示

## 残課題 (Phase 5 へ)

1. **technology 軸の補強**: 現状 11 件と最少。組織技術 (記帳法、通信、生産方式) の facet 化を追加調査
2. **時代別偏重の補正**: medieval 13 + early_modern 8 + extant 7 = 28 (65%)、modern/contemporary が手薄。20-21c の追加注釈
3. **facet ベクトルでのクラスタリング**: 25 機能 + 8 facet 軸を組み合わせた特徴ベクトルで Phase 5 の clustering へ
4. **Phase 5 へ向けた特徴抽出パイプライン**: codex 13 の clustering スクリプトを facet 込みで再実行

## 成果物 (Phase 4)

- ETL: etl/30 〜 etl/36 (7 ファイル) + etl/40_facet_overview.py
- 可視化: data/facet_overview.html (43×8 マトリクス、新規)
- 再生成: data/genealogy_network.svg / data/network_stats.json / data/function_heatmap.html / data/lifecycle_timeline.svg / data/statistics_report.md

## ロードマップ進捗

- v0.0 事前リサーチ: ✓ 2026-05-02
- v0.1 Phase 1 (claim-based core, 5 cases): ✓ 2026-05-02
- v0.2 Phase 2 (diversity 6 cases): ✓ 2026-05-02
- v0.3 Phase 3 (genealogy network, 18 cases): ✓ 2026-05-02
- v0.3+ 20-team batch (43 cases, 5,500 year span): ✓ 2026-05-03
- **v0.5 Phase 4 (temporal_facet 全 43 cases 展開): ✓ 2026-05-03**
- v0.7 Phase 5 (特徴抽出・clustering): 次フェーズ
- v0.9 Phase 6 (系譜推定・専門家レビュー): 計画
- v1.0 Phase 7 (公開版・論文草稿): 計画
