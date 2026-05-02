# Phase 3 (v0.3 Relations and Events) 完了レポート

完了日: 2026-05-03
ステータス: **Phase 3 完了基準達成** → Phase 4 (v0.5 temporal facets) 移行可

注記: ネットワーク分析は `data/network_stats.json` の 18 ノード / 13 エッジ時点のスナップショットに基づく。現在の `data/og.db` は並行作業の反映により `claim=374`, `source=30`, `relation=16` まで進んでいるため、投入実績では現在 DB の実数も併記する。

## ロードマップ Phase 3 完了条件 vs 実績

- [x] `relation`, `event`, `event_organization`, `event_relation`, `dormancy_record` を含む v0.3 schema migration が実装されている。
  - `research/codex4_ddl_README.md` で v0.1/v0.2/v0.3 のマイグレーション順と設計判断を確認済み。
  - SQLite サンドボックス `data/og.db` では v0.3 テーブルが作成済み。PostgreSQL 移行は未実施。
- [x] 創設、解散、合併、分裂、改革、危機、ガバナンス変更を Event として記録できている。
  - 現在 DB: `event=33`。内訳は founding 14, dissolution 6, crisis 3, revival 3, governance_change 2, reorganization 2, merger 1, reform 1, split 1。
- [x] 支配、同盟、競争、継承、分派、資源交換、知識移転、模倣などを Relation として記録できる構造になっている。
  - 現在 DB: `relation=16`。内訳は knowledge_transfer 6, mimetic_isomorphism 6, succession 2, competition 1, schism 1。
  - `network_stats.json` スナップショット: `relation=13` 相当。内訳は knowledge_transfer 4, mimetic_isomorphism 5, succession 2, competition 1, schism 1。
- [x] 分裂、統合、継承、支配、資源交換を Event と Relation の両方から辿れる。
  - Cluny → Cistercian は `split` event と `schism` relation で辿れる。
  - Benedictine → Cluny/Cistercian は `founding/split` event と `succession` relation で辿れる。
  - Linux Foundation は `merger` event と Wikimedia からの `mimetic_isomorphism` relation で、現代財団型の制度的同型化として辿れる。
  - 資源交換そのものの `relation_type` は今回の 18 ケースでは未使用だが、v0.3 DDL と relation schema には強度・根拠つきで記録できる。
- [x] Relation の強度は根拠がある場合のみ記録され、欠損が許容されている。
  - `relation.strength` は NULL 許容。現在 DB でも Hanseatic → VOC, Wikimedia → MakerDAO, VOC → MakerDAO などは strength NULL のまま、confidence のみで保持している。
- [x] 系譜を tree ではなく network として扱う試作ができている。
  - `data/genealogy_network.svg` と `data/network_stats.json` を作成済み。
  - succession/schism の縦方向だけでなく、knowledge_transfer/mimetic_isomorphism による水平伝播をエッジ化済み。
- [ ] 代表ケースの系譜図 3〜5 件を個別図として整備する。
  - 全体 SVG は作成済みだが、個別ケース図 3〜5 件は未分割。Phase 4 のケースブック作成時に切り出す。

## 投入実績 (Phase 1+2+3 累積)

| 項目 | 依頼時点概況 | 現在 DB 実数 | 備考 |
|---|---:|---:|---|
| organization | 348 | 348 | ROR/Wikidata typed/代表注釈ケースを含む |
| claim | 371 | 374 | 並行作業で 3 件増加 |
| source | 23 | 30 | 並行作業で 7 件増加 |
| function_type | 25 | 25 | codex7 Miller 20 + Beer VSM 5 |
| activity | 37 | 37 | 18 完全注釈ケースに分布 |
| function_record | 77 | 77 | 上位は policy_identity 13, boundary 11, memory 10 |
| impact_record | 37 | 37 | 経済 14, 技術 8, 文化 5, 政治 4, 知識 4, 社会 2 |
| event | 33 | 33 | Phase 3 主要成果 |
| relation | 13 | 16 | `network_stats.json` は 13 エッジ時点 |
| event_organization | - | 34 | Event と Organization の接続 |
| event_relation | - | 0 | 今回は relation を event に直接接続していない |
| organization_form_assignment | - | 39 | 型分類の多対多割当 |

ETL は `etl/01_load_function_types.py` から `etl/10_network_statistics.py` までの 10 本で Phase 3 スナップショットを構築済み。`etl/11_isolate_resolution.py` は未追跡ファイルとして存在し、孤立ノード解消の並行作業に使われている。

## 系譜ネットワーク分析

`network_stats.json` 時点の完全注釈 18 ケースは、18 ノード / 13 エッジ / 6 連結成分である。最大成分は 11 ノード、中成分は 3 ノード、孤立は 4 ノード。

### 連結成分の意味的解釈

最大成分 11 ノードは、Benedictine, Cluny, Cistercian, Bologna, Hanseatic, VOC, Mondragón, Grameen, Wikimedia, Linux Foundation, MakerDAO を含む。時代的には 529 年の Benedictine から 2017 年の MakerDAO まで約 1500 年にまたがる。

この長期連続は、単一の直系継承ではない。中世修道院の規則・記憶・境界維持、大学・ギルドの法人格的自治、商業ネットワークと特許会社の資源動員、協同組合・財団・DAO のガバナンス模倣が、`succession`, `schism`, `knowledge_transfer`, `mimetic_isomorphism` で接続されているために生じている。つまり「同じ組織種が1500年生きた」のではなく、境界維持・記憶・意思決定・正統性の組み合わせが複数の器を渡って再利用された、と解釈するのが妥当である。

中成分 3 ノードは、三井越後屋 / 三井グループ、鴻池家、比叡山延暦寺である。これは東アジアの `ie_household` と宗教的制度基盤が、信用、継承、場、名跡、金融・商業実践を通じて接続される小系譜である。codex3 の東アジア視点に沿えば、法人格ではなく「家」「場」「制度的保護」「信用メカニズム」を temporal facet 化する必要がある。

孤立 4 ノードは、アシャンティ王国、ムガル朝マンサブダール制、Hadza バンド、インカ帝国である。孤立は「系譜がない」ことを意味しない。Phase 3 スナップショットでは、比較可能な relation 証拠を過剰に足さなかった結果である。非西洋国家組織や狩猟採集バンドは、欧州中世・現代デジタル系の relation vocabulary だけでは接続しにくく、Stream G/J のような非西洋・cliodynamics 側の出典で慎重に接続すべきである。

### 中心性上位ノードの解釈

`network_stats.json` の degree 上位は、Benedictine, Wikimedia Foundation, Cistercian が total degree 3 で並ぶ。

Benedictine は out-degree 3 で、規則・修道制・境界維持の供給源として働いている。これは個体群生態学でいう形態の増殖であり、autopoiesis でいう決定・規則・記憶の再生産でもある。

Wikimedia Foundation は in-degree 1 / out-degree 2 で、現代の非営利財団型ガバナンスから Linux Foundation と MakerDAO へ制度的同型化を広げる媒介点になっている。ここでは効率性よりも、正統性、開放性、コミュニティ統治の模倣が中心である。

Cistercian は in-degree 2 / out-degree 1 で、Benedictine/Cluny から受け継ぎつつ Bologna へ知識移転する中継点である。分派は断絶ではなく、記憶と境界維持を再編して新しい形態を作る event として読める。

### relation_type 分布の解釈

`network_stats.json` 時点では mimetic_isomorphism 5, knowledge_transfer 4, succession 2, competition 1, schism 1 である。現在 DB では knowledge_transfer と mimetic_isomorphism が各 6 まで増えている。

medieval 側は Benedictine → Cluny/Cistercian の `succession` と Cluny → Cistercian の `schism` が太い。中世の関係は、規則・正統性・改革運動・分派を通じた縦方向の再生産として現れる。

contemporary 側は Wikimedia → Linux Foundation/MakerDAO, VOC → MakerDAO, Mondragón → Grameen などの `mimetic_isomorphism` が中心である。現代組織では、直接の親子関係より、ガバナンス様式、財団モデル、協同組合原理、プロトコル的正統性の模倣が系譜エッジになる。

`knowledge_transfer` は Hanseatic → VOC, Cistercian → Bologna, Bologna → Wikimedia など、長距離交易、学術自治、知識共有を接続する。ただし、現在 DB に追加された Inca → Mondragón, Mansabdari → 鴻池家, 延暦寺 → 三井などの低 confidence エッジは、Phase 4 で claim と出典を再検証する必要がある。

## 18 完全注釈ケースの分布

### 時代別

`network_stats.json` の era_distribution:

| era | 件数 |
|---|---:|
| medieval | 7 |
| early_modern | 5 |
| contemporary | 3 |
| postwar | 2 |
| extant | 1 |

古代・BC500 以前は 18 ケースに含まれていない。これは既知課題として Phase 4 で補う。

### 状態別

`network_stats.json` の status_distribution:

| status | 件数 |
|---|---:|
| active | 11 |
| extinct | 5 |
| transformed | 2 |

現在 DB 全体では unknown 226, active 111, extinct 9, transformed 2 であり、Wikidata typed 由来の unknown が大きい。完全注釈ケースでは active/extinct/transformed が運用できているが、大量取り込み側は状態補完が必要である。

### 連結成分別

| 成分 | 件数 | メンバー | 解釈 |
|---|---:|---|---|
| 最大成分 | 11 | Benedictine, Cluny, Cistercian, Bologna, Hanseatic, VOC, Mondragón, Grameen, Wikimedia, Linux Foundation, MakerDAO | 修道制・大学・商業・協同組合・デジタル財団/DAOを横断する制度記憶と模倣の連鎖 |
| 東アジア中成分 | 3 | 三井越後屋 / 三井グループ, 鴻池家, 比叡山延暦寺 | 家・信用・宗教的制度基盤・商業実践の小系譜 |
| 孤立 | 1 | アシャンティ王国 | 西アフリカ国家組織。比較語彙と典拠接続が未成熟 |
| 孤立 | 1 | ムガル朝マンサブダール制 | イスラーム帝国官僚制。資源配分・軍役・身分秩序の facet 化が必要 |
| 孤立 | 1 | Hadza バンド | 狩猟採集バンド。relation 化の捏造リスクが高く、孤立維持も妥当 |
| 孤立 | 1 | インカ帝国 | アンデス行政・ayllu・道路/倉庫網との接続候補はあるが要出典 |

## Phase 4 (v0.5 temporal facets) への移行アクション

1. `organization_facet` 相当の temporal facet schema を実装する。
   - 優先 facet: governance, resource_base, territory, membership, identity, technology, boundary。
   - JSON 自由記述に流れないよう、facet_type と最小必須フィールドを固定する。
2. 18 完全注釈ケースに facet を追加する。
   - 三井/鴻池/延暦寺では、法人格ではなく家、場、名跡、信用、制度的保護を分ける。
   - Benedictine/Cluny/Cistercian では、規則、支部、改革、境界維持、記憶を分ける。
   - Wikimedia/Linux/MakerDAO では、財団、コミュニティ、プロトコル、トークン、意思決定境界を分ける。
3. relation と event の claim 監査を行う。
   - confidence 0.5 未満の relation は、出典、解釈ノート、代替説明を確認する。
   - 影響関係と類似関係の混同を避け、mimetic は「直接影響」ではなく制度的同型化として記録する。
4. 代表ケースの個別系譜図 3〜5 件を作る。
   - 修道制チェーン、東アジア家業チェーン、現代デジタル財団/DAO、非西洋国家組織、孤立ケースの扱いを候補にする。
5. Wikidata typed 由来の unknown status を補完する。
   - dissolution_date 欠損を unknown として保持しつつ、claim_value_kind の `unknown` と `absent` を混同しない。
6. PostgreSQL への移行準備をする。
   - SQLite サンドボックスで実証済みの DDL v0.1/v0.2/v0.3 を PostgreSQL に適用し、pgvector/PostGIS/BRIN/GIN の本番運用を検討する。

## 既知の課題

- Wikidata 取り込みの品質問題
  - Phase 1 完了レポートで確認済み。`P31/P279*` の subclass 展開により、historical_organization や DAO に不適切なエントリが混入した。
  - codex 8 で並行対応中。Phase 4 では depth 制限、confidence 減点、別ソース照合、手動 curation を品質ゲートに入れる。
- 4 isolate ノード
  - `network_stats.json` 時点では Asante, Mansabdari, Hadza, Inca が孤立。
  - Stream M で対応中。`etl/11_isolate_resolution.py` は存在するが未追跡であり、Phase 3 完了レポートではスナップショットを固定して扱う。
- 古代 (BC500 以前) のカバレッジ不足
  - 18 完全注釈ケースに BC500 以前がない。
  - Seshat/Cliodynamics, ancient polity, temple economy, kinship organization を追加候補にする。
- `event_relation` が未使用
  - Event と Relation を両方から辿る要件は実質的には満たしているが、event_relation テーブルへの直接接続は 0 件。
  - Phase 4 で split/merger/governance_change と relation を明示リンクする。
- relation confidence の低い水平接続
  - 非西洋ケースを接続する低 confidence の knowledge_transfer は、比較仮説としては有用だが、確定系譜として扱わない。

## 学術的な含意

### codex1 の理論批判の罠 5 つに対する現状ステータス

| 罠 | 現状ステータス |
|---|---|
| Reification | 部分的に回避。Organization を固定実体ではなく claim/event/relation/function の束として扱えている。ただし図示ではノードが実体化して見えるため、図注で限界を明記する必要がある。 |
| 適者生存の循環論法 | 回避中。status と event は記録しているが、active を適応の証拠として使っていない。Phase 4 で resource_base/legitimacy/competition を facet として独立記録する必要がある。 |
| 個体境界の曖昧さ | 問題が可視化された。三井、鴻池、MakerDAO、Wikimedia は法的境界・成員境界・意思決定境界が一致しない。Phase 4 temporal facets の中心課題である。 |
| 機能主義的な後知恵 | 部分的に回避。Activity/Function/Impact を分離したため、「存在したから機能した」という記述は避けやすい。一方、function_record は解釈依存なので confidence と claim 監査が必要。 |
| 生物学からの過剰輸入 | 回避中。Miller/Beer は function_type に限定し、VSR は event の横断軸として扱っている。生物学的な繁殖・死・代謝を直訳していない。 |

### 個体群生態学

Phase 3 は、組織形態の創設、分裂、死亡、再編を event として数えられる段階に達した。Benedictine 系の succession/schism と現代 mimetic の分布差は、組織形態が時代ごとに異なる増殖メカニズムを持つことを示す。ただし、個体群密度、創設率、死亡率はまだ計量できない。

### Autopoiesis

境界維持、記憶、方針・同一性が function_record 上位に来ていることは、組織が資源の束だけでなく、次の作動を生む規則・記録・決定の束として持続することを示す。修道制、家業、財団、DAO は法人格が異なっても、決定と記憶の再生産という観察軸で比較できる。

### サイバネティクス

Beer VSM 由来の `vsm_s5_policy_identity` が 13 件で最多であり、Phase 3 の完全注釈ケースでは「組織が何をしているか」よりも「何を同一性として裁定するか」が強く記録されている。Phase 4 では S1-S5 の偏りを見て、統治・監査・環境知能がどの時代で薄いかを補う必要がある。

### 制度論

contemporary relation で mimetic_isomorphism が中心になったことは、効率的適応だけでは現代組織の系譜を説明できないことを示す。財団、協同組合、DAO は、正統性、透明性、参加、オープン性といった制度的シグナルを模倣している。これは Stream L の制度論・資源依存論を v0.3 relation_type に物理化した効果である。

## 判定

Phase 3 は、v0.3 schema、Event/Relation 投入、18 ケースの系譜ネットワーク、SVG 可視化、ネットワーク統計まで到達しており、ロードマップ上の主要完了条件を満たした。残る不足は個別系譜図、event_relation の直接利用、低 confidence relation の監査であり、いずれも Phase 4 の temporal facets と比較ケースブックで扱うのが適切である。
