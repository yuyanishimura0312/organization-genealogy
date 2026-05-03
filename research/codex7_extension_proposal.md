# Codex7 拡張提案: 機能タクソノミーの sub-function 階層化

## 1. 背景

`research/codex7_function_taxonomy.md` で確立した 25 マスター機能 (Miller 20 + VSM 5) は、`research/A_theoretical_foundations.md` および Miller (1978) *Living Systems*、Beer (1972, 1979, 1985) の VSM に厳密に対応する正本である。本提案は、この 25 機能を**変更も削除もせず、追加もしない**。代わりに、各 master function の下に観察可能な sub-function を階層的に追加し、`function_type_id` の **enum 制約は完全に保ったまま**、新しい列 `sub_function_id` を導入する。

## 2. 動機: ヒートマップから読み取れる注釈断層

`data/function_coverage.md` (18 組織、77 function_record) では:

- **未使用 10 機能**: M05 Converter / M08 Extruder / M09 Motor / M10 Supporter / M11 Input Transducer / M12 Internal Transducer / M14 Timer / M15 Decoder / M16 Associator / M20 Output Transducer
- **低頻度 6 機能**: M04 Distributor (2), M06 Producer (2), M07 Matter-Energy Storage (1), M13 Channel and Net (2), M19 Encoder (2), S3 Internal Control (2)
- **最頻出**: S5 Policy/Identity (13/18), M02 Boundary (11/18), M17 Memory (10/18)
- **Miller 53 / VSM 24** の偏り

未使用 10 機能の多くは Miller (1978: pp. 3-4, 18-31) が「物質・エネルギー処理」または「情報処理の物理層」として定義したもので、生物学的システムに対しては感覚器官・運動器官・神経伝達物質などの**物理単位**として明確だが、組織レベルでは「印章・布告板・使者」のような複数物理担体が一つの抽象機能を実装するため、**注釈者が institutional-level で述べられない**ことが原因である。

ただし、この 10 機能は**デジタル組織 (DAO、OSS 財団、プラットフォーム) では再び明示的な物理単位**として浮上する。例:

- **MakerDAO の Timer (M14)**: Ethereum block time、debt auction の epoch 周期、oracle price feed の更新 cadence
- **Linux Foundation の Decoder (M15)**: ABI 互換性検証、CVE classification、license compatibility 解析
- **Anonymous の Output Transducer (M20)**: リーク発信 (DDoS スクリプト、video manifesto、Pastebin dump)
- **Wikimedia の Associator (M16)**: bot による相互参照、recommendation engine、edit pattern detection

つまり、未使用 10 機能は「組織レベルの語彙不足」によって観察できないだけで、**sub-function 層を導入すれば可視化が進む**と仮説立てる。

## 3. 設計原則 (バックワード互換性)

1. **25 マスター機能はそのまま維持**: `function_type_id` enum 不変。Miller 1978 と Beer 1972/1979/1985 への一対一対応を壊さない。
2. **sub_function は purely additive**: 既存 77 records は **`sub_function_id = NULL` で valid**。
3. **sub_function_id は階層 ID**: `<master_id>::<sub_id>` 形式 (例: `miller_14_timer::block_epoch`)。`::` 以降をパースすれば抽象機能に戻れる。
4. **集計クエリは無影響**: master 別集計は `GROUP BY function_type_id` のままで動く。sub-function 別集計は新クエリ。
5. **指標の根拠は原典に残す**: sub_function の definition は Miller 1978 の subsystem 説明か、Beer の VSM 論述から逸脱しない。技術用語 (webhook, oracle, smart contract event) は **example** として era_examples に置き、definition には書かない。

## 4. Sub-function 提案 (25 master 全件)

各 master 機能に対して 2-4 sub-function を提案する。優先順位は: (a) 未使用 10 機能の解像度向上、(b) S5 / Boundary / Memory の過剰負荷を分解、(c) デジタル組織の前景化機能への対応。

### 4.1 Miller マターエネルギー系 (M01-M10)

| master | sub_function_id | 名称 | デジタル例 | 既存ケースで新たに観察可能? |
| --- | --- | --- | --- | --- |
| M01 Reproducer | `m01::filiation` | 母子型分派 (filiation) | git fork、protocol fork | ベネディクト/シトー/Cluny/三井/鴻池/MCC で既存記録を分割 |
| M01 Reproducer | `m01::franchise` | 規約複製型 (franchise/charter) | DAO charter template、CNCF graduation | Linux Foundation, Wikimedia の chapter |
| M01 Reproducer | `m01::succession` | 後継者任命 | maintainer succession plan | 比叡山、三井 (別家制) |
| M02 Boundary | `m02::membership` | 成員資格 | account, MKR holder | 既存 11 件のうち多くを再分類 |
| M02 Boundary | `m02::access_control` | アクセス制御 | API key, smart contract permission | MakerDAO, Linux Foundation |
| M02 Boundary | `m02::secrecy` | 秘密保持 | private repo, gnosis safe | VOC の trade secret |
| M02 Boundary | `m02::expulsion_gate` | 除名・追放 | ban, slashing | Hadza (流動的)、ハンザ unhansing、Wikimedia ban |
| M03 Ingestor | `m03::tribute_extraction` | 貢納・徴税 | gas fee, protocol revenue | Inca mit'a, ムガル jagir, Asante 金鉱税 |
| M03 Ingestor | `m03::voluntary_inflow` | 寄進・寄付 | donation, grant | Wikimedia, Grameen 国際援助 |
| M03 Ingestor | `m03::market_acquisition` | 市場調達 | token sale, IPO | VOC, Linux Foundation 会費 |
| M04 Distributor | `m04::redistribution` | 再分配 | DAO grants, Inca qollqa | Inca, Hadza demand-sharing |
| M04 Distributor | `m04::routing` | 動的経路選択 | autoscaling, message queue routing | (新規観察) Linux Foundation の CI 配分 |
| M05 Converter | `m05::material_processing` | 物質加工 | (該当少) | VOC の倉庫加工 (新規) |
| M05 Converter | `m05::skill_formation` | 技能形成 | onboarding, training | ベネディクト novitiate, MCC 大学 |
| M05 Converter | `m05::data_normalization` | データ正規化 | ETL, schema casting | (新規) Wikimedia bot, Linux Foundation の bug triage |
| M06 Producer | `m06::core_output` | 基幹生産 | software, content | VOC 航海、シトー会農業 |
| M06 Producer | `m06::public_good` | 公共財生産 | OSS, articles | Linux Foundation, Wikimedia (新規) |
| M07 ME Storage | `m07::physical_reserve` | 物質備蓄 | (該当少) | ベネディクト穀倉 |
| M07 ME Storage | `m07::treasury` | 財務予備 | DAO treasury, endowment | MakerDAO PSM (新規)、MCC solidarity fund (新規) |
| M08 Extruder | `m08::waste_disposal` | 廃棄 | log rotation, blob deletion | (新規) すべての digital ケース |
| M08 Extruder | `m08::personnel_release` | 人員排出 | offboarding, ban | (新規) Wikimedia ban の二重分類 |
| M08 Extruder | `m08::deprecation` | 非推奨化 | API deprecation, EOL | (新規) Linux Foundation, MakerDAO |
| M09 Motor | `m09::physical_movement` | 物理移動 | logistics | VOC 船団、Inca chasqui |
| M09 Motor | `m09::deployment_pipeline` | デプロイ実行 | CI/CD, container orchestration | (新規) Linux Foundation, MakerDAO |
| M10 Supporter | `m10::physical_infrastructure` | 物理基盤 | data center, office | (新規) Wikimedia data center, Linux Foundation infra |
| M10 Supporter | `m10::institutional_skeleton` | 制度骨格 | bylaws, org chart | (新規) すべての法人化ケース |
| M10 Supporter | `m10::protocol_substrate` | プロトコル基盤 | EVM, HTTP | (新規) MakerDAO の Ethereum 依存 |

### 4.2 Miller 情報処理系 (M11-M20)

| master | sub_function_id | 名称 | デジタル例 | 新規観察 |
| --- | --- | --- | --- | --- |
| M11 Input Transducer | `m11::sensor_signal` | センサ信号 | telemetry, IoT, oracle | (新規) MakerDAO oracle |
| M11 Input Transducer | `m11::petition_intake` | 陳情・苦情 | issue tracker, ombudsman | (新規) Linux Foundation Issue, Wikimedia Village Pump |
| M11 Input Transducer | `m11::market_signal` | 市場信号 | price feed, demand signal | (新規) MakerDAO price oracle, VOC trade reports |
| M11 Input Transducer | `m11::membership_application` | 加入申請 | KYC, application form | Grameen 5 人グループ加入手続き |
| M12 Internal Transducer | `m12::accounting` | 会計計測 | metrics, audit log | (新規) 鴻池大福帳, MCC, MakerDAO oracle |
| M12 Internal Transducer | `m12::quality_inspection` | 品質検査 | CI test, code review | (新規) Linux Foundation, ムガル dagh (馬の烙印) を再分類 |
| M12 Internal Transducer | `m12::observability` | 観測 | tracing, metrics, audit log | (新規) すべての digital |
| M13 Channel and Net | `m13::courier_route` | 飛脚・伝書 | (歴史) | Inca chasqui (既存)、ハンザ商人連絡網 |
| M13 Channel and Net | `m13::messaging_substrate` | メッセージング基盤 | pub/sub, mailing list | (新規) Linux Foundation LKML, Wikimedia listserv |
| M13 Channel and Net | `m13::deliberation_forum` | 評議体 | DAO forum, governance forum | (新規) Wikimedia Village Pump, MakerDAO forum |
| M14 Timer | `m14::ritual_calendar` | 儀礼暦 | (歴史) | (新規) ベネディクト Liturgy of the Hours, シトー会 General Chapter (年 1) |
| M14 Timer | `m14::block_epoch` | ブロック・エポック | block time, epoch | (新規) MakerDAO, Ethereum 依存ケース |
| M14 Timer | `m14::cadence_review` | レビュー周期 | sprint, quarterly | (新規) MCC Cooperative Congress 周期, Linux Foundation release |
| M14 Timer | `m14::deadline_enforcement` | 期限強制 | timeout, SLA, vesting cliff | (新規) MakerDAO, Linux Foundation |
| M15 Decoder | `m15::translation` | 翻訳 | i18n, schema mapping | (新規) Wikimedia 多言語、ムガルペルシア語行政 |
| M15 Decoder | `m15::legal_interpretation` | 法的解釈 | license review, legal opinion | (新規) Linux Foundation, ボローニャ大学 |
| M15 Decoder | `m15::compatibility_check` | 互換性検証 | ABI check, schema registry | (新規) Linux Foundation |
| M15 Decoder | `m15::classification` | 分類 | tagging, ontology | (新規) Wikimedia category, Inca quipu の knot type |
| M16 Associator | `m16::case_law` | 判例蓄積 | precedent, retrospective | (新規) ボローニャ大学 (glossae), ムガル年代記 |
| M16 Associator | `m16::pattern_recognition` | パターン認識 | recommendation, ML feature | (新規) Wikimedia bot, MakerDAO risk model |
| M16 Associator | `m16::postmortem_learning` | ポストモーテム | postmortem, RCA | (新規) Linux Foundation incident, MakerDAO Black Thursday |
| M17 Memory | `m17::archive` | 文書庫 | object store, archive.org | 多くを再分類 |
| M17 Memory | `m17::ledger` | 帳簿 | git history, blockchain | MakerDAO, 鴻池大福帳 |
| M17 Memory | `m17::genealogy_record` | 系譜記録 | maintainer lineage, succession記録 | (新規) ベネディクト、三井家系図 |
| M17 Memory | `m17::operational_manual` | 業務マニュアル | runbook, SOP | (新規) Linux Foundation TODO best practices, シトー会 customs |
| M18 Decider | `m18::executive_command` | 執行命令 | executive vote, order | Asante Asantehene, ムガル皇帝 |
| M18 Decider | `m18::collegial_council` | 評議体決定 | council, board | VOC Heeren XVII, Wikimedia ArbCom |
| M18 Decider | `m18::consensus_signal` | 合意シグナル | rough consensus, on-chain vote | Hadza, MakerDAO MKR vote, Wikimedia consensus |
| M18 Decider | `m18::automated_controller` | 自動制御 | policy engine, smart contract | (新規) MakerDAO liquidation engine |
| M19 Encoder | `m19::statute` | 法令 | constitution, charter | (新規) Linux Foundation governance docs, Wikimedia Five Pillars (現在 S5 単独だが二重分類可) |
| M19 Encoder | `m19::specification` | 仕様 | OpenAPI, RFC | (新規) Linux Foundation, MakerDAO MIPs |
| M19 Encoder | `m19::brand_message` | ブランド・広報 | press release, brand guideline | (新規) Wikimedia, MCC |
| M19 Encoder | `m19::machine_readable_policy` | 機械可読ポリシー | policy-as-code, smart contract | (新規) MakerDAO MIP-as-code |
| M20 Output Transducer | `m20::publication` | 出版 | website, feed | (新規) Wikimedia, Linux Foundation blog |
| M20 Output Transducer | `m20::broadcast_event` | 放送・公示 | webhook, on-chain event emit | (新規) MakerDAO event log |
| M20 Output Transducer | `m20::ceremonial_display` | 儀礼的提示 | ribbon-cutting, conference keynote | (新規) Linux Foundation KubeCon, Asante 黄金の床几儀礼 |
| M20 Output Transducer | `m20::leak_dispatch` | リーク発信 | manifesto, leak | Anonymous (将来ケース) |

### 4.3 VSM (S1-S5)

| master | sub_function_id | 名称 | デジタル例 | 新規観察 |
| --- | --- | --- | --- | --- |
| S1 Operations | `s1::frontline_unit` | 現場部隊 | service team, working group | 既存 3 件を再分類 |
| S1 Operations | `s1::regional_branch` | 地域支部 | chapter, regional DAO sub-DAO | (新規) Wikimedia chapter, Mondragón cooperative member |
| S2 Coordination | `s2::standard_procedure` | 標準手順 | linter, style guide | (新規) Linux Foundation, シトー会 General Chapter (既存を再分類) |
| S2 Coordination | `s2::dependency_management` | 依存関係管理 | service mesh, package registry | (新規) Linux Foundation |
| S3 Internal Control | `s3::budget_control` | 予算統制 | quota, treasury policy | MCC solidarity fund |
| S3 Internal Control | `s3::audit` | 監査 (S3*) | security audit, dagh | ムガル dagh, MCC Standing Committee |
| S4 Intelligence | `s4::strategy_unit` | 戦略部署 | strategy office, foundation board | Cluny 教皇直属、VOC Heeren XVII |
| S4 Intelligence | `s4::external_scanning` | 外部スキャン | trend mining, community signal | (新規) Linux Foundation TAB, MakerDAO risk team |
| S5 Policy/Identity | `s5::founding_charter` | 創設憲章 | constitution, manifesto | 既存 13 件を分割 |
| S5 Policy/Identity | `s5::value_creed` | 価値・教義 | mission, principles | Wikimedia Five Pillars |
| S5 Policy/Identity | `s5::sacred_object_or_symbol` | 神聖な依代 | logo, mascot, symbol | Asante 黄金の床几 (既存)、Wikipedia globe (新規) |
| S5 Policy/Identity | `s5::lineage_authority` | 系譜的権威 | founder lineage, founder narrative | 比叡山 (最澄)、三井 (高利)、Cluny (Bernard 系) |

## 5. 拡張後の機能数

- マスター: 25 (不変)
- sub-function 候補: 上記表で **約 70 個** (M11-M20 + VSM で密度高)
- 合計識別子空間: **25 + 70 = 95 (理論上)**、実用的に観察される sub-function は **50-60 程度**になる見込み

提案の現実的目標は **「マスター 25 + sub-function 50」前後**。これが Miller 1978 の subsystem 内分類 (各 subsystem は内部に複数の component を持つ) と同程度の解像度になる。

## 6. 18 ケースを sub-function でリビジット

未使用 10 機能で**新たに観察できる record 数**を概算する (重複なし、保守的見積もり):

| 未使用機能 | 新規観察可能ケース | 件数 |
| --- | --- | --- |
| M11 Input Transducer | MakerDAO oracle, Linux Foundation issue, Wikimedia village pump, Grameen 加入手続き, VOC trade report, ムガル査察報告 | **6** |
| M12 Internal Transducer | 鴻池大福帳 (M17 と二重分類)、MCC 内部監査、MakerDAO observability、ムガル dagh (S3 と二重分類)、Linux Foundation CI、VOC ledger (M17 と二重分類) | **6** |
| M14 Timer | ベネディクト Liturgy of the Hours、シトー会 General Chapter、MakerDAO block time、Linux Foundation release train、MCC 年次会議、ボローニャ大学 academic year | **6** |
| M15 Decoder | ボローニャ大学 (glossae)、ムガルペルシア語、Wikimedia 多言語、Linux Foundation license check、Inca quipu type、Cluny 教皇文書解釈 | **6** |
| M16 Associator | ボローニャ大学、シトー会 General Chapter (S2 と二重分類)、MakerDAO risk model、Linux Foundation post-incident、ムガル年代記、Wikimedia bot | **6** |
| M20 Output Transducer | Wikimedia 公開、Linux Foundation publication、MakerDAO event emit、Asante 黄金の床几 (S5 と二重分類)、VOC auction announcement、Cluny 教皇布告 | **6** |
| M05 Converter | ベネディクト novitiate、MCC Mondragón 大学、Wikimedia bot pre-processing、Linux Foundation training | **4** |
| M08 Extruder | Wikimedia ban (M02 と二重分類)、Linux Foundation deprecation、MakerDAO emergency shutdown、ハンザ unhansing (M02 と二重分類) | **4** |
| M09 Motor | VOC 船団 (既存ケース内再分類)、Inca chasqui (M13 と二重分類)、Linux Foundation CI/CD、MakerDAO transaction broadcast | **4** |
| M10 Supporter | Wikimedia インフラ、Linux Foundation インフラ、MakerDAO Ethereum 依存、VOC 倉庫網、ベネディクト修道院建築、ボローニャ大学 college 制度 | **6** |

**合計新規 record (二重分類含む): 約 54 件**
**保守的に二重分類を排除 (ユニーク): 約 35-40 件**

現状 77 records → 拡張後 **120-130 records** が見込まれる。VSM/Miller 比率も改善 (Miller 53/77 → Miller 100+ で偏り是正)。

## 7. マイグレーション戦略 (バックワード互換)

### Phase A: スキーマ追加 (破壊なし)

```sql
ALTER TABLE function_record
  ADD COLUMN sub_function_id TEXT;
ALTER TABLE function_record
  ADD COLUMN sub_function_evidence TEXT; -- JSON: {means, indicators}

CREATE INDEX idx_fr_subfn ON function_record(sub_function_id);
```

`function_type_id` enum は不変。既存 77 records は `sub_function_id IS NULL` で valid。

### Phase B: sub_function 辞書テーブル

```sql
CREATE TABLE function_subtype (
  sub_function_id     TEXT PRIMARY KEY,           -- 'm14::block_epoch'
  function_type_id    TEXT NOT NULL REFERENCES function_type(function_type_id),
  name_ja             TEXT NOT NULL,
  name_en             TEXT NOT NULL,
  definition          TEXT NOT NULL,              -- Miller/Beer 原典内に収まる範囲
  era_examples        TEXT,                       -- JSON {ancient, ..., digital}
  added_in_version    TEXT NOT NULL DEFAULT 'codex7_v2',
  source_citation     TEXT                        -- e.g., "Miller 1978: 39"
);
```

### Phase C: 既存 77 records のリビジット (任意)

リサーチャーが手動で `UPDATE function_record SET sub_function_id = ?` を行う。リビジット完了率は KPI として追跡。**未リビジットでもクエリは破綻しない**。

### Phase D: 集計クエリの両立

```sql
-- master 別集計 (旧クエリ、無変更で動く)
SELECT function_type_id, COUNT(*) FROM function_record GROUP BY function_type_id;

-- sub-function 別集計 (新規)
SELECT function_type_id, sub_function_id, COUNT(*)
FROM function_record
WHERE sub_function_id IS NOT NULL
GROUP BY function_type_id, sub_function_id;
```

ヒートマップ (`etl/13_function_heatmap.py`) は無変更で動く。新ヒートマップ `13b_subfunction_heatmap.py` を追加するだけ。

### Phase E: 検証

- Miller 1978 と Beer 1972/1979/1985 への引用突合: sub_function definition が原典の subsystem 説明から逸脱していないか reviewer が確認。
- 既存 77 records の集計結果が拡張前後で**完全一致**することを CI で検証 (`function_type_id GROUP BY` の結果)。

## 8. 原典対応の確認

- **Miller 1978**: subsystem 概念は本書 chapter 3 (pp. 18-31) で生命システムの 7 階層全てに対し定義される。各 subsystem は内部に component を持つ (例: Channel and Net は p. 65 で「neurons, hormones, written documents, telephone wires」を含むと明示)。本提案の sub_function は Miller の component 列挙の組織版である。
- **Beer 1972 *Brain of the Firm***: VSM は recursive で各 system 内に sub-systems を持つ (chapter 8-9)。S5 を `founding_charter / value_creed / sacred_object_or_symbol / lineage_authority` に分けるのは Beer 1979 *Heart of Enterprise* p. 258 の identity の 4 facet (purpose, ethos, pathos, logos) に近接する。
- **逸脱しないルール**: sub_function の definition には「smart contract」「blockchain」「webhook」のような **2010 年代以降の固有名**を含めない。era_examples の `digital` フィールドにのみ書く。

## 9. 結論

- 25 マスター機能はそのまま正本として残し、観察解像度の問題は sub_function 層で解く。
- 拡張で **既存 77 records → 約 120-130 records**、未使用 10 機能のうち **少なくとも 6-8 が観察可能**になる。
- 最も観察可能になるのは **M14 Timer**, **M11 Input Transducer**, **M20 Output Transducer**, **M15 Decoder** の情報処理層。これらはデジタル組織で物理的単位として再前景化する。
- バックワード互換性は完全。既存クエリ・集計は無変更で動作。
