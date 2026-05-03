# Paper Outline — 組織系譜論文の骨子

作成日: 2026-05-02
担当: Phase 3 並列タスク #Q (Paper Drafting)
基盤: 18 完全注釈ケース、348 organization、374 claim、16 relation、3 連結成分。詳細解釈は `plan/scholarly_implications.md`。

> 本書は論文の骨子（タイトル候補、Abstract、Section 構成、Visualizations、Bibliography）であり、本文ドラフトではない。Phase 4 完了後に本文化する。

---

## 1. Title 候補（3 案）

**(A)** *Organizations as Reticulate Lineages: A Network-Based Genealogy of 18 Cases Across 1500 Years*
- 焦点: tree でなく network であること、長期史 reticulate 構造。
- 想定読者: Organization Studies / ASQ。

**(B)** *From Rule to Mimesis: Function, Identity, and Isomorphism in a Cross-Era Organizational Database*
- 焦点: medieval succession/schism と contemporary mimetic の対比、S5 Policy/Identity の中心性。
- 想定読者: Journal of Organization Design / AMR。

**(C)** *The Identity-First Organization: Policy and Memory as the Recurring Vehicles of Long-Run Organizational Continuity*
- 焦点: VSM S5 が 13/18 で最頻出という発見、autopoiesis × VSM のハイブリッド読み。
- 想定読者: Organization Studies / Organization Science（理論寄り）。

推奨第一候補は (A)。経験的発見（reticulate ネットワーク + 1500 年スパン）が最も明確に伝わり、phylogenetic network 文献（Stream K）にも橋渡し可能。

---

## 2. Abstract（250 語、英文想定）

> Note: 以下は英文 250 語の構造案を日本語ドラフトで示す。本文化時に英訳。

組織を「生命」として捉える研究プログラムは、Hannan and Freeman の個体群生態学、Luhmann のオートポイエーシス、Beer の Viable System Model、DiMaggio and Powell の制度的同型化など、互いに競合する複数の系譜から構成されてきた。本論文は、6 世紀から現代までの 18 ケース（Benedictine, Cluny, Cistercian, University of Bologna, Hanseatic League, VOC, Inca Empire, Mughal Mansabdari, Ashanti Kingdom, Mitsui, Konoike, Mt. Hiei, Mondragón, Grameen Bank, Wikimedia Foundation, Linux Foundation, MakerDAO, Hadza band）を、組織を claim/event/relation/function の束として記述する関係データベースに完全注釈し、77 の機能記録と 16 の系譜関係を抽出した。三つの主要発見を報告する。第一に、12 ノード／約 1500 年スパンの最大連結成分は tree ではなく reticulate network であり、組織系譜は succession/schism の縦方向と knowledge_transfer/mimetic_isomorphism の水平方向の両方で構成される。第二に、Beer VSM の S5 Policy/Identity が 18 ケース中 13 で記録され、Miller の Boundary（11）/ Memory（10）/ Ingestor（9）を上回る最頻機能となる一方、いずれの機能も 18 ケース全体で普遍的ではない。第三に、relation_type は時代依存的に偏り、medieval は succession+schism、contemporary は mimetic_isomorphism が支配的であり、DiMaggio-Powell の制度的同型化が現代組織で支配的メカニズムであることを支持する。本研究はまた、個体境界の曖昧さ（三井グループ、Wikimedia、MakerDAO の法的・成員・意思決定境界の不一致）を方法論的限界として明示し、複数境界での感度分析と古代・非西洋・女性組織への拡張を次の研究課題として提示する。

語数概算: 約 600 文字 ≒ 英文 250 語。実装時に縮約する。

---

## 3. Sections（6 構成）

### 3.1 Section 1: Introduction（約 1500 語）

- 問い: 組織を「生命」として捉える諸理論を、長期史の経験データで弁別できるか。
- 動機: 組織は M&A・スピンオフ・模倣で水平伝達が頻繁であり、tree モデルを前提とした生物学的アナロジーは部分的にしか効かない。一方、Luhmann の決定の連鎖、Beer の再帰的サブシステム、DiMaggio-Powell の制度的同型化、Hannan-Freeman の個体群密度はいずれも単独では長期史を説明できない。
- 貢献の宣言:
  1. 6 世紀–2017 年の 18 ケースを claim/event/relation/function の束として注釈した最初の関係データベース。
  2. 組織系譜が reticulate network である経験的証拠。
  3. S5 Policy/Identity の超時代的中心性と、medieval/contemporary 間の relation_type 分布変化。
  4. 個体境界の曖昧さを「分析者が選ぶ境界が結果を決める」方法論的限界として明示。
- 構成案内。

### 3.2 Section 2: Theoretical Background（約 2500 語）

- 4 系譜の比較: Spencer（批判対象）、Hannan-Freeman、Maturana-Luhmann、Beer。
- 補正理論: DiMaggio-Powell (1983)、Meyer-Rowan (1977)、Pfeffer-Salancik (1978)、Suchman (1995)、Greif (1989, 2006)、North (1990)、Padgett-Powell (2012)。
- 死亡論: Stinchcombe (1965)、Hannan-Freeman (1984)、Brüderl-Schüssler (1990)、Barron-West-Hannan (1994)。
- 系譜推定論: Mesoudi (2011)、Greenhill et al. (2009)、phylogenetic network 系（Bryant-Moulton 2004; Solís-Lemus & Ané 2017）。
- 仮説提示:
  - **H1 (Reticulate)**: 長期史の組織系譜は tree よりも network トポロジに整合する。
  - **H2 (Identity-First)**: 時代を超えて再生産される機能は S5 Policy/Identity が最頻である。
  - **H3 (Era-Dependent Isomorphism)**: medieval は succession/schism、contemporary は mimetic isomorphism が支配的である。

### 3.3 Section 3: Method and Data（約 2500 語）

- データモデル v0.3: organization / claim / event / relation / function_record / impact_record / source / organization_form_assignment（codex2、codex4 DDL v0.3）。
- 機能 taxonomy: codex7（Miller 20 + Beer VSM 5）。
- ケース選定: 6 大陸 / 6 世紀–2017 年 / 修道会、商業会社、家業、宗教制度、財団、DAO、協同組合、狩猟採集バンド、非西洋国家。サンプリング戦略は theoretical sampling（Glaser-Strauss 1967 / Eisenhardt 1989）。
- 注釈プロセス: 各ケースで claim 約 20、event 約 2、function_record 約 4–6、impact_record 約 2、relation 約 1（隣接ケースとの接続あり）。すべての claim に source を紐付け、confidence と claim_value_kind を記録。
- 関係抽出: relation_type は succession / schism / knowledge_transfer / mimetic_isomorphism / competition / dominance / resource_exchange の 7 候補から選択（Phase 3 では 5 種使用）。
- ネットワーク分析: 連結成分、次数中心性、relation_type 分布。`etl/10_network_statistics.py` による再現可能な計算。
- 限界明示:
  - サンプル小（18 ケース、個体群統計には不十分）。
  - 古代（BC500 以前）未含。
  - 非西洋・女性組織カバレッジ不足。
  - 単一 coder（複数 coder の κ 未計算）。

### 3.4 Section 4: Findings（約 3500 語）

#### 4.1 Network Topology（H1 検証）

- 18 ノード / 16 エッジ / 3 連結成分。最大成分 12 ノード（修道会＋商業＋大学＋協同組合＋財団＋DAO 横断）、中成分 5 ノード（東アジア家業＋宗教＋非西洋国家）、孤立 1 ノード（Hadza）。
- 最大成分内のエッジは succession 2、schism 1、knowledge_transfer 6、mimetic_isomorphism 6、competition 1。tree 仮定では schism と mimetic がループを作るため不適合。
- 中心性上位ノード: Benedictine（out-degree 3、規則供給源）、Wikimedia（in 1 / out 2、現代財団型ガバナンス媒介点）、Cistercian（in 2 / out 1、改革分派の中継点）。
- Phylogenetic network 適用候補（Stream K の NeighborNet 等）は今回未実施。次の研究課題として残す。

#### 4.2 Function Distribution（H2 検証）

- 25 機能のうち 10 機能は 1 件以上の記録、15 機能は記録なし（M05 Converter, M08 Extruder, M09 Motor, M10 Supporter, M11–M16, M20 など low-level 物理サブシステム）。
- 上位 4 機能: S5 Policy/Identity 13、M02 Boundary 11、M17 Memory 10、M03 Ingestor 9。Universal な機能はゼロ。
- 組織種別パターン:
  - 修道院: M01 Reproducer + S5 + M17 + M02。
  - 古代官僚制: M03 + M17 + M18 + S1。
  - 家業（Ie）: M01 + M17 + S5 + M03。
  - 特許貿易会社: M02 + M03 + M06 + M17。
  - 狩猟採集バンド: M02 + M04 + M18 + S5。
- Miller 53 records / VSM 24 records。VSM は機能あたり頻度（4.8 r/機能）で Miller（2.65 r/機能）を上回る。
- S5 集中の三仮説（注釈アーティファクト / Identity-first / 規範的選択効果）と現データでの非識別性。

#### 4.3 Era-Dependent Relation Distribution（H3 検証）

- medieval（7 ケース）: succession 2 + schism 1 + knowledge_transfer 2（Cistercian → Bologna 等）が中心。
- early_modern（5 ケース）: knowledge_transfer 中心（Hanseatic → VOC、ボローニャ → 各地大学）。
- contemporary + extant + postwar（6 ケース）: mimetic_isomorphism 6 が支配的（Wikimedia → Linux/MakerDAO、Mondragón → Grameen、VOC → MakerDAO）。
- DiMaggio-Powell (1983) の三型のうち本データで物理化されたのは mimetic のみ。coercive と normative は relation_type に未実装。

#### 4.4 East-West Asymmetry

- 東アジア中成分（三井／鴻池／延暦寺）と非西洋孤立（Hadza、Inca、Mansabdari、Ashanti）は、relation vocabulary の偏りを反映。
- 「家」「場」「名跡」「制度的保護」は法人格中心の relation_type では捕捉しにくい。codex3 の指摘と整合。

### 3.5 Section 5: Discussion（約 2500 語）

- H1 支持: 組織系譜は reticulate network。tree モデルは不適切。Padgett-Powell (2012) の autocatalytic 多重ネットワーク論と整合。
- H2 部分支持: S5 Policy/Identity は最頻だが universal ではない。Luhmann (1995, 2000) の autopoiesis 解釈と整合する一方、注釈アーティファクト仮説を排除できない。
- H3 支持: 時代依存的 isomorphism。DiMaggio-Powell (1983) の mimetic が現代で支配的。Greif (2006) と North (1990) の path-dependent 制度進化が medieval に整合。
- 4 系譜の弁別評価:
  - Hannan-Freeman: 概念語彙は有用、定量検定は不可（サンプル小）。
  - Luhmann: 親和性最大、operationalization 未完。
  - Beer: function taxonomy として最適、規範化リスク要注意。
  - Spencer: 採用せず、進歩史観チェックリストとして使用。
- 個体境界の曖昧さ: 三井 / Wikimedia / MakerDAO / Mondragón で法的・成員・意思決定境界が不一致。境界選択そのものが分析対象。
- 機能主義的後知恵への自己注意: status (active/extinct) を function_record に逆算しない設計は維持しているが、論文叙述で滑りやすい。

### 3.6 Section 6: Limitations and Future Research（約 1500 語）

- データ面: サンプル小、古代不足、非西洋・女性組織不足、単一 coder。
- 方法面: 境界選択の感度未測定、coder bias κ 未計算、時間粒度が粗い、phylogenetic network 未適用。
- 理論面: 生命メタファー一枚岩化を完全に回避できていない。正統性論・権力論の接合が薄い。
- 次の研究課題:
  1. Phase 4 temporal facets 実装。
  2. ケース 50–100 拡大。
  3. relation_type 拡張（coercive / normative / resource_flow / decision_link）。
  4. coder bias 監査（複数 coder + κ）。
  5. NeighborNet / SplitsTree6 で Δ-score 測定。
  6. Seshat との entity matching。
  7. 三重境界での感度分析。

---

## 4. Key Visualizations（5 点）

1. **Figure 1: Genealogy Network (overall)** — 18 ノード／16 エッジ／3 連結成分。relation_type を色分け。`data/genealogy_network.svg` を改訂し、ノード形状を era、色を connected_component で塗り分け。図注で「ノードはスナップショットの集約表示」と reification 注意を明記。

2. **Figure 2: Function Heatmap (organization × function)** — 18 ケース × 25 機能のバイナリ／頻度ヒートマップ。`data/function_heatmap.html` を pdf 化。S5 行と Boundary/Memory 行を強調。Universal 行が無いことを明示。

3. **Figure 3: Relation Type Distribution by Era** — bar chart。x 軸 = era（medieval / early_modern / postwar / contemporary / extant）、stacked bar = relation_type 比率。H3 の era-dependent isomorphism を可視化。

4. **Figure 4: Largest Connected Component (zoomed)** — 12 ノード成分のみ。Benedictine → Cluny → Cistercian → Bologna → … → MakerDAO の主要パスを強調表示。約 1500 年スパンを時間軸に展開。

5. **Figure 5: Boundary Ambiguity Cases** — 三井 / Wikimedia / MakerDAO / Mondragón について、法的境界 / 成員境界 / 意思決定境界 / 資産境界の 4 重円を可視化。Phase 4 temporal facets の必要性を視覚的に示す。

補助テーブル:
- **Table 1**: 18 ケースの基本属性（name, era, status, type, founding/dissolution year）。
- **Table 2**: 25 機能の頻度と組織カバレッジ（function_coverage.md より）。
- **Table 3**: 16 relation の era × type クロス表。
- **Table 4**: codex1 の 5 罠 × Phase 3 自己評価ステータス。

---

## 5. Bibliography（40–50 件、research A–L から実在文献のみ抽出）

> 採用基準: research/A–L で典拠が明示されており、年・著者・媒体（DOI / ISBN / 雑誌巻号）まで確認できているもののみを列挙。要追跡・未確認文献は除外。

### 古典理論（生命・システム・サイバネティクス）

1. Beer, S. (1972). *Brain of the Firm*. Allen Lane.
2. Beer, S. (1979). *The Heart of Enterprise*. Wiley.
3. Beer, S. (1985). *Diagnosing the System for Organizations*. Wiley.
4. Maturana, H. R., & Varela, F. J. (1980). *Autopoiesis and Cognition: The Realization of the Living*. D. Reidel. DOI: 10.1007/978-94-009-8947-4.
5. Miller, J. G. (1978). *Living Systems*. McGraw-Hill.
6. Luhmann, N. (1995). *Social Systems*. Stanford University Press.
7. Morgan, G. (1986/2006). *Images of Organization*. SAGE.

### 個体群生態学・進化経済学

8. Hannan, M. T., & Freeman, J. (1977). The Population Ecology of Organizations. *American Journal of Sociology*, 82(5), 929–964. DOI: 10.1086/226424.
9. Hannan, M. T., & Freeman, J. (1984). Structural Inertia and Organizational Change. *American Sociological Review*, 49(2), 149–164.
10. Hannan, M. T., & Freeman, J. (1989). *Organizational Ecology*. Harvard University Press.
11. Hannan, M. T., & Carroll, G. R. (1992). *Dynamics of Organizational Populations*. Oxford University Press.
12. Carroll, G. R., & Hannan, M. T. (2000). *The Demography of Corporations and Industries*. Princeton University Press.
13. Stinchcombe, A. L. (1965). Social Structure and Organizations. In J. G. March (Ed.), *Handbook of Organizations* (pp. 142–193). Rand McNally.
14. Brüderl, J., & Schüssler, R. (1990). Organizational Mortality: The Liabilities of Newness and Adolescence. *Administrative Science Quarterly*, 35(3), 530–547.
15. Barron, D. N., West, E., & Hannan, M. T. (1994). A Time to Grow and a Time to Die: Growth and Mortality of Credit Unions in New York City, 1914–1990. *American Journal of Sociology*, 100(2), 381–421.
16. Aldrich, H. E. (1999). *Organizations Evolving*. SAGE.
17. Nelson, R. R., & Winter, S. G. (1982). *An Evolutionary Theory of Economic Change*. Harvard University Press.
18. Penrose, E. T. (1959). *The Theory of the Growth of the Firm*. Blackwell.

### 制度論・正統性・資源依存

19. DiMaggio, P. J., & Powell, W. W. (1983). The Iron Cage Revisited: Institutional Isomorphism and Collective Rationality in Organizational Fields. *American Sociological Review*, 48(2), 147–160.
20. Meyer, J. W., & Rowan, B. (1977). Institutionalized Organizations: Formal Structure as Myth and Ceremony. *American Journal of Sociology*, 83(2), 340–363.
21. Pfeffer, J., & Salancik, G. R. (1978). *The External Control of Organizations: A Resource Dependence Perspective*. Harper & Row.
22. Scott, W. R. (2014). *Institutions and Organizations: Ideas, Interests, and Identities* (4th ed.). SAGE.
23. Suchman, M. C. (1995). Managing Legitimacy: Strategic and Institutional Approaches. *Academy of Management Review*, 20(3), 571–610.
24. Granovetter, M. (1985). Economic Action and Social Structure: The Problem of Embeddedness. *American Journal of Sociology*, 91(3), 481–510.
25. Friedland, R., & Alford, R. R. (1991). Bringing Society Back In: Symbols, Practices, and Institutional Contradictions. In W. W. Powell & P. J. DiMaggio (Eds.), *The New Institutionalism in Organizational Analysis*. University of Chicago Press.
26. Thornton, P. H., Ocasio, W., & Lounsbury, M. (2012). *The Institutional Logics Perspective*. Oxford University Press.
27. Padgett, J. F., & Powell, W. W. (2012). *The Emergence of Organizations and Markets*. Princeton University Press.

### 制度経済学・取引コスト

28. North, D. C. (1990). *Institutions, Institutional Change and Economic Performance*. Cambridge University Press.
29. Williamson, O. E. (1985). *The Economic Institutions of Capitalism*. Free Press.
30. Greif, A. (1989). Reputation and Coalitions in Medieval Trade: Evidence on the Maghribi Traders. *Journal of Economic History*, 49(4), 857–882.
31. Greif, A. (2006). *Institutions and the Path to the Modern Economy*. Cambridge University Press.

### イノベーション・能力論・両利き

32. Schumpeter, J. A. (1934). *The Theory of Economic Development*. Harvard University Press.
33. Cohen, W. M., & Levinthal, D. A. (1990). Absorptive Capacity: A New Perspective on Learning and Innovation. *Administrative Science Quarterly*, 35(1), 128–152.
34. Henderson, R. M., & Clark, K. B. (1990). Architectural Innovation. *Administrative Science Quarterly*, 35(1), 9–30.
35. March, J. G. (1991). Exploration and Exploitation in Organizational Learning. *Organization Science*, 2(1), 71–87.
36. Teece, D. J., Pisano, G., & Shuen, A. (1997). Dynamic Capabilities and Strategic Management. *Strategic Management Journal*, 18(7), 509–533.
37. Anderson, P. (1999). Complexity Theory and Organization Science. *Organization Science*, 10(3), 216–232.
38. Nonaka, I., & Takeuchi, H. (1995). *The Knowledge-Creating Company*. Oxford University Press.

### 産業組織史・企業史

39. Chandler, A. D. (1977). *The Visible Hand: The Managerial Revolution in American Business*. Belknap Press.
40. Chandler, A. D. (1962). *Strategy and Structure*. MIT Press.

### 文化進化・系統推定

41. Mesoudi, A. (2011). *Cultural Evolution: How Darwinian Theory Can Explain Human Culture and Synthesize the Social Sciences*. University of Chicago Press.
42. Greenhill, S. J., Currie, T. E., & Gray, R. D. (2009). Does horizontal transmission invalidate cultural phylogenies? *Proceedings of the Royal Society B*, 276(1665), 2299–2306.
43. Bryant, D., & Moulton, V. (2004). Neighbor-Net: An Agglomerative Method for the Construction of Phylogenetic Networks. *Molecular Biology and Evolution*, 21(2), 255–265.
44. Solís-Lemus, C., & Ané, C. (2017). Inferring Phylogenetic Networks with Maximum Pseudolikelihood under Incomplete Lineage Sorting. *Molecular Biology and Evolution*, 34(12), 3292–3307.

### Cliodynamics / 長期史データベース

45. Turchin, P., et al. (2018). Quantitative historical analysis uncovers a single dimension of complexity that structures global variation in human social organization. *PNAS*, 115(2), E144–E151.

### 人類学・狩猟採集

46. Boehm, C. (1993). Egalitarian Behavior and Reverse Dominance Hierarchy. *Current Anthropology*, 34(3), 227–254.
47. Dunbar, R. I. M. (1993). Coevolution of neocortical size, group size and language in humans. *Behavioral and Brain Sciences*, 16(4), 681–694.

### 権力・批判理論（Discussion 補強）

48. Lukes, S. (2005). *Power: A Radical View* (2nd ed.). Palgrave Macmillan.
49. Bourdieu, P. (1986). The Forms of Capital. In J. Richardson (Ed.), *Handbook of Theory and Research for the Sociology of Education* (pp. 241–258). Greenwood.

### 方法論

50. Eisenhardt, K. M. (1989). Building Theories from Case Study Research. *Academy of Management Review*, 14(4), 532–550.

合計 50 件。research A–L で典拠確認済みのもののみを採用し、URL のみで一次出典が確認できなかった項目（DAO 関連の Buterin 2014 ブログ記事や Wikipedia 引用、企業ウェブサイト等）は除外した。Stream K のうち Bryant-Moulton 2004 と Solís-Lemus-Ané 2017 は採用、Stream J の Turchin et al. 2018 PNAS は採用、Whitehouse 2019 Nature は撤回済みのため意図的に除外。

---

## 6. Submission Targets（投稿先候補）

| 候補 | フィット | 想定 desk reject リスク |
|---|---|---|
| **Organization Studies** (SAGE, EJOR の後継格) | 第一候補。理論多元性・歴史比較に強く、Luhmann/Beer/制度論の融合が読まれやすい。 | 低-中。経験データ N=18 が小さい点で revise 要求は確実。 |
| **Administrative Science Quarterly (ASQ)** | 第二候補。方法論的厳密性を要求するが、population ecology / institutional theory のホームジャーナル。 | 中。N=18 でのファクト検証は弱いが、理論貢献として評価される可能性。 |
| **Journal of Organization Design** | 第三候補。VSM / Beer 系の組織設計論に親和的。Open Access。 | 低。但しインパクトは ASQ/OS より下。 |
| **Academy of Management Review (AMR)** | 経験データ前提ではなく理論論文として書き直す場合の候補。reticulate network framework として concept paper 化。 | 中-高。empirical を切り落とす必要あり、Phase 4 完了後の再検討。 |

推奨戦略: Phase 4 temporal facets 完了後、Organization Studies に N=18 → 30–50 に拡大したうえで投稿。AMR には reticulate genealogy framework の concept paper を派生して別投稿。

---

## 7. 次工程

1. Phase 4 temporal facets 実装（前提）。
2. ケース 30–50 拡大。
3. 本骨子の英文化、本文ドラフト作成。
4. 5 図の作成（特に Figure 1 と Figure 5）。
5. Internal review → 国際 workshop pre-submission（European Group for Organizational Studies / Organization Science online forum）。
6. Organization Studies 投稿。
