# J. Seshat databank と Cliodynamics の深掘り

事前リサーチ Stream J（第2波）。第1波 D・F で重要性が確認された Seshat / Cliodynamics を実装可能粒度まで掘り下げる。本ノートは codex2 (`/Users/yuya/organization-genealogy/research/codex2_data_model.md`) のスキーマと突き合わせ、継承・拡張の実務指針までつなぐ。

## 概要

Seshat: Global History Databank は CSH Vienna / Evolution Institute が運営する世界史定量データベース。最新公開バンドルは Equinox2020（374 polities × 約47,400 records、1,500+ 変数）と派生版 Equinox-Continuous (2023)、地理境界版 Cliopatria v0.1.3 (2025/01、約1,600 polities, 3400 BCE–2024 CE)、現在生成中の Polaris2026。CC BY-NC-SA。Cliodynamics は Turchin の構造-人口論を中核に、社会複雑度の単一主成分（PC1≈75%）と Crisis-recovery oscillation を主張。Whitehouse 2019 (Nature) は撤回、Slingerland らから coder bias の批判が継続。

## Seshat の構造（最新版）

### データセット系列

| 名称 | 公開時点 | 単位 | スコープ | 入手 |
| --- | --- | --- | --- | --- |
| Equinox2020 | Cliodynamics 11(1):41-50 (2020), Zenodo v.1 (2022/06) | NGA × Polity × 100yr | 30 NGA / 374 polities / 47,400 records / 1,500+ variables | DOI 10.5281/zenodo.6642230, GitHub `seshatdb/Equinox_Data` |
| Equinox-Continuous | Zenodo (2023/07) | culturally/institutionally continuous polity 系列 | Timescale.SM_Data.xlsx | DOI 10.5281/zenodo.8120128 |
| Cliopatria v0.1.3 | 2025/01/21 | polity geo-temporal slice | 約1,600 polities / 15,000+ records, 3400 BCE–2024 CE, EPSG:4326 | GitHub `Seshat-Global-History-Databank/cliopatria`, `cliopatria.geojson.zip` |
| Polaris2026 | 生成中（最新更新 2026/02/25） | polity threads | `Polaris2026.xlsx` + `polity_threads.csv` | GitHub `Seshat-Global-History-Databank/build_polaris_dataset` |
| Live DB (`seshat-db.com`) | 連続更新（最新 2026/04/30） | polity / variable / claim | 6 モジュール（Core, Crisis DB, General, RT, SC, WF, EC） | REST API、ログイン要 |

### 単位（NGA: Natural Geographic Area）

- 約100km × 100km（±50%）の固定矩形エリア。時間で位置を変えない。
- 10 major regions（Europe, Africa, Southwest Asia, South Asia, Southeast Asia, East Asia, Central Eurasia, North America, South America, Oceania）に各 3 NGA = 30 NGA を「early-complex / late-complex / intermediate」三段階で層化サンプリング（World Sample-30）。
- NGA を時間軸で200–300年単位の polity slice に分割し、各 slice に変数値を付与。Cliopatria はこれに地理ポリゴンを追加。

### 変数体系（モジュール別）

REST API のモジュール構成（`seshat-db.com/api/`）:

1. **Core** — macro-regions, regions, polities, capitals, sections, variable hierarchies, references, citations, religions, shapefiles
2. **General** — polity 名・期間・centralization・言語・宗教・他ポリティとの関係・専門家割当
3. **Societal Complexity (SC)** — 階層、専門職、法、公共事業、識字、貨幣、建築、計量
4. **Warfare (WF)** — 金属、武器、攻城兵器、装甲、軍用獣、艦船、要塞
5. **Religious Traditions (RT)** — 普及度、習合、分化、政府制限、差別、moralizing supernatural beliefs
6. **Economics (EC)** — 奢侈品交易（金属、織物、加工品、香辛料、酒、陶磁器、宝石、食品）
7. **Crisis DB** — 米国暴力データ（locations / subtypes / sources / events / consequences）+ 約168歴史ケース

### Social Complexity 9-CC (PNAS 2018)

各 polity / 100年で評価される 9 complexity characteristics（CC）。51 構成変数の主成分。

| グループ | CC | 代表変数（実装名） |
| --- | --- | --- |
| Scale | Polity Population (PolPop) | range 値、最小/最大推定 |
| Scale | Polity Territory (PolTerr) | km² range |
| Scale | Population of Largest Settlement (CapPop) | 人口 range |
| Scale | Largest Communication Distance | km |
| Hierarchy | Hierarchical Levels | Settlement / Administrative / Religious / Military hierarchy |
| Government | Government complexity | 専門職、官僚機構、法制度（A/P/U/~ ） |
| Information | Writing systems | Mnemonic / Nonwritten / Written / Script / Phonetic |
| Information | Texts | Lists & tables / Calendar / Sacred / Religious / Practical / History / Philosophy / Science / Fiction |
| Information | Money | Article / Token / Precious metal / Foreign coin / Indigenous coin / Paper / Debt & credit / Store of wealth |
| Infrastructure | Infrastructure (Infra) | 12 変数集約：water supply, food storage, road, bridge, canal, port, market, postal courier/station/general, irrigation, drinking water |
| Information | Postal | Courier / Postal station / General postal / Fastest individual communication |
| Information | Measurement | Length / Area / Volume / Weight / Time / Geometrical |

公開ページ集計値: 26,206 values / 77 variables / 621 polities（公開ブラウザ時点）。

**コード化記号**: `A`=Absent / `P`=Present / `U`=Unknown / `~`=Transitional または Range 値（min,max 推定）。

## 取得方法

### A. Zenodo / GitHub ダンプ（推奨：再現性確保）

```bash
# Equinox 2020 一括ダンプ
curl -L "https://zenodo.org/records/6642229/files/seshatdb/Equinox_Data-v.1.zip" -o equinox.zip
unzip equinox.zip

# Equinox-Continuous (2023)
curl -L "https://zenodo.org/records/8120128/files/Timescale.SM_Data.xlsx" -o timescale.xlsx

# Cliopatria 地理データ
git clone https://github.com/Seshat-Global-History-Databank/cliopatria
# cliopatria.geojson.zip を解凍 → GeoPandas で読込
```

ライセンス: Equinox2020 は CC BY 1.0 (Zenodo メタデータ)。サイト公開分は CC BY-NC-SA。Cliopatria は repo LICENSE 要確認。

### B. REST API（推奨：最新値）

```python
# 1. seshat-db.com で account 申請 → seshat.admin@csh.ac.at に許可メール
# 2. Python パッケージ
git clone https://github.com/Seshat-Global-History-Databank/seshat_api
cd seshat_api && pip install .

from seshat_api import SeshatAPI
from seshat_api.core import Polities

client = SeshatAPI(username="<USER>", password="<PASS>")
polities = Polities(client)  # iterable
for p in polities:
    print(p.id, p.name)
```

エンドポイント: `https://seshat-db.com/api/<module>/<resource>/`、JSON。認証は `/api/api-auth/login/`。

### C. Cliopatria（GeoPandas）

```python
import geopandas as gpd
gdf = gpd.read_file("cliopatria.geojson")
# columns: Name, geometry (Polygon, EPSG:4326), Area (km², EPSG:6933),
#          Type="POLITY", FromYear, ToYear (BCE は負), Wikipedia, SeshatID
gdf[gdf.SeshatID.notna()]  # Seshat 本体と join 可能な行
```

### ライセンス整理

- **Equinox2020 (Zenodo v.1)**: CC BY 1.0
- **Equinox-Continuous (2023)**: CC BY 4.0
- **Live DB ブラウザ/ダウンロード**: CC BY-NC-SA
- **seshat_api パッケージ**: MIT
- **Cliopatria**: 要 repo 内 LICENSE 確認（記載なし時は商用要許諾）

商用での再配布は CC-BY-NC-SA 制約に注意。我々のプロジェクトの公開出力は **派生データ作成時の license inheritance（NC-SA）の波及範囲** を別途検討要。

## Cliodynamics 主要結果 5 件

### 1. Turchin et al. (2018) "A single dimension of complexity" (PNAS 115:E144)

- **結論**: 414 societies × 30 NGAs × 51 変数の PCA で第1主成分が分散の約75%を説明。「社会複雑性は単一次元で計測可能」。
- **データ**: Seshat World Sample-30。
- **方法**: 9 CC を集約後 PCA、世界地域横断で再現性確認。
- **批判**: 51 変数の選択自体が "scale + administrative" 偏重で因子の自己実現的構造になりやすい。Slingerland らは coding source の不透明性も指摘。

### 2. Turchin et al. (2022) "Disentangling evolutionary drivers" (Sci Adv 8:eabn3517)

- **結論**: 社会複雑性の進化的駆動要因仮説を競合検定。集団間競争（特に warfare）と農業生産性が支持、religion 単独説は弱い。
- **データ**: Equinox2020 ベース。
- **方法**: Bayesian model comparison。
- **批判**: warfare 変数のコード化粒度。

### 3. Whitehouse et al. (2019, retracted 2021) "Complex societies precede moralizing gods" (Nature 568:226)

- **結論**（撤回前）: Big Gods は社会複雑性の **後** に出現、原因ではない。
- **データ**: Seshat 414 societies。
- **方法**: NA を Absent として処理（→ 致命的）。
- **批判**: Beheim et al. (2021) が NA→Absent 変換を指摘し撤回。Slingerland et al. (2020 / 2022 "retake") は historian-vetting 不足、periodization の恣意性、data pasting/filling を指摘。Whitehouse らは 2022 RBB で再分析、主要結論は維持と主張。

### 4. Turchin (2016) "Ages of Discord" + DST 体系

- **結論**: 米国史を Goldstone 由来の Structural-Demographic Theory で再構成し、約50年周期の二相（integration / disintegration）と elite overproduction → political stress → crisis を提示。2020-2030 を第二の Age of Discord と予測。
- **データ**: 米国賃金、選挙暴力、議会極化、富裕層数、大学院供給など独自編集。
- **方法**: Political Stress Index (PSI) = MMP × EMP × SFD（mass mobilization potential × elite mobilization potential × state fiscal distress）。
- **批判**: 変数選択の事前性、変数集約の重み付けの恣意性。Turchin 2025 "The Great Holocene Transformation" で更新。

### 5. Currie & Mace (2009-2014) cultural phylogenetics（Seshat 前史 / 補完）

- **結論**: Bantu 89 + Austronesian 88 societies で社会複雑性は incremental に上下し（Nature 2010 "Rise and fall of political complexity")、political complexity は ethnolinguistic group 拡散を予測する。Bantu kinship の系統再構築は Main Sequence Theory に挑戦（PNAS 2014）。
- **データ**: Ethnographic Atlas + 言語系統樹。
- **方法**: Bayesian phylogenetic comparative method (BayesTraits)。
- **意義**: 我々が組織を「系譜」で扱う上で、polity → ethnolinguistic group → organizational lineage の概念連続性の参照点。Seshat NGA は地理アンカーで言語系譜を扱わない点で相補的。

## 方法論的留意点

我々のプロジェクトで Seshat を採用する場合の注意：

1. **Coder bias / expert vetting 不透明性** — RA による 1 次コードを expert がどこまで vet したかの track が弱い。各値に「coder ID + reviewer ID + last-reviewed」のメタを必ず保持する設計に。codex2 の `Claim.recorded_by + reliability_basis` で対応可能。
2. **Data pasting / data filling** — 連続する time slice 間で値が変わらない場合に複製、欠損を隣接値で補完する慣行が指摘される。我々は **「inferred / observed / inherited」** を Claim レベルで区別すべき（codex2 `Claim.interpretation_note` を構造化フィールドに昇格）。
3. **NA vs Absent** — Whitehouse 撤回の主因。我々は `present | absent | partial | unknown | inapplicable` の5値を必ず分け、`unknown` を絶対に `absent` 扱いしない。
4. **欧米中心バイアス** — World Sample-30 は層化されているが、専門家プールと参照文献は依然 anglophone 偏重。codex3（東アジア視点）と組み合わせて補正。
5. **Polity 境界の曖昧性** — 200–300年の time slice 切断は文化連続性を切断する場合がある（Equinox-Continuous はこれに対する応答）。我々は temporal facet を明示的に "continuous" / "discrete" でフラグする。
6. **Single-dimension claim の循環性** — 51 変数が scale 中心に偏重すれば PC1=75% は半ば必然。我々は **scale 系列と非-scale 系列（ケア・調停・正統化など）を分離** して PCA すること。
7. **NGA 単位は組織より粗い** — Seshat の単位は polity（≈ state）であり、神殿経済・修道院・ギルド・企業・DAO はサブ-polity。Seshat スキーマは出発点でしかない。

## 統合戦略：Seshat → 我々の Organization スキーマへのマッピング

codex2 の Organization スキーマと Seshat の対応案：

| Seshat 概念 | codex2 マッピング | 注 |
| --- | --- | --- |
| Polity | `Organization`（`primary_form_id` = `polity` form） | NGA + time slice を 1 Organization と扱う |
| NGA | `Organization.geo_scope`（fixed bbox） + `Population.selection_criteria` の地理キー | 同一 NGA 上の polity 連鎖は `Event.succession` で接続 |
| 100yr time slice | `OrganizationTemporalFacet`（`valid_from`/`valid_to` で 100 年区切り） | facet_type = `state_snapshot` |
| 9 CC + 51 変数値 | `OrganizationFeatureVector.features_jsonb`（schema version `seshat-eq2020`） | 同時に対応する `Activity` / `Function` / `ImpactRecord` を派生 |
| Variable コード（A/P/U/~/Range） | `Claim.claim_value` JSONB（`{state: "P/A/U/T", range:[min,max], confidence}` ） | `unknown` を `absent` に潰さない |
| Reference / Citation | `Source` + `Claim.source_id` | Seshat の reference は二次文献中心 → reliability 評価必須 |
| Polity transition | `Event` (`event_type`: `succession`/`merger`/`split`) + `Relation` (`relation_type`: `succession`) | Cliopatria の FromYear/ToYear ペアから自動生成 |
| Cliopatria geometry | `Organization.geo_scope.polygon_geojson` | EPSG:4326 → 等面積 EPSG:6933 計算保持 |
| Crisis DB event | `Event` (`event_type`: `crisis`) + `ImpactRecord` (`direction`: `negative`) | demographic / fiscal / elite 各次元の `metric_name` を標準化 |
| Moralizing gods 変数 (RT) | `Function` (`function_type`: `legitimation`) + `Activity` (`domain`: `ritual`) | 変数の真偽値だけでなく「どの集団が誰を対象に」までは Seshat にない情報を追加 |

### 拡張実務

- **schema version**: `feature_schema_version = "seshat-eq2020"` で Equinox 由来 vector を識別、別 version `"seshat-polaris2026"` を並列で持つ。
- **NGA → 組織単位への分解**: 1 polity facet を Anchor として、その下に "sub-organization" として religious order / merchant guild / military lineage を `Organization` で別ノード化、`Relation`（type=`subordinate_of`/`embedded_in`）で polity に繋げる。Seshat は polity 単位だが我々は polity を「環境」、subentity を「組織」とする二層モデルが有効。
- **NA 取扱い**: Seshat の `~` (transitional) と U (unknown) は両方 `Claim.confidence < 0.4` に丸めず、`facet_value.state` で別カテゴリとして残す。
- **temporal granularity**: Seshat 100yr → 我々 `valid_from/valid_to` の date range（精度 century）。短期組織（企業・DAO）と古代 polity を同一スキーマで扱う以上、`date_precision` は必須。
- **license**: Seshat 由来データを取り込む facet には `Source.license` フィールドを追加し、`CC-BY-NC-SA` をプロパゲートさせる UI を v0.2 で実装。

## 関連 databank（補完候補）

| DB | 単位 | 規模 | 特性 | Seshat との関係 |
| --- | --- | --- | --- | --- |
| **D-PLACE** | linguistic/geographic culture | 1,400+ societies | EA + Binford HG + SCCS + WNAI を統合、地理・言語・環境統合 | NGA より細粒度の文化単位、Seshat 補完 |
| **SCCS** (Standard Cross-Cultural Sample) | culture | 186 cultures | Murdock & White 1969、現代狩猟採集～産業社会、奴隷制・親族・宗教 | 統計検定の出発点、Seshat の歴史軸を持たない |
| **Pulotu** | Austronesian society | 116 cultures | 超自然的信念・実践、reference + page 番号付き | Big Gods 仮説の南太平洋検証、Seshat RT と相補 |
| **DRH** (Database of Religious History, UBC, Slingerland) | religious group + place + time | 1,000+ entries (2023/02), 488 expert contributors | 宗教 entity 中心、Polity poll は休止中（再開予定）、relational, expert-authored | Seshat への対案、coding bias の反例 |
| **Ethnographic Atlas (EA)** | culture | 1,200+ | Murdock のクラシック、D-PLACE 経由でアクセス | Seshat の polity 軸と直交 |

統合戦略：Seshat を polity-time facet の骨格、D-PLACE / SCCS を ethnographic baseline、DRH / Pulotu を religion sub-entity の補強、として 4 層で取り込む。codex2 `Population.selection_criteria` に `source_db` キーを必須化。

## 未確認・要追跡

1. **Polaris2026 の正式リリース時期**と Equinox からの差分（変数追加・polity 拡張） — `build_polaris_dataset` repo は active development（2026/02 最終）。Polaris2026.xlsx の column header を直接確認したい。
2. **seshat-db.com REST API の rate limit / pagination 仕様** — README に明示なし。実 endpoint で確認が必要（`/api/core/polities/?page=1&page_size=100`想定）。
3. **Cliopatria LICENSE** — repo LICENSE ファイルの実体未確認。商用利用可否が決まる。
4. **Equinox-Continuous の "continuous polity thread" の操作的定義** — arXiv:2212.00563 v3 を要精読（"culturally and institutionally continuous" の閾値）。
5. **Slingerland-Whitehouse 論争の最新状態** — 2022 "retake" 以降、Religion, Brain & Behavior 誌での応酬を 2024–2026 でフォロー。Beheim ら次論文の有無。
6. **CrisisDB の variable schema 公開状況** — 168 cases × ~100 indicators が CSV で出ているか、論文 SI のみか。`peterturchin.com/research/current-research/crisis-databank/` には素データへのリンクがない。
7. **Seshat の "expert vetting" メタデータが API で取得可能か** — coder ID / reviewer ID / last-reviewed が JSON に含まれるか実 endpoint で確認。
8. **D-PLACE と Seshat の polity-culture cross-walk** — 公式 mapping は存在するか、自前で作るしかないか。
9. **2025 Turchin "The Great Holocene Transformation"** の詳細（出版形態・データ更新）。
10. **Cliopatria の geometry を polity 連続性の同定に使えるか** — 同一名称・隣接時期・領土重複 70%以上を `Event.succession` 自動生成のヒューリスティックとして使えるか（要実装検証）。

---

## ソース

- [Seshat downloads page](https://seshat-db.com/downloads_page/)
- [Seshat SC variables page](https://seshat-db.com/sc/scvars/)
- [Seshat REST API root](https://seshat-db.com/api/)
- [Seshat NGAs core endpoint](https://seshat-db.com/core/ngas/)
- [Seshat-Global-History-Databank GitHub org](https://github.com/Seshat-Global-History-Databank)
- [seshat_api Python package](https://github.com/Seshat-Global-History-Databank/seshat_api)
- [build_polaris_dataset repo](https://github.com/Seshat-Global-History-Databank/build_polaris_dataset)
- [Cliopatria geo dataset](https://github.com/Seshat-Global-History-Databank/cliopatria)
- [Seshat docs site](https://seshat-global-history-databank.github.io/seshat/)
- [Equinox 2020 Zenodo](https://zenodo.org/records/6642229)
- [Equinox-Continuous Zenodo (2023)](https://zenodo.org/records/8120128)
- [Turchin et al. 2018 PNAS – single dimension of complexity](https://www.pnas.org/doi/10.1073/pnas.1708800115)
- [Turchin et al. 2022 Sci Adv – disentangling drivers](https://www.science.org/doi/10.1126/sciadv.abn3517)
- [Whitehouse et al. 2019 Nature (retracted)](https://www.nature.com/articles/s41586-019-1043-4)
- [Retraction note (Nature 2021)](https://www.nature.com/articles/s41586-021-03656-3)
- [Whitehouse 2022 RBB "retake"](https://www.tandfonline.com/doi/full/10.1080/2153599X.2022.2074085)
- [Slingerland et al. 2020 "Coding culture" (Evol Hum Sci)](https://www.cambridge.org/core/journals/evolutionary-human-sciences/article/coding-culture-challenges-and-recommendations-for-comparative-cultural-databases/27CCA9E8D72FB095CD3C268332EA8A52)
- [Historians Respond to Whitehouse et al. 2019 (J Cog Histor)](https://journal.equinoxpub.com/JCH/article/view/18509)
- [DRH overview paper (Slingerland-Monroe-Muthukrishna 2023)](https://www.tandfonline.com/doi/full/10.1080/2153599X.2023.2200825)
- [Crisis Databank (Turchin)](https://peterturchin.com/research/current-research/crisis-databank/)
- [Currie et al. 2010 Nature – Rise and fall of political complexity](https://www.nature.com/articles/nature09461)
- [Currie & Mace 2009 PNAS – social complexity & linguistic diversity](https://pmc.ncbi.nlm.nih.gov/articles/PMC3061144/)
- [D-PLACE landing](https://d-place.org)
- [SCCS Wikipedia](https://en.wikipedia.org/wiki/Standard_Cross-Cultural_Sample)
- [Database of Religious History](https://religiondatabase.org/)
- [Equinox2020 Data Release paper (Cliodynamics 11(1))](https://escholarship.org/uc/item/4wj1j1vb)
- [Seshat productivity NGA paper (Holocene 2021)](https://journals.sagepub.com/doi/abs/10.1177/0959683621994644)
