# Scholarly Implications — 18 完全注釈ケースから読む組織系譜

作成日: 2026-05-02
担当: Phase 3 並列タスク #Q (Scholarly Analysis)
基盤データ: 18 完全注釈ケース、348 organization、374 claim、16 relation、3 連結成分（大 12 / 中 5 / Hadza のみ孤立）。
基盤文書: `research/codex1_theory_critique.md`、`data/network_stats.json`、`data/function_coverage.md`、`plan/phase3_complete.md`。

> 本書は「経験的発見の理論的解釈」と「方法論的罠の自己評価」を目的とする提言メモであり、論文草稿そのものではない。論文化に向けた骨子は `plan/paper_outline.md` に分離している。

---

## 1. 経験的発見の解釈

### 1.1 1500 年連続成分（最大成分 12 ノード）の意味

最大連結成分は、Benedictine（529 設立）、Cluny、Cistercian、Bologna、Hanseatic、VOC、Mondragón、Wikimedia、Linux Foundation、MakerDAO、Grameen、Inca を含む 12 ノード／約 1500 年スパンを持つ。エッジは `succession`（2）、`schism`（1）、`knowledge_transfer`（6）、`mimetic_isomorphism`（6）、`competition`（1）の混合で構成される。

この成分は「同一の組織種が 1500 年連続して生きた」ことを意味しない。Cluny → Cistercian の `schism`、Cistercian → Bologna の `knowledge_transfer`、VOC → MakerDAO の `mimetic_isomorphism` のように、相互に法人格・成員・資源・地理が連続しないノード群が、規則・記録・境界維持・正統性の再利用によってネットワーク的に接続されている。これは Padgett & Powell (2012) の autocatalytic 多重ネットワーク論、および DiMaggio & Powell (1983) の制度的同型化論の双方と整合する。組織系譜は生物学的個体群の意味での lineage ではなく、文化進化論で言う水平伝達優位の reticulate な系統 (Stream K, NeighborNet/PhyloNet 系の関心領域に対応) として観察される。

含意は次の通りである。第一に、組織系譜分析は tree モデルではなく phylogenetic network が正しい既定モデルである。第二に、Hannan & Freeman (1977) の population ecology の「個体（organization as discrete individual）」前提は、長期史データには弱く、Luhmann 系の「決定の連鎖」と Beer の「再帰的サブシステム」を補助線にして、何が乗り物（vessel）を渡って再生産されたかを問う必要がある。第三に、組織進化を語るには、媒介ノード（Benedictine, Wikimedia, Cistercian）の制度的開放性と再帰性を独立に測る指標が要る。

### 1.2 S5 Policy/Identity 集中の含意（13/18）

Beer VSM の S5（Policy/Identity）は 18 ケース中 13 で記録され、Miller の Boundary（11/18）、Memory（10/18）、Ingestor（9/18）を上回り、taxonomy 全 25 機能のうち最頻出となった。ただし「universal な機能はゼロ」であり、すべての組織で記録される機能は存在しない。

この偏りは三通りに解釈できる。

**(a) 注釈アーティファクト仮説**: S5 は「組織が何を自分のアイデンティティとして裁定するか」という抽象度の高い機能であり、史料・公式文書・規則文・ミッションステートメントから読み取りやすい。これに対し、M05 Converter / M09 Motor / M11 Input Transducer などの低レベル物理サブシステムは、組織レベル史料からは読めない。すなわち S5 集中は、観察粒度のバイアスを反映している可能性が高い。

**(b) Identity-first 仮説**: 18 ケースは修道会、商業会社、家業、財団、DAO など、いずれも「自己を何として裁定するか」を明示しないと作動しないタイプの組織である。狩猟採集バンド（Hadza）でも、儀礼・タブー・自己定義を通じた S5 相当が観察されている。すなわち、組織が時代と形態を超えて連続するとき、最初に再生産されるのは Policy/Identity であり、これは Luhmann 的な「決定が次の決定を可能にする」自己産出の核と一致する。

**(c) 規範的選択効果仮説**: アイデンティティを明示できない組織は史料に残りにくく、本データセットに採取されにくい。S5 集中は、サンプリング段階で Identity-bearing 組織に偏った結果である。

実際にはこの三つは排他的ではなく、現在のデータからはどれが支配的かを切り分けられない。Phase 4 で temporal facets を導入し、identity statement の有無・更新頻度・対立履歴を独立記録すれば、(b) と (a)+(c) を区別する仕掛けになる。

### 1.3 東西分岐 — 中成分 5 ノードの解釈

中成分 5 ノードは、三井越後屋／三井グループ、鴻池家、比叡山延暦寺、アシャンティ王国、ムガル朝マンサブダール制で構成される（`network_stats.json` 時点では 3 ノード東アジア成分 + 2 isolate だったが、現在 DB の relation 増加でアシャンティ／ムガルが東アジア成分側に弱接続された。低 confidence エッジは `plan/phase3_complete.md` で監査対象として明記済み）。

この成分は西欧最大成分と次の点で構造的に異なる。

- 法人格中心ではなく、家・名跡・場・宗教的庇護・身分秩序の組み合わせで境界が構成される。codex3 の東アジア視点が指摘する通り、「法人」概念は分析単位として弱く、temporal facet として「家業」「場」「信用」「制度的保護」を分ける必要がある。
- relation_type は `knowledge_transfer` 中心であり、`mimetic_isomorphism` は薄い。これは現代西欧／グローバル系で財団・協同組合・DAO が制度的同型化を通じて接続されるパターンと対比的である。
- mansabdar や ashanti のような国家組織は、欧州中世修道会と直接 succession でつながらない。Stream G（非西洋国家）と Stream J（Seshat/Cliodynamics）の語彙を導入しないと、関係エッジが捏造的になる。

東西分岐は「西欧近代型組織が普遍であり、東洋／非西洋は遅れている」というモダニゼーション図式の根拠ではない。むしろ、relation vocabulary 自体が西欧・現代中心に整備されてきたことを反映しており、データ側のバイアス（codex1 の罠 4 = 機能主義的後知恵 + Stream L の正統性論）として読むべきである。

### 1.4 medieval=succession+schism, contemporary=mimetic という時代構造

relation_type の分布は時代ごとに偏る。medieval では Benedictine → Cluny／Cistercian の `succession`、Cluny → Cistercian の `schism` が太く、組織形態が縦方向の規則・改革・分派で再生産される。contemporary では Wikimedia → Linux Foundation／MakerDAO、VOC → MakerDAO、Mondragón → Grameen の `mimetic_isomorphism` が中心であり、直接の親子関係ではなく、ガバナンス様式・財団モデル・協同組合原理・プロトコル的正統性の模倣がエッジになる。

この時代構造は二つの理論を経験的に支持する。

- DiMaggio & Powell (1983) の mimetic isomorphism は、不確実性下の現代組織で支配的なメカニズムである。
- Greif (1989, 2006) や North (1990) の path-dependent 制度進化は、medieval 期の規則・正統性・改革運動の再生産パターンに整合する。

Phase 4 では、relation の時代分布を独立変数として記録し、`coercive` / `normative` も加えた三型 isomorphism と `succession` / `schism` / `knowledge_transfer` / `competition` の関係を多項分布で扱える状態にする必要がある。

### 1.5 Miller 53 vs VSM 24 records の意味

77 records のうち Miller 53 / Beer VSM 24。Miller は粒度が細かく（20 機能）、Beer は粒度が粗い（5 機能）が、機能あたり頻度では VSM の方が高い（4.8 records/機能 vs Miller 2.65 records/機能）。とくに S5 単独で 13 records を占め、Miller の Boundary（11）と Memory（10）を上回る。

この非対称は、「組織の identity と境界はマクロな診断対象、ingestor/distributor/decoder のような operational サブシステムはミクロな史料が要る」という観察粒度の階層を裏付ける。Phase 4 以降、ミクロ機能を埋める段階に進むと、Miller / VSM 比はより均衡化すると見込まれる。逆に、現在の比率を「Miller が冗長で VSM が本質的」と読むのは早計であり、taxonomy の選択ではなく観察コストの差として解釈する必要がある。

---

## 2. codex1 の 5 罠ステータス

`research/codex1_theory_critique.md` で挙げた 5 罠について、Phase 3 完了時点の自己評価を更新する。

| # | 罠 | ステータス | 根拠 / 残課題 |
|---|---|---|---|
| 1 | Reification | 部分的に回避 | Organization は claim/event/relation/function の束として保持され、ノードに固定属性を持たせない設計を維持。ただし SVG 可視化ではノードが実体に見えるため、図注で「ノードはスナップショットの集約表示」と明記する必要がある。Phase 4 で temporal facet を入れると、reification リスクは更に下がる。 |
| 2 | 適者生存の循環論法 | 回避中 | status (active/extinct/transformed) と event は記録するが、active を「適応していた証拠」として function_record に転写していない。ただし「Benedictine が長く生きたから境界維持機能が強い」という逆算読みが論文叙述で発生しやすく、`plan/paper_outline.md` の Discussion で明示的に注意を入れる。Phase 4 で resource_base / legitimacy / competition を facet として独立記録する必要がある。 |
| 3 | 個体境界の曖昧さ | 問題が顕在化、未解決 | 三井（家／グループ／法人）、Wikimedia（財団／コミュニティ／プロジェクト）、MakerDAO（プロトコル／DAO／財団／トークン）、Mondragón（連合体／個別協同組合／教育機関）はいずれも法的・成員・意思決定境界が一致しない。Phase 3 では organization 単位を fixed したまま注釈したが、Phase 4 temporal facets が中心課題として残る。境界選択そのものが分析対象であることを論文で明示する。 |
| 4 | 機能主義的な後知恵 | 部分的に回避 | Activity / Function / Impact を分離し、impact_record を function_record から独立記録した。これにより「存在したから機能した」という記述は表面的には避けられている。ただし function_record のコーディングは解釈依存で、coder bias 監査が未実施。Phase 4 で function_record の confidence と evidence link を再点検する。 |
| 5 | 生物学からの過剰輸入 | 回避中 | Miller / Beer は function_type に限定し、繁殖・代謝・死を直訳していない。`event_type` には `dissolution` / `revival` / `crisis` を導入したが、これは Stinchcombe / Hannan-Freeman / Brüderl の死亡論に対応する社会科学側の概念であり、生物学からの直接輸入ではない。なお `mimetic_isomorphism` を「水平伝達 (HGT)」と呼び替える誘惑があるが、現状では制度論用語のまま保持し、Stream K の phylogenetic network 適用は Phase 5 以降に分離する。 |

総評として、5 罠中 4 つは観測下にあり管理可能、罠 3（個体境界）のみが Phase 3 段階では未解決の構造的問題として残る。論文化では罠 3 を「分析者が選ぶ境界が結果を決める」という方法論的限界として明示し、複数境界での感度分析を試みる必要がある。

---

## 3. 4 理論系譜の経験的応用評価

codex1 の 4 系譜（Spencer、Hannan-Freeman、Maturana-Luhmann、Beer）が、本データセットでどの程度有効に適用できたかを評価する。

### 3.1 Spencer の有機体的社会観

採用していない。ただし、最大成分 12 ノードを「制度の長期分化と統合」として読む誘惑が常に存在し、これは Spencer 的進歩史観に滑りやすい。本データでは Hadza バンドが Mondragón や MakerDAO より「単純」または「原始的」であるという読みは、観察粒度のバイアス（罠 3 と 4）を Spencer の枠組みで合理化することに等しい。Spencer は批判対象としてのみ参照し、論文では「Hadza は relation 化の捏造リスクが高いため孤立を維持している」と明記することで進歩史観を回避する。

**評価**: 採用しない。批判対象として保持。

### 3.2 Hannan & Freeman の個体群生態学

部分的に有効。`event_type` (founding 14 / dissolution 6 / crisis 3 / revival 3) は population ecology の founding rate / mortality rate / liability of newness / liability of senescence の語彙と直接対応する。VOC（1602–1799）は「特許貿易会社」個体群の代表事例として、リーマン・Andersen は現代解散事例として、Mondragón / Grameen は postwar 協同組合の生存事例として位置づけられる。

ただし、本データはサンプリング設計が「個体群密度」を計算できる規模ではない。18 ケースは比較的成功した（または社会的に記憶された）組織に偏っており、Brüderl & Schüssler (1990) が示した liability of adolescence のような U 字型ハザード関数を検定するには、ベース母集団とサンプリングフレームが弱い。

**評価**: 概念語彙は有用、定量検定は不可。Phase 4 以降に Seshat (Stream J) や CRSP / US Courts (Stream I) との接続を検討する必要がある。

### 3.3 Maturana-Luhmann のオートポイエーシス

最も親和性が高い。S5 Policy/Identity の集中（13/18）と Memory（10/18）、Boundary（11/18）の同時頻出は、Luhmann (1995, 2000) が組織を「決定が次の決定を可能にするコミュニケーション・システム」として定義したことと整合する。Benedictine の Rule、Cistercian の General Chapter、Wikimedia の Foundation Charter、MakerDAO の MIPs ガバナンス手続きは、いずれも「組織の作動として何を認めるか」を明示する規則体系であり、Luhmann 的な観察対象として揃っている。

ただし、Luhmann の autopoiesis を実証研究に落とすコストは大きい。本データでは「決定の連鎖」を直接コーディングしていない（claim を decision として独立に取り出していない）。Phase 4 以降、`event_type=governance_change` と `claim_predicate=decided` を組み合わせて decision log を再構成する余地がある。

**評価**: 解釈枠組みとして強力、operationalization は未完。Phase 4 で decision-log facet 化を検討する。

### 3.4 Stafford Beer のサイバネティクス（VSM）

機能 taxonomy として直接採用済み。S1-S5 の偏りは、Phase 3 完全注釈ケースで S5 > S1 = S2 = S4 = 3 > S3 = 2 となり、組織が何を「同一性として裁定するか」を強く反映する一方、S2 調整・S3 内部統制・S4 環境スキャンは観察コストが高く取りこぼしやすい。これは Beer 自身が `Brain of the Firm` (1972) で警告した「viability の評価には S1-S5 を均等に観察する必要がある」という方法論的指針と整合する欠落である。

注意点として、Beer の VSM を「良い組織の設計原理」として規範化する誘惑がある。codex1 が指摘する通り、本研究では VSM を「歴史的組織の診断語彙」として使うにとどめ、Hadza バンドが S2 / S3 を欠くことを「未発達」と読まない。

**評価**: function taxonomy として最適。ただし規範化リスクを論文で明記する。

### 3.5 採用組み合わせ（codex1 の提言と Phase 3 実績の対応）

codex1 が提言した「Hannan-Freeman を比較基盤、Luhmann を境界・自己再生産の補助線、Beer を内部構造の診断、Spencer を批判対象、制度論・資源依存論を補正」という多層採用は、Phase 3 で部分実装された。

- Hannan-Freeman → event schema (founding/dissolution/crisis) で対応。
- Luhmann → claim と function_record (S5/Memory/Boundary) で部分対応。decision log は未対応。
- Beer → function_type taxonomy（codex7）で全面採用。
- Spencer → 採用せず、進歩史観チェックリストとして使用。
- DiMaggio-Powell の制度同型化 → relation_type=`mimetic_isomorphism` で物理化済み。`coercive`/`normative` は未実装。
- Pfeffer-Salancik の resource dependence → `relation_type=competition` でわずかに触れた程度。Phase 4 で resource flow facet を要検討。

---

## 4. 限界と次の研究課題

### 4.1 データセットの限界

1. **サンプル小**: 18 完全注釈ケースは個体群統計には弱い。density dependence や U 字型 hazard を検定するには、Seshat 374 polities や CRSP/US Courts の数万社規模が必要。
2. **古代カバレッジ不足**: BC500 以前が 18 ケースに含まれない。Stream J の Seshat World Sample-30 と接続する必要がある。
3. **非西洋・周縁の relation 不足**: アシャンティ・ムガル・Hadza・Inca の relation エッジは捏造リスクが高く、現状は低 confidence または孤立で保持。Stream G / H / J 由来の語彙拡張が必要。
4. **女性・ジェンダー視点の欠落**: 18 ケースは事実上ジェンダー中立（あるいは男性中心）として注釈されている。Stream H が指摘する女性組織・女子修道院・女性ギルドは未投入。

### 4.2 方法論の限界

1. **境界選択の感度未測定**: 罠 3（個体境界）について、三井をどこで切るか、Wikimedia をどこで切るかで結果が変わるはずだが、感度分析を行っていない。
2. **coder bias 未監査**: function_record と relation_type のコーディングは解釈依存。複数 coder による inter-rater agreement (κ) は計算していない。Stream J の Whitehouse (2019) Nature 論文撤回事案は、coder bias 監査の欠如が致命的になり得ることを示している。
3. **時間粒度が粗い**: event 33 件は時間軸を持つが、claim は temporal facet 化されておらず、ある時点での「組織の状態」を再構成する仕組みが弱い。Phase 4 の中心課題。
4. **phylogenetic network 未適用**: Stream K で整理した NeighborNet / PhyloNet / HyDe は、本データに直接適用可能だが Phase 3 では未実施。

### 4.3 理論側の限界

1. **生命メタファーの一枚岩化を完全には回避できていない**: 4 系譜を分けて使う設計だが、論文叙述では「組織を生命として」という総称的言い回しに戻りやすい。
2. **正統性論との接合が弱い**: Suchman (1995) の pragmatic / moral / cognitive legitimacy は relation_type には物理化されておらず、claim 単位での legitimacy facet が必要。
3. **権力論との接合が薄い**: Lukes の三次元権力、Bourdieu の field/capital、Foucault の governmentality は Stream L で整備したが、本 18 ケースの注釈には反映されていない。Phase 4 以降の課題。

### 4.4 次の研究課題（優先順）

1. Phase 4 temporal facets 実装（governance / resource_base / territory / membership / identity / technology / boundary）。
2. ケース数を 50→100 まで拡大し、古代・非西洋・女性組織・社会運動を含める。
3. relation_type に `coercive` / `normative` / `resource_flow` / `decision_link` を追加し、DiMaggio-Powell 三型 + resource dependence + Luhmann の decision を物理化する。
4. coder bias 監査（複数 coder で 18 ケースを再注釈し κ を計算）。
5. NeighborNet / SplitsTree6 で「組織系譜は tree か network か」の Δ-score を測定。
6. Seshat (Equinox-Continuous, Cliopatria) との entity matching を試行し、polity 単位と organization 単位のクロスウォークを作る。
7. 法的境界・成員境界・意思決定境界の三重境界で同一組織を再注釈し、感度分析を行う。

---

## 5. 結論

Phase 3 の 18 完全注釈ケースは、組織系譜が tree ではなく reticulate network であること、S5 Policy/Identity が時代を超えて最頻出する機能であること、medieval/contemporary で支配的な relation_type が異なること、東西で relation vocabulary の整備度に偏りがあることを経験的に示した。これらは Hannan-Freeman の population ecology、Luhmann の autopoiesis、Beer の VSM、DiMaggio-Powell の制度同型化のいずれかを単独で採用しても説明できず、多層理論の経験的支持として読める。

同時に、本研究は方法論的罠 3（個体境界の曖昧さ）を解決していない。これは Phase 4 temporal facets と複数境界感度分析で取り組む必要がある。論文化では、この限界を欠陥として隠さず、組織を生命として捉える研究プログラム自体の構造的課題として明示する。
