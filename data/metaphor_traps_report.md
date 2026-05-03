# Metaphor Traps Audit

- Database: `data/og.db`
- Scope: existing SQLite tables only; no DB writes.
- Interpretation: detections are review candidates, not automatic proof of error.

## Summary

| Trap | Count |
| --- | ---: |
| Reification | 0 |
| Circular survival | 0 |
| Boundary ambiguity | 0 |
| Functionalist hindsight | 99 |
| Biological over-import usage check | 38 |

## 1. Reification

Regex review of `organization.description`, `activity.description`, and `claim.interpretation_note` for organization subjects directly paired with biological verbs.

_No records detected._

Recommendation: replace organism-subject phrasing with explicit mechanism claims, or attach a source-backed interpretation note that marks the phrase as metaphorical.

## 2. Circular Survival

`event.dissolution_cause = 'obsolescence'` rows were checked for survival-of-the-fittest style explanations.

_No records detected._

Recommendation: require a concrete causal chain such as technology shift, regulatory change, fiscal collapse, or successor institution, not a tautological selection label.

## 3. Boundary Ambiguity

Boundary-related claims were grouped by organization and flagged only when multiple jurisdiction values or open/closed boundary claims co-occurred.

_No records detected._

Recommendation: encode boundary claims with time validity and boundary dimension, for example legal jurisdiction, membership, territory, or operational network.

## 4. Functionalist Hindsight

`function_record.confidence >= 0.9` with `claim_id` NULL or empty.

| function_id | organization | function_type | confidence | mechanism |
| --- | --- | --- | --- | --- |
| 3d361fad0021484dbd1083fa83a5949f | Cluny 修道会 (Order of Cluny) | miller_01_reproducer / Reproducer | 0.95 | {"means": ["母院 (Cluny) からの修道士派遣による新修道院創立", "Cluny Customs (Liber Tramitis) の適用"]} |
| 95bf815f9196416d9fc49260ab6015fe | Cluny 修道会 (Order of Cluny) | miller_02_boundary / Boundary | 0.95 | {"means": ["教皇直属の特権", "世俗領主からの独立 (Roman Church の傘下)"]} |
| ee99d6f08ca949e1a361473e3113b9c1 | Defense Advanced Research Projects Agency (DARPA) | miller_03_ingestor / Ingestor | 0.95 | {"means": ["連邦予算 (DOD)", "Congressional appropriation"]} |
| 1fc75f35eff5477ba29cf0a903521699 | Defense Advanced Research Projects Agency (DARPA) | miller_04_distributor / Distributor | 0.95 | {"means": ["BAA (Broad Agency Announcement)", "contracts to universities/labs"]} |
| ac6bf7e4fb9b4989965c7981ea6b1bf8 | Defense Advanced Research Projects Agency (DARPA) | miller_18_decider / Decider | 0.95 | {"means": ["Program Manager の選定権限", "Director の承認", "DOD 上位の予算枠"], "note": "Program Manager の '帝王的' 権限が ARPA Model の核"} |
| 314b5115ff744ef5a7b26081db76c95f | Grameen Bank | vsm_s2_coordination / System 2 Coordination | 0.95 | {"means": ["週次 group meeting", "village center 監督", "5 人グループの相互信用評価"]} |
| f311a1c9ff1f4654abe6dfc5320e019d | Greenpeace International (Stichting Greenpeace Council) | miller_20_output_transducer / Output Transducer | 0.95 | {"means": ["media spectacle (ボート対峙画像)", "photo journalism", "social media"], "note": "メディア露出が主な政治的影響経路"} |
| 7903147ce4754e92a743ee041e22adfe | Hadza バンド (Hadzabe) | miller_18_decider / Decider | 0.95 | {"means": ["コンセンサス + ゴシップ + 嘲笑による自発的服従"], "note": "中央集権なし、Boehm reverse dominance hierarchy"} |
| 90251fc311e444a981e48c55954f2b99 | International Committee of the Red Cross (ICRC) | vsm_s5_policy_identity / System 5 Policy and Identity | 0.95 | {"means": ["7 Fundamental Principles", "中立 / 公平 / 独立"]} |
| e48d80715a224ccaa1a1cbe4b14eee48 | Linux Foundation | miller_03_ingestor / Ingestor | 0.95 | {"means": ["企業会費", "スポンサーシップ", "KubeCon 等カンファレンス収益"]} |
| 494a4e9527ce48ae8cf93e7c828a0f9d | Linux Kernel Community | miller_13_channel_and_net / Channel and Net | 0.95 | {"means": ["Linux Kernel Mailing List (LKML)", "Git distributed VCS (Torvalds 開発, 2005-)", "patchwork / lore.kernel.org"]} |
| b43cf50857164f2c8434b60b41a4cca0 | Linux Kernel Community | miller_17_memory / Memory | 0.95 | {"means": ["Git history (cryptographic immutability)", "lore.kernel.org メールアーカイブ"]} |
| 46291dbfdbfb49cf894b18f00da52a56 | MakerDAO | miller_17_memory / Memory | 0.95 | {"means": ["Ethereum blockchain (immutable record)"]} |
| e3be5deb2ba343c7999d5be9026bb5ed | Mondragón Corporación Cooperativa (MCC) | miller_03_ingestor / Ingestor | 0.95 | {"means": ["組合員出資 (~€15,000 加入金)", "Caja Laboral 預金"]} |
| 842aadd83d1a49fda2a9c9c607365cda | Toyota Motor Corporation | miller_06_producer / Producer | 0.95 | {"means": ["TPS", "Just-In-Time", "kanban", "jidoka", "takt time"]} |
| 3c0da7107004464bb5b5de309d0a5d70 | United Nations (UN) | miller_18_decider / Decider | 0.95 | {"means": ["安保理 (拘束力ある決議)", "総会 (勧告)", "P5 拒否権"]} |
| 0442fab0421746fa9cc63da3bfa06446 | Wikimedia Foundation | miller_03_ingestor / Ingestor | 0.95 | {"means": ["寄付 (主)", "grant", "merchandise"]} |
| 1f79b079e0154fbc9ccc547d7bb0cc65 | Wikimedia Foundation | miller_17_memory / Memory | 0.95 | {"means": ["記事履歴 (永久保存)", "talk page アーカイブ", "CC-BY-SA license で再配布可"]} |
| c175289736cc44dd8587b6a12f4bcddf | アル・アズハル (Al-Azhar Mosque & University) | miller_17_memory / Memory | 0.95 | {"means": ["写本・図書館 (al-Azhar Library)", "口承イスナード (伝承連鎖) の保持"]} |
| b05240c070464801bb056408d4786fb9 | ウルク Eanna 神殿 (Eanna Temple of Uruk) | miller_17_memory / Memory | 0.95 | {"means": ["proto-cuneiform 粘土板", "数値トークン"]} |

_Showing 20 of 99 records._

Recommendation: either attach a source-backed claim or lower confidence until the mechanism has provenance.

## 5. Biological Over-Import Usage Check

Usage count for Miller physical processing subsystems at organization level: Ingestor, Distributor, Converter, Producer, Matter-Energy Storage, Extruder, Motor, Supporter.

| function_id | organization | function_type | confidence | mechanism |
| --- | --- | --- | --- | --- |
| ee99d6f08ca949e1a361473e3113b9c1 | Defense Advanced Research Projects Agency (DARPA) | miller_03_ingestor / Ingestor | 0.95 | {"means": ["連邦予算 (DOD)", "Congressional appropriation"]} |
| fa554c03661348d78edc2bc1ac8a2ad7 | Grameen Bank | miller_03_ingestor / Ingestor | 0.85 | {"means": ["顧客の貯蓄", "国際援助 (初期)", "商業預金"]} |
| 4108b59e675140f48f70215a2299f82e | Greenpeace International (Stichting Greenpeace Council) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["小口寄付 (政府・企業献金は受け取らない)", "supporter base 3M+"]} |
| e48d80715a224ccaa1a1cbe4b14eee48 | Linux Foundation | miller_03_ingestor / Ingestor | 0.95 | {"means": ["企業会費", "スポンサーシップ", "KubeCon 等カンファレンス収益"]} |
| e3be5deb2ba343c7999d5be9026bb5ed | Mondragón Corporación Cooperativa (MCC) | miller_03_ingestor / Ingestor | 0.95 | {"means": ["組合員出資 (~€15,000 加入金)", "Caja Laboral 預金"]} |
| e742086ad71e4ecfb046ed802cbd8683 | Self-Employed Women's Association (SEWA) | miller_03_ingestor / Ingestor | 0.8 | {"means": ["組合員月会費", "Mahila SEWA Bank 預金", "国際協力機関助成 (Ford Foundation, ILO 等)"]} |
| 0442fab0421746fa9cc63da3bfa06446 | Wikimedia Foundation | miller_03_ingestor / Ingestor | 0.95 | {"means": ["寄付 (主)", "grant", "merchandise"]} |
| ea9054275fb24e30951ea1244fac07f2 | アシャンティ王国 (Asante Empire) | miller_03_ingestor / Ingestor | 0.8 | {"means": ["金鉱税", "奴隷貿易税", "属州貢納"]} |
| 043596cf75e94929ac7ae05b7da97246 | アル・アズハル (Al-Azhar Mosque & University) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["waqf 寄進による永久財源", "学生からの授業料は伝統的に無し (waqf が教師俸給を負担)"]} |
| 74106464939d49c98033ca62e9b83921 | インカ帝国 (Tahuantinsuyu) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["mit'a (賦役)", "tribute (各 ayllu からの貢納)"], "note": "通貨なし、現物・労働ベース"} |
| 627071f963414e8c9d01d1301042d8df | ウルク Eanna 神殿 (Eanna Temple of Uruk) | miller_03_ingestor / Ingestor | 0.85 | {"means": ["租税・貢納", "神殿土地からの収穫", "強制労働 (corvée)"]} |
| 087fca9d0409444a828463d79999ca31 | エジプト第18王朝の宰相 (djati / vizier) | miller_03_ingestor / Ingestor | 0.8 | {"means": ["徴税監督 (収穫税、人頭労役)"]} |
| cef63c13e84c45f6981ffc04446cb362 | オスマン・ティマール制 (Ottoman Timar System) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["tahrir 台帳に基づく徴税", "öşür (収穫税)・çift resmi (ヤク税) 等の体系"]} |
| c97f15f7538641318360137cc89fa5ec | オランダ東インド会社 (VOC) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["IPO", "bond issuance", "trade revenue"]} |
| 428e6669b4f84b959323378b2d57d87d | スレイマニエ・キュリエ (Süleymaniye Külliyesi) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["ワクフ財産からの賃料・地代", "皇室追加寄進"]} |
| cc78dfd7b7e241ee94e3b58a8116c889 | バイト・アル=ヒクマ (Bayt al-Ḥikma / House of Wisdom) | miller_03_ingestor / Ingestor | 0.85 | {"means": ["カリフ俸給 (パトロン制)", "ビザンツへの遣使による写本獲得 (ex. al-Maʾmūn → Leo VI 提案)"]} |
| b30900f250504342a57062f452ca018d | ムガル朝マンサブダール制 (Mansabdari System) | miller_03_ingestor / Ingestor | 0.9 | {"means": ["jagir (徴税権)", "khalisa (皇室直轄地)"], "note": "jagir は数年で別地に転換され、所領化を防ぐ"} |
| a549db69095e44348f9bf3307fa26a01 | ローマ軍団 (Roman legio, post-Marian) | miller_03_ingestor / Ingestor | 0.85 | {"means": ["徴募 (dilectus)", "退役兵土地給付による継続的補充"]} |
| 7a6fc88797904a8f8582f47978a46a06 | 堺会合衆 (Sakai Egoshu) | miller_03_ingestor / Ingestor | 0.7 | {"means": ["関税相当の入市料", "商工業者からの賦課金", "矢銭 (戦時拠出)"]} |
| c07af3f0989e4fab878b6d84df4d6dad | 鴻池家 | miller_03_ingestor / Ingestor | 0.9 | {"means": ["酒販売益", "為替手数料", "大名貸利息", "幕府御用金"]} |

_Showing 20 of 38 records._

Recommendation: treat this as an inventory, not an error list. For physical-processing labels, require a human-readable organizational analogue in `mechanism`.
