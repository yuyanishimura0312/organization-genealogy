# Stream I: 組織の死・解散・継承パターン

事前リサーチノート（第2波） / 担当: Stream I / 日付: 2026-05-02
姉妹文書: A_theoretical_foundations / B_historical_genealogy / C_typologies / D_existing_databases / E_innovation_theory / F_methodology / codex1-3

---

## 概要

組織を生命体として扱うなら誕生のみならず「死・解散・継承」もデータ化する必要がある。第1波 D で「組織の死データはほぼ存在しない（誕生に偏る）」と判明したため、本ノートは死亡理論（Stinchcombe / Hannan-Freeman / Brüderl / Barron-West）、企業破綻データ源（CRSP / US Courts / TDB / TSR / OECD-Eurostat / BLS-BED）、歴史事例（VOC / ITT / Lehman / Enron / Andersen / 財閥解体 / シニセ）、継承メカニズム（家族企業・修道会・ブランド再ライセンス）を整理し、Event スキーマに `dissolution_cause / successor / legacy` を加えるための実証的足場を提供する。

---

## 死亡・解散の理論（7件）

### 1. Liability of Newness（Stinchcombe 1965）
Arthur Stinchcombe が "Social Structure and Organizations" (Handbook of Organizations, 1965) で提示。新しい組織が高い失敗率を負う理由は (a) 新しい役割の学習コスト、(b) 標準化されたルーチン不在、(c) 見知らぬ他者との関係構築、(d) 既存組織との競争での顧客基盤未確立。失敗ハザード関数は年齢に対して単調減少、というのが古典命題。Wharton による2017年再検証（"The Liability of Newness Revisited"）あり。

### 2. Structural Inertia + Age Dependence（Hannan & Freeman 1984; 1989）
"Structural Inertia and Organizational Change" (American Sociological Review 49: 149-164, 1984) で「信頼性・説明責任の追求が硬直性を生み、変化試行そのものが死亡率を上げる」と論じた。Hannan は1998年 American Journal of Sociology の "Rethinking Age Dependence in Organizational Mortality: Logical Formalizations" で年齢効果を再公理化。ハザードのパターンは (i) 年齢で減少、(ii) U字（adolescence）、(iii) 年齢で上昇（senescence/obsolescence）の三つに整理される。

### 3. Liability of Adolescence（Brüderl & Schüssler 1990）
Administrative Science Quarterly 35(3): 530-547。ミュンヘン＆上バイエルンの全企業登記/抹消データ（1980-1989, n>171,000）を用い、初期資源 endowment が monitoring 期間を生む結果、ハザードは創業1〜15年後にピークを迎える「逆 U」を実証。Stinchcombe の単調減少を否定。

### 4. Liability of Senescence vs. Obsolescence（Barron, West & Hannan 1994）
ニューヨーク信用組合 1914-1990 を分析。Senescence = 内部効率の劣化（sclerosis）、Obsolescence = 外部環境とのミスマッチ。両者を区別することが重要との主張。Sørensen & Stuart (2000) "Aging, Obsolescence, and Organizational Innovation" (ASQ) が技術環境ドリフトを通じた obsolescence を実証。

### 5. Density Dependence（Hannan & Carroll 1992 *Dynamics of Organizational Populations*）
個体群密度が legitimation（少数時に supra-linear に上昇）と competition（多数時に supra-linear に上昇）の両方を駆動し、誕生率と死亡率に逆 U / U 字の効果。ヨーロッパ自動車産業 1886-1981、米ビール産業など多数の実証。Carroll & Hannan (2000) *The Demography of Corporations and Industries* に集大成。

### 6. Cohort / Imprinting Effect
Stinchcombe imprinting hypothesis を Carroll & Hannan が cohort dependence として再定式化。創業時の環境条件（規制・技術・資源）が長期生存パターンに刻印される。経済危機コホート（1929年, 2008年, COVID）の生存曲線比較が古典手法。

### 7. Autocatalytic Genesis & Termination（Padgett & Powell 2012）
*The Emergence of Organizations and Markets* (Princeton UP)。Production / linguistic / biographical autocatalysis の三層が交差する複数ネットワークから新形式が emerge する一方、autocatalytic loop の崩壊が組織解体の機序。中世フィレンツェのパートナーシップ・17世紀オランダ合本会社・19世紀ドイツ帝国議会の事例を含む。「死」とは autocatalytic 反応の停止である、というのが我々のデータベース設計に直結する含意。

### 補助理論（メモ）
- **Liability of smallness**（Aldrich & Auster 1986）— 規模が小さいほど死亡率が高い。年齢効果と交絡。
- **Resource partitioning**（Carroll 1985）— ジェネラリスト集中市場でスペシャリストが生存するニッチ。
- **Red Queen**（Barnett & Hansen 1996）— 競争経験が能力と脆弱性を同時に上げる。

---

## 死亡・解散・継承の歴史的・現代的事例（13件）

### A. 解散・破綻

1. **VOC オランダ東インド会社解散（1799）** — 1602年設立、世界初の株式会社。第四次英蘭戦争（1780-84）で財務崩壊、1796年バタヴィア共和国により国有化、1799/12/31 特許状失効。資産・負債・植民地（蘭領東インド）はオランダ政府に承継。組織の死と資産の継承が分離した古典例。

2. **リーマン・ブラザーズ破綻（2008/9/15）** — 164年の歴史。Chapter 11 申請時の資産 6,000億ドル超で米史上最大。サブプライム関連 illiquid asset と 40:1 のレバレッジが直接原因。北米 IB 部門は Barclays、欧州・アジア部門は野村が買収 — ブランドは消滅したが人材・コードベース・取引先関係は継承。Dodd-Frank 法（2010）の起爆剤。

3. **Enron 崩壊（2001/12/2）** — 60億ドル超の負債を mark-to-market、SPE で隠蔽。株価は 2000/8 の $90 から 2001/11 の $1未満へ。4,000人即時解雇、15,000人の年金消滅、株主損失 ~110億ドル。Sarbanes-Oxley Act (2002) を生み出した。

4. **Arthur Andersen 解体（2002）** — Big Five の一角、世界中に 28,000人の従業員。Enron 関連文書のシュレッダー破棄で 2002/3/14 司法妨害起訴、6/15 有罪。SEC 監査ライセンス自主返上で 2002/8/31 実質廃業。最高裁は 2005年に有罪判決を破棄したが組織は復活せず — *再活性に失敗した稀有な事例*。多くのパートナーは Deloitte / EY / KPMG / PwC へ移籍 — 人材は分散承継。

5. **戦前財閥解体（GHQ 1945-1948）** — 16財閥が完全解体対象、26財閥が再組織化対象（Asano, Furukawa, Nakajima, Nissan, Nomura, Okura ほか）。持株会社解散、家族資産凍結、interlocking directorship 禁止、独占禁止法。冷戦激化（reverse course）で1948以降不徹底に終わり、戦後 keiretsu（三菱・三井・住友・芙蓉・三和・第一勧銀）として*同型再生*。組織の「眠り→再活性」典型。

### B. 分裂・スピンオフ

6. **ITT 三分割（1995）** — Geneen 時代の巨大コングロマリットを Rand Araskog が16年かけて自発的に分解。ITT Hartford（保険、年商 $11B）/ ITT Industries（自動車部品・防衛・電子）/ ITT Corp.（Sheraton, Caesars, MSG）。米企業史上最大規模の自発的解体。Cusatis-Miles-Woolridge (1993, J. Financial Economics 33:293-311) が示した「スピンオフ後3年間の超過リターン」の経験的裏付けの一例。

7. **Cluny → Cîteaux 分派（1098）** — Cluny 改革派（910創設、12世紀には1,000院超のネットワーク）の世俗化・贅沢化に反発し Molesme 出身の修道士が Cîteaux 修道院を設立、Benedict Rule 厳格回帰。13世紀第一四半期まで Cluny を凌駕。組織の「腐敗→分派改革→世代交代」のパターン。修道院ネットワーク全体を一つの「個体群」と見なすと density dependence が観察可能。

8. **欧州主要民主主義における政党フラグメンテーション（1960-2025）** — 西側民主主義における effective number of electoral parties (ENEP) の長期上昇。ドイツでは1970年代に二大政党合計90%以上 → 2017年には53%まで低下し六党体制化。組織分裂が個体群の「種分化」として観察できる例。

### C. 継承・再活性

9. **シニセ（老舗）と日本の長寿企業** — 200年以上存続する企業の半数以上が日本に集中。33,000社（100年超）、3,100社（200年超）、140社（500年超）、19社（1000年超）と推計（2020）。家訓 (kakun) による継続・本業集中・現金準備・負債回避が共通項。一方で 2022年に 100年超企業 33社が廃業 — 後継者不在 (jigyō shōkei) が現代的死因として浮上。

10. **Mondragon と Fagor** — 1956年バスク創設、100超の労働者協同組合連合体。協同組合は5年生存率80%（株式会社44%）と高い（UK Co-operatives 統計）。一方 2013年 Fagor Electrodomésticos S. Coop の破綻はグループ最大の事件で、「協同組合だから永続する」神話を壊した。Rochdale-ICA 系譜から Mondragon 原則が "descent with modification" した点も継承研究として重要。

11. **Nokia → HMD Global（2014-2026）** — 1865年創業の Nokia は携帯部門を 2014 年 Microsoft に売却、2016年に元 Nokia 幹部が HMD Global を設立し Foxconn と組んで携帯資産を $350M で買収・Nokia ブランドのライセンスを取得（2026年まで、2025年に2-3年延長）。2024 年から HMD は自社ブランドにシフト、2025年で Nokia smartphone 終了（feature phone のみ存続）。「ブランド継承による組織の死後生」の現代モデル。

12. **家族企業の世代継承統計** — 30%が二代目、12%が三代目、3%が四代目以降に到達（FBCG, Morgan Stanley, HBR 2021）。ただし HBR 2021 は「失敗の定義」を問題化（事業売却、ロールアップ、戦略買収は単純な「失敗」ではない）。Stinchcombe imprinting と承継準備の交差が研究フロンティア。

13. **Jesuit 禁圧と復活（1773 → 1814）** — 教皇 Clement XIV が 1773 にイエズス会を formal suppression、1814 に Pius VII が restoration。41年の「死亡期間」を経た再活性 — ロシア領内で形式的存続を保ったため完全消滅は回避。組織の「眠り (dormancy)」が法人格レベルで部分的に維持されると復活確率が上がるという仮説の歴史的裏付け。Benedict 系は逆に各 abbey 独立性が高く、個別院の死と全体（congregation）の永続が両立する分散モデル。

---

## 既存データ源マトリクス — 何が記録されていて何が抜けているか

| データ源 | 範囲 | 記録される事象 | 主要識別子 | 死因の分類 | 後継者 (successor) リンク | 抜けているもの |
|---|---|---|---|---|---|---|
| **CRSP delisting codes** (米株式) | NYSE/AMEX/Nasdaq 上場銘柄 | 上場廃止 | PERMNO/PERMCO（恒久ID） | 200-399 M&A、≥400 倒産・清算、332/570/573 自発的廃止 | 部分的（M&A 相手は別 PERMNO 経由） | 非上場・破綻前 dormant 期間・brand legacy |
| **US Courts (BAPCPA)** | 連邦破産裁判所 | Chapter 7/11/13 申立 | 事件番号 | Chapter 種別と事業/個人区別 | 11条更生後の同一性は弱い | 申立に至らない silent shutdown |
| **東京商工リサーチ (TSR)** | 日本全国 | 法的倒産 + 私的倒産（銀行取引停止・内整理） | 企業コード | 4法 + 私的 | 後継・スポンサー記載あり（記事レベル） | 廃業（後継不在）の体系記録は別 |
| **帝国データバンク (TDB)** | 日本全国（COSMOS 140万社）| 法的倒産のみ（4法、負債1,000万円以上） | TDBコード | 4法 | 部分的 | 私的整理・小規模廃業 |
| **BLS Business Employment Dynamics** | 米全 establishment | establishment death（4四半期連続ゼロ雇用） | EIN | 死因なし（ただ消失） | なし | 死因・継承・ブランド・特許 |
| **Eurostat-OECD SDBS** | EU+OECD | enterprise death rate, 5年生存率 | NACE/ISIC | 死因なし | なし | 個別企業 ID への traceability |
| **ECB Statistical Data Warehouse** | ユーロ圏 | corporate insolvency (集計) | 集計のみ | M&A vs liquidation 程度 | なし | 個社ミクロ |
| **SEC EDGAR (Form 8-K, 15, 25)** | 米上場 | 重要事象（M&A 1.01/2.01）、Form 25 上場廃止、Form 15 reporting 終了 | CIK | 高解像度 | 8-K 内記述 | 非上場・国際比較困難 |
| **Mergerstat / Refinitiv (旧 Thomson) M&A** | グローバル M&A | deal-level | deal ID | M&A タイプ | acquirer/target ペア明示 | M&A 後の文化統合・実質生存 |
| **VOC・歴史的アーカイブ** | 個別企業 | dissolution decree, asset transfer | なし | 文書解釈 | 文書解釈 | 構造化なし |

**横断的ギャップ**:
- 法人格ベースの「死」は記録されるが、**autocatalytic loop の崩壊**（Padgett-Powell 的視点）は記録されない。
- **後継者・遺産（successor / legacy）リンク** が体系化されていない（CRSP M&A コードと SEC 8-K の組合せが最良だが断片的）。
- **死後生**（ブランド・特許・人材ネットワーク・コードベース・規範）の追跡なし — IPO 後の特許継承は USPTO assignee で部分的に追える。
- **眠り (dormancy)** と **再活性** の状態遷移を記述するデータモデル不在。

---

## ボトムアップ分析・データベース設計への含意

### Event スキーマ拡張案

Stream A/D で議論されたイベントスキーマに以下の **dissolution event** を追加する：

```yaml
event:
  id: evt_xxx
  org_id: org_xxx
  type: dissolution | suspension | merger_target | spinoff_parent | spinoff_child
              | acquisition | brand_handover | dormancy_enter | dormancy_exit
              | succession | regulatory_dissolution
  date: ISO8601 (or fuzzy)
  date_uncertainty: enum {exact, year, decade, century}

  dissolution_cause:                # 多次元タグ（複数選択可）
    primary: enum {
      bankruptcy_chapter7,          # 清算
      bankruptcy_chapter11,         # 再建（実質的には continuation）
      bankruptcy_chapter13,
      civil_rehabilitation_jp,      # 民事再生
      corporate_reorganization_jp,  # 会社更生
      special_liquidation_jp,       # 特別清算
      bank_transaction_halt_jp,     # 銀行取引停止
      voluntary_liquidation,
      m_and_a_absorbed,
      m_and_a_dissolved_into_buyer,
      regulatory_dissolution,       # 例: 財閥解体, GHQ 命令
      schism_split,                 # 分裂で本体消滅
      successor_absent,             # 後継者不在で廃業
      charter_expiration,           # 例: VOC
      criminal_prosecution,         # 例: Andersen, Enron
      war_revolution,
      natural_disaster,
      unknown
    }
    secondary_factors: [list of factor tags]
    altman_z_score_at_t-1: float?   # 構造化された早期警報
    age_at_death_years: int
    cohort_year: int                # imprinting / cohort 分析用

  successor:                        # 多重後継者を許容
    - successor_org_id: org_xxx
      relation: enum {
        legal_successor,            # 法的承継（更生後の同一法人）
        asset_recipient,            # 資産買収
        brand_licensee,             # 例: HMD-Nokia
        spinoff_continuation,
        ip_assignee,                # 特許承継
        personnel_diaspora,         # 人材分散先（複数）
        cultural_descendant,        # 例: Cluny → Cîteaux
        political_successor         # 例: keiretsu after zaibatsu
      }
      transfer_share: float         # 0..1 (推定)

  legacy:                           # 死後に残るもの
    patents: [USPTO assignee 移転 list]
    trademarks: [list]
    code_repositories: [list]       # OSS 化されたか
    physical_assets: [description]
    norms_and_practices: [free text + tags]
    network_alumni: [list of org_ids where ex-members migrated]
    archives: [URL/citation]

  evidence:
    sources: [list]
    confidence: enum {high, medium, low, conjecture}
```

### dormancy（眠り）の状態モデル

死亡を二項（alive/dead）ではなく以下の状態機械で表す：

```
ACTIVE → SUSPENDED (休眠会社, dormant) → REACTIVATED (復活)
                                        ↘ DISSOLVED (解散)
ACTIVE → DISSOLVED ↘
                    LEGACY-ONLY (法人消滅・遺産のみ生存) → REINCARNATED (例: HMD-Nokia)
                                                       ↘ EXTINCT (完全消滅)
```

これにより Jesuit 1773-1814、財閥→keiretsu、Nokia→HMD、シニセ廃業からの再興がすべて同一スキーマで扱える。

### 死因の階層構造

死因は単一カテゴリではなく多次元タグで持つ。Hannan-Freeman の age dependence、Brüderl の adolescence、Barron-West の senescence/obsolescence の各仮説検証を可能にする：
- `age_at_death_years` × `cohort_year` × `density_at_t-1` の三次元で生存分析（Cox / Kaplan-Meier）。
- `imprinting_factors` フィールドに創業時環境（規制レジーム、戦争・平時、技術世代）を保存。

### 既存データ源との接続レイヤ

CRSP PERMNO、SEC CIK、TDB コード、TSR 企業コード、登記法人番号（日本）、Companies House number（英国）、EIN（米）を `external_ids[]` 配列で持ち、後から既存死亡データを結合可能にする。各 ID には `retrieval_date` と `last_observed_status` を付与（CRSP 慣行に倣う）。

---

## 倫理

1. **関係者保護** — 倒産・解散には個人（経営者、従業員、債権者）の生活破壊が伴う。Lehman 25,000人解雇、Enron 4,000人即時失業＋15,000人の年金消失。生存中の関係者を identifiable にする粒度の公開は避け、**個社レベルでは publicly attested な事実のみ**を採用、private interview や leaked 文書は扱わない。

2. **現存組織への影響** — 「死亡予測」モデル（Altman Z-score 派生）を公開すると自己成就的予言になる可能性。本データベースは*事後分析*を目的とし、生存中組織の予測スコアは内部研究用途に限定する。

3. **遺族企業・家族企業のセンシティビティ** — シニセ廃業や家族企業承継失敗は当事者にとって *kakun の侮辱* となり得る。日本の文脈では「廃業」と「後継者不在」を区別し、後者を中立用語 `successor_absent` で記述。

4. **植民地・帝国主義の遺産** — VOC、東インド会社、戦前財閥は植民地搾取・戦争動員の主体でもあった。「組織の生命」というメタファーが暴力性を中和しないよう、`legacy` フィールドに *harm_inflicted* タグを設けて被害文脈を可視化する（codex3 の東アジア視点と統合）。

5. **再活性の濫用** — shell company / dormant company の悪用（pump-and-dump、reverse merger 詐欺）が SEC で問題化。dormancy → reactivation を理論的に追跡する一方、悪用パターンと正当な再興（伝統工芸、HMD-Nokia 型）を区別する分類学が必要。

---

## 未確認・要追跡

1. **TDB / TSR API・ライセンス** — 学術利用条件と粒度。COSMOS 140万社の個社レベル取得可能性。
2. **Mergerstat / Refinitiv M&A database** — 価格・アクセス。SDC Platinum の歴史的後継。
3. **Padgett-Powell autocatalytic 公式モデル** — 数理形式（彼らの appendix）が我々のグラフ DB スキーマに mappable か検証。
4. **Sørensen & Stuart (2000) Aging, Obsolescence and Innovation** — 元論文 ASQ 入手して obsolescence の operational definition を確認。
5. **Brüderl & Schüssler (1990) ASQ 35:530** — ハザードカーブ図を取得し adolescence ピークの数値再現。
6. **戦前財閥解体一次史料** — 持株会社整理委員会（HCLC）報告書、GHQ SCAPIN 文書（国会図書館）。
7. **Cluny-Cîteaux ネットワーク** — Padgett 系の歴史社会学者による定量再構成があるか。
8. **HMD Global ライセンス契約条項** — 2026 年延長後の終了条件、Nokia ブランド遺産の最終帰属。
9. **UK Companies House dormant company register** — dormant 状態の統計的分布。
10. **韓国・中国の倒産統計** — 韓国 KIS-VALUE、中国国家企業信用情報公示系統の構造。
11. **religious order の解散統計** — Vatican/AAS にデータがあるか。
12. **Enron 崩壊後の人材ディアスポラ** — Veld (Skilling) 等への follow-up 研究はあるか。
13. **liability of obsolescence の定量基準** — 環境ドリフトをどう測るか（特許引用ネットワーク？）
14. **コホート分析用の歴史的危機イヤー** — 1873, 1929, 1973, 2008, 2020 各コホートの個体数比較データセット。
15. **Bankruptcy archives 19世紀** — 英国 London Gazette、米連邦破産前史。

---

## 参考文献（主要）

- Stinchcombe, A. L. (1965) "Social Structure and Organizations," *Handbook of Organizations*.
- Hannan, M. T., & Freeman, J. (1984) "Structural Inertia and Organizational Change," *American Sociological Review* 49: 149-164.
- Hannan, M. T. (1998) "Rethinking Age Dependence in Organizational Mortality," *American Journal of Sociology* 104(1).
- Brüderl, J., & Schüssler, R. (1990) "Organizational Mortality: The Liabilities of Newness and Adolescence," *Administrative Science Quarterly* 35(3): 530-547.
- Barron, D. N., West, E., & Hannan, M. T. (1994) Credit unions analysis, *AJS*.
- Sørensen, J. B., & Stuart, T. E. (2000) "Aging, Obsolescence, and Organizational Innovation," *ASQ*.
- Hannan, M. T., & Carroll, G. R. (1992) *Dynamics of Organizational Populations*, Oxford UP.
- Carroll, G. R., & Hannan, M. T. (2000) *The Demography of Corporations and Industries*, Princeton UP.
- Cusatis, P., Miles, J., & Woolridge, J. R. (1993) "Restructuring through Spinoffs," *J. Financial Economics* 33: 293-311.
- Cartwright, S., & Cooper, C. L. (1996) *Managing Mergers, Acquisitions and Strategic Alliances*, 2nd ed., Routledge.
- Altman, E. I. (1968) Z-score original paper.
- Padgett, J. F., & Powell, W. W. (2012) *The Emergence of Organizations and Markets*, Princeton UP.
- Eurostat & OECD (2007) *Manual on Business Demography Statistics*.

データ源 URL:
- CRSP delisting codes: https://www.crsp.org/products/documentation/delisting-codes
- US Courts BAPCPA: https://www.uscourts.gov/data-news/reports/statistical-reports/bankruptcy-abuse-prevention-and-consumer-protection-act-report/
- BLS BDM: https://www.bls.gov/bdm/
- Eurostat-OECD SDBS: https://stats.oecd.org/index.aspx?queryid=70734
- TSR 全国倒産動向: https://www.tsr-net.co.jp/news/status/
- TDB 倒産情報: https://www.tdb.co.jp/report/bankruptcy/
- SEC Form 8-K: https://www.sec.gov/files/form8-k.pdf
