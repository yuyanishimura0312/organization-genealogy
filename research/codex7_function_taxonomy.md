# Codex7 Function Taxonomy

## 目的

このタクソノミーは、`research/codex2_data_model.md` の Function テーブルにある `function_type` 列挙の正本である。活動が「何をしたか」を表すのに対し、Function は「その活動が組織生命としてどの機能を果たしたか」を記録する。

設計上の主軸は James Grier Miller の *Living Systems* における 20 critical subsystems と、Stafford Beer の Viable System Model における S1-S5 である。合計 25 機能を master taxonomy とし、Aldrich の VSR、Teece の Dynamic Capabilities、March の exploration/exploitation は機能ではなく、時間軸上の変化イベントや適応エピソードを読む横断軸として扱う。

## 出典と注意

- Miller: James Grier Miller, *Living Systems* (McGraw-Hill, 1978)。本リポジトリの `research/A_theoretical_foundations.md` も同書を典拠としている。
- Miller の 20 critical subsystems は、1 Reproducer, 2 Boundary, 3 Ingestor, 4 Distributor, 5 Converter, 6 Producer, 7 Matter-Energy Storage, 8 Extruder, 9 Motor, 10 Supporter, 11 Input Transducer, 12 Internal Transducer, 13 Channel and Net, 14 Timer, 15 Decoder, 16 Associator, 17 Memory, 18 Decider, 19 Encoder, 20 Output Transducer とする。
- ユーザー提示リストには `Timer` が含まれていなかったが、20 機能にするには Miller 系統の一覧で使われる `Timer` を入れる必要がある。
- Beer: Stafford Beer, *Brain of the Firm* (1972), *The Heart of Enterprise* (1979), *Diagnosing the System for Organizations* (1985)。VSM は S1 Operations, S2 Coordination, S3 Internal control, S4 Intelligence/Strategy, S5 Policy/Identity として扱う。S3* audit は独立した 6 番目の VSM 機能ではなく、S3 の監査チャネルとして `vsm_s3_internal_control` に含める。
- Aldrich: Howard E. Aldrich, *Organizations Evolving* (1999)。Variation, Selection, Retention, Struggle は function_type ではなくイベント軸。
- Teece: Teece, Pisano & Shuen (1997), Teece (2007)。Sensing, Seizing, Transforming/Reconfiguring は function_type ではなく適応サイクル。
- March: March (1991) "Exploration and Exploitation in Organizational Learning"。探索・活用は function_type ではなく活動・イベントの orientation。

## 設計判断

1. Miller は「生命システムが存続するために必要な処理機能」の網羅表として使う。
2. Beer は「現業単位をどう存続可能に制御するか」のメタ機能として Miller とは別列で使う。
3. VSR、Dynamic Capabilities、Exploration/Exploitation は、ある時点で組織が持つ機能ではなく、機能が時間の中でどう変化・選択・保持されるかを表す軸として扱う。
4. `function_id` は `function_type` にそのまま格納できる snake_case の安定 ID とする。
5. 歴史比較のため、各機能は ancient, medieval, modern, contemporary, digital の 5 時代例を持つ。

## 25 機能一覧

| function_id | 日本語名 | English | Miller | VSM | 定義 |
| --- | --- | --- | --- | --- | --- |
| `miller_01_reproducer` | 再生産 | Reproducer | 1 |  | 組織の憲章、型、構成単位、後継単位を複製し、同型または派生的な組織を生み出す機能。 |
| `miller_02_boundary` | 境界維持 | Boundary | 2 |  | 組織の内外を区分し、成員、資源、情報、権限の出入りを許可・遮断・条件付ける機能。 |
| `miller_03_ingestor` | 取り込み | Ingestor | 3 |  | 外部環境から人員、資金、物資、エネルギー、原材料を組織内へ取り入れる機能。 |
| `miller_04_distributor` | 配分 | Distributor | 4 |  | 取り込まれた資源を組織内の単位、工程、地域、役割へ移送・配分する機能。 |
| `miller_05_converter` | 変換 | Converter | 5 |  | 入力された資源の形態、品質、利用可能性を変え、組織が使える中間資源にする機能。 |
| `miller_06_producer` | 生産 | Producer | 6 |  | 組織の目的に沿う財、サービス、制度的成果、公共財を作り出す機能。 |
| `miller_07_matter_energy_storage` | 物質・エネルギー貯蔵 | Matter-Energy Storage | 7 |  | 資源を将来利用できるよう蓄積、保管、在庫化、予備化する機能。 |
| `miller_08_extruder` | 排出 | Extruder | 8 |  | 不要物、廃棄物、余剰、リスク、退職者、不適合資源を組織外へ出す機能。 |
| `miller_09_motor` | 移動・作動 | Motor | 9 |  | 組織または構成要素を空間的・作業的に移動させ、行動を実行可能にする機能。 |
| `miller_10_supporter` | 支持・構造保持 | Supporter | 10 |  | 構成要素の位置関係、物理的基盤、制度的骨格を維持し、組織形態を支える機能。 |
| `miller_11_input_transducer` | 入力変換 | Input Transducer | 11 |  | 外部環境からの情報信号を検知し、組織内で処理できる形に変換する機能。 |
| `miller_12_internal_transducer` | 内部状態変換 | Internal Transducer | 12 |  | 組織内部の状態、活動、異常、成果を検知し、管理可能な情報へ変換する機能。 |
| `miller_13_channel_and_net` | 通信路・ネットワーク | Channel and Net | 13 |  | 情報を構成単位間で運ぶ通信路、会議体、文書経路、ネットワークを維持する機能。 |
| `miller_14_timer` | 時間調整 | Timer | 14 |  | 活動の順序、周期、期限、同期、リズムを生成し、時間的整合性を保つ機能。 |
| `miller_15_decoder` | 解読 | Decoder | 15 |  | 外部または内部から入った情報を、組織内で理解・処理できるコード、分類、意味へ変換する機能。 |
| `miller_16_associator` | 関連付け・学習 | Associator | 16 |  | 複数の情報項目を結び付け、パターン、因果仮説、経験則、学習を形成する機能。 |
| `miller_17_memory` | 記憶 | Memory | 17 |  | 情報、手続き、歴史、権利、関係、判断理由を保存し、必要時に検索・再利用する機能。 |
| `miller_18_decider` | 意思決定 | Decider | 18 |  | 他の機能から情報を受け取り、選択、優先順位、命令、制御方針を決める中枢的機能。 |
| `miller_19_encoder` | 符号化 | Encoder | 19 |  | 内部判断や知識を、外部または他部門が解釈できる言語、文書、命令、規格、信号へ変換する機能。 |
| `miller_20_output_transducer` | 出力変換 | Output Transducer | 20 |  | 内部で符号化された情報を、環境中の媒体や相手に届く形へ物理的・技術的に出力する機能。 |
| `vsm_s1_operations` | 現業・一次活動 | System 1 Operations |  | S1 | 環境と直接相互作用し、組織の主要価値を実行する自律的な現業単位の機能。 |
| `vsm_s2_coordination` | 調整・安定化 | System 2 Coordination |  | S2 | 複数の現業単位間の摩擦、振動、重複、衝突を抑え、運用を安定させる機能。 |
| `vsm_s3_internal_control` | 内部統制・最適化 | System 3 Internal Control and Audit |  | S3 | 現業単位全体の資源配分、内部統制、短中期の最適化を行い、S3* 的な監査で報告の現実性を検証する機能。 |
| `vsm_s4_intelligence_strategy` | 環境知能・戦略 | System 4 Intelligence and Strategy |  | S4 | 外部環境と未来を探索し、長期適応、研究、戦略、変化への応答を設計する機能。 |
| `vsm_s5_policy_identity` | 方針・同一性 | System 5 Policy and Identity |  | S5 | 組織の目的、価値、正統性、許容リスク、同一性を定め、現在志向の S3 と未来志向の S4 の緊張を裁定する機能。 |

## 観察可能な指標の使い方

指標は「機能の実在を示す痕跡」として扱う。たとえば `miller_17_memory` なら文書館、帳簿、議事録、データベース、検索可能な履歴が指標になる。`vsm_s2_coordination` なら標準手順、調整会議、共有カレンダー、依存関係管理、衝突の減少が指標になる。

個別の指標と時代別例は `codex7_function_taxonomy.json` の各 function object に格納した。データ投入時は、Function レコードの `function_type` に 25 ID のいずれかを入れ、具体的な仕組みは `mechanism`、根拠は `claim_id` で管理する。

## 横断軸

### VSR

Aldrich の Variation, Selection, Retention, Struggle は function_type ではなく、イベント列に付与する変化ラベルである。例として、新しい支部制度の導入は variation、失敗した支部の閉鎖は selection、成功した支部規約の標準化は retention、資源・正統性をめぐる競合は struggle として記録する。

### Dynamic Capabilities

Teece の Sensing, Seizing, Transforming/Reconfiguring は、適応エピソードのフェーズとして扱う。Sensing は `miller_11_input_transducer`、`miller_15_decoder`、`miller_16_associator`、`vsm_s4_intelligence_strategy` を多用する。Seizing は `miller_18_decider`、`miller_04_distributor`、`vsm_s3_internal_control` と結び付きやすい。Transforming/Reconfiguring は S1-S3 の構造、`miller_10_supporter`、`miller_17_memory`、`miller_06_producer` を変更する。

### Exploration / Exploitation

March の exploration/exploitation は、機能分類ではなく活動やイベントの orientation とする。同じ `miller_06_producer` でも、新規プロトタイプ生産なら exploration、既存製品の効率化なら exploitation である。したがって `exploration` や `exploitation` を `function_type` にしない。

## codex2 への実装メモ

- `Function.function_type` は `codex7_function_taxonomy.json` の `function_type_enum` に制約する。
- `Function.mechanism` には具体的制度、部門、技術、手続き、役職を入れる。
- `Activity.activity_type` は行為の種類、`Function.function_type` は生命システム上の役割として分離する。
- VSR / Dynamic Capabilities / March 軸は `Event` または将来の `ChangeEpisode` に `cycle_phase` / `orientation` として持たせるのがよい。

