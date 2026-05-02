# Stream D: 既存データベース・データ源マッピング

調査日: 2026-05-02 / 担当: 事前リサーチ Stream D

---

## 概要

組織を「生命」として捉える系譜分析に活用しうる既存データベース・公開データセット・APIを 40 件以上洗い出し、カバー期間・地域・組織種別ごとに利用可能性を整理した。法人実体・スタートアップ・学術・特許・NPO・ESG はオープン／有料 API が比較的揃う一方、近代以前の組織、グローバル南、非公式組織、組織の「死」（解散・合併）データは構造的に欠ける。再利用と独自構築のハイブリッド戦略が現実的。

---

## データベース一覧

### 法人実体・基本情報

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| OpenCorporates | OpenCorporates Ltd | 全世界 230+ 法域、登記データに準拠 | 法人名・登記番号・住所・ステータス・役員・LEI mapping | API 無料枠あり / 商用は有料 | 強: 世界最大のオープン法人データ。弱: 各国登記の更新頻度に依存、歴史的データは断片的 | https://opencorporates.com/ |
| GLEIF (LEI) | Global Legal Entity Identifier Foundation | 2012〜現在、全世界 | LEI・法人名・住所・親子関係（Level 2） | 完全オープン (CC0) / API・bulk download | 強: グローバル一意 ID、Who-owns-whom 関係。弱: LEI 取得は主に金融取引主体のみ、中小企業はカバー外 | https://www.gleif.org/en/lei-data/gleif-api |
| gBizINFO | デジタル庁・経済産業省 | 日本、現役法人中心 | 法人番号・所在地・補助金・調達・特許・財務 | 完全オープン / REST API | 強: 日本国内官公庁データを法人番号で串刺し。弱: 廃業・歴史データ薄、海外法人なし。2026年1月に新システム移行 | https://info.gbiz.go.jp/ |
| 法人番号公表サイト | 国税庁 | 日本、2015〜 | 法人番号・名称・所在地・変更履歴 | 完全オープン / API・CSV | 強: 全日本法人を網羅。弱: 財務・活動データなし | https://www.houjin-bangou.nta.go.jp/ |
| Companies House | UK 政府 | UK、1844年法人化以降 | 会社番号・役員・財務・filing履歴 | 完全オープン / API | 強: 役員・PSC情報・歴史的 filing が無料公開。弱: UK 限定 | https://developer.company-information.service.gov.uk/ |
| SEC EDGAR | SEC (US) | US 上場・公募、1993〜 (一部 1934 以降の歴史的 filings) | filings (10-K/10-Q/8-K等)・XBRL 財務データ・役員・株主 | 完全オープン / data.sec.gov API、10 req/sec | 強: 米国上場の包括的開示。弱: 非上場・私企業はなし | https://www.sec.gov/search-filings/edgar-application-programming-interfaces |
| Orbis (Bureau van Dijk) | Moody's | 全世界 4億+法人 | 財務・所有関係・役員・標準化財務諸表 | 有料・大学ライセンス / bulk・API | 強: 非上場・グローバル網羅、UBO データ。弱: 高額、再配布不可 | https://www.bvdinfo.com/en-gb/our-products/data/international/orbis |
| OpenSanctions | OpenSanctions GmbH | 全世界、PEP・制裁・犯罪関連、240+ 国 | 法人・個人・関係、FollowTheMoney オントロジー | CC-NC（非商用無料） / 商用ライセンス | 強: 透明性の高い deduplication、API・bulk。弱: ハイリスク中心の偏り | https://www.opensanctions.org/ |

### 金融・財務

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| Compustat | S&P Global | 北米 1950〜、グローバル 1987〜 | 標準化財務諸表・セグメント・配当・買収 | WRDS 経由・大学ライセンス | 強: 学術標準、長期時系列。弱: 上場中心、有料 | https://www.spglobal.com/marketintelligence/en/solutions/sp-capital-iq-pro |
| CRSP | University of Chicago Booth | NYSE 1925〜、AMEX/Nasdaq | 株価・リターン・出来高・株式分割 | WRDS / 大学ライセンス | 強: 米国株のゴールドスタンダード歴史データ。弱: 米国限定 | https://www.crsp.org/ |
| S&P Capital IQ | S&P Global | グローバル 100,000+ 法人 | 財務・M&A・PE/VC・関係 | 有料（個別契約） | 強: 民間企業 M&A の深さ。弱: 高額 | https://www.spglobal.com/marketintelligence/ |
| EDINET | 金融庁 | 日本上場、2008〜 | 有価証券報告書・XBRL・大量保有 | 完全オープン / API v2 (2026 年 4 月版) | 強: XBRL 標準、構造化財務。弱: 上場中心、英語化薄 | https://disclosure2.edinet-fsa.go.jp/ |

### スタートアップ・新興

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| Crunchbase | Crunchbase Inc. | グローバル、1990s〜 | 創業者・調達・買収・チーム・PoC | 無料閲覧 / Pro $49–199/mo / API は別途エンタープライズ契約 | 強: コミュニティ編集で速報性高い。弱: 自己申告偏り、API は高額 | https://www.crunchbase.com/ |
| PitchBook | Morningstar | グローバル、PE/VC | 取引履歴・LP・バリュエーション・退出 | 有料 ~$12k+/年 | 強: PE/VC 取引の深さ。弱: 高額、API 制限 | https://pitchbook.com/ |
| CB Insights | CB Insights | グローバル、テック企業中心 | 投資・M&A・特許・ニュース AI抽出 | 有料 ~$60k+/年（Analytics 入門 $50k） | 強: 新興技術トレンド分析。弱: 非常に高額 | https://www.cbinsights.com/ |
| INITIAL (Speeda Startup Information Research) | Uzabase | 日本、16,000+ スタートアップ | 調達・株主・KPI・組織 | 法人有料、無料簡易版 | 強: 日本スタートアップ最深。弱: 日本限定、API 限定的 | https://initial.inc/ |
| SPEEDA | Uzabase | グローバル業界・企業 | 業界レポート・財務・関係 | 有料 | 強: 日本語ユーザー向け業界俯瞰。弱: 高額、再配布不可 | https://jp.ub-speeda.com/ |

### 歴史的組織・知識ベース

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| Wikidata | Wikimedia Foundation | 全世界・全時代 | inception/dissolution date・親子関係・活動領域・場所 (Q43229 organization と全 subclass) | CC0 / SPARQL endpoint, dump | 強: 古代〜現代を一元、構造化、自由再配布。弱: 網羅性ばらつき、出典品質まちまち | https://query.wikidata.org/ |
| DBpedia | DBpedia 協会 | 全世界 (Wikipedia 抽出) | infobox 由来の組織属性 | CC-BY-SA / SPARQL | 強: 多言語横断。弱: Wikipedia infobox 依存で精度ばらつき | https://www.dbpedia.org/ |
| Wikipedia カテゴリ (organizations by century 等) | WMF | 全世界・全時代 | 分類・記事本文 | CC-BY-SA | 強: ヒューリスティック発見に有用。弱: 構造化されていない | https://en.wikipedia.org/wiki/Category:Organizations |
| Internet Archive Wayback Machine | Internet Archive | Web 1996〜、1兆ページ超 | 組織サイトの歴史的スナップショット | 無料 / API・CDX | 強: 失われた組織・サイトの追跡。弱: クロール網羅性に偏り | https://web.archive.org/ |
| Project Gutenberg | PG | 古典テキスト全世界 | 歴史史料・組織記述（テキスト） | パブリックドメイン中心 | 強: 一次史料にアクセス。弱: 構造化なし、自然言語処理必要 | https://www.gutenberg.org/ |

### 学術・知識生産

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| OpenAlex | OurResearch | グローバル、研究機関 109,000+ | 機関・著者・論文・引用、ROR ID 紐付け 94% | CC0 / API・snapshot | 強: 完全オープンの MAG 後継、機関ネットワーク分析可能。弱: 1900s 以前の歴史薄 | https://openalex.org/ |
| ROR | Research Organization Registry | グローバル研究組織 | 組織名・国・関係・代替名 | CC0 / API・dump | 強: 学術組織のオープン正規化 ID。弱: 学術組織のみ | https://ror.org/ |
| Crossref | Crossref | 学術出版 1990s〜 | DOI・著者・所属・引用 | オープン API | 強: 学術メタデータの基礎レイヤー。弱: 機関情報は副次的 | https://www.crossref.org/ |
| Microsoft Academic Graph | Microsoft (廃止 2021) | 1800s〜2021 | 論文・著者・機関・ FoS | レガシーダンプのみ | 強: 大規模歴史データ。弱: 廃止・更新なし、OpenAlex に移行 | https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/ |

### 特許・技術活動

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| USPTO Open Data Portal | USPTO | 米国、1790〜 | 特許書誌・本文・出願人・引用 | 完全オープン / API・bulk | 強: 米国特許 230 年。弱: 米国限定、出願人の名寄せ要 | https://data.uspto.gov/ |
| PatentsView | USPTO 委託 | 米国、disambiguated | 名寄せ済み出願人・発明者・地理 | 無料 API | 強: 学術用途で名寄せ済み。弱: 米国限定 | https://patentsview.org/ |
| EPO PATSTAT | EPO | グローバル、書誌・citation・ family | 特許統計データベース | 有料・学術ライセンスあり | 強: グローバル一元。弱: 有料 | https://www.epo.org/searching-for-patents/business/patstat.html |
| Google Patents Public Datasets | Google + IFI Claims | グローバル | 全文・citation・family、BigQuery | 無料閲覧 / BigQuery 課金 | 強: 全文 BigQuery 解析可能。弱: API は廃止 | https://cloud.google.com/blog/topics/public-datasets/google-patents-public-datasets |
| The Lens | Cambia | 特許 136M+ / 学術 200M+ | 特許・論文を統合検索、出願人正規化 | 無料閲覧 / 一部有料 API | 強: 特許×学術の統合。弱: API 商用は有料 | https://www.lens.org/ |
| J-PlatPat | INPIT | 日本特許全期間 | 特許・実用新案・意匠・商標 | 無料閲覧 / API は限定 | 強: 日本特許の公式。弱: 大量機械処理は別契約 | https://www.j-platpat.inpit.go.jp/ |

### NPO・市民社会

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| Candid (旧 GuideStar + Foundation Center) | Candid | 米国 1.8M+ NPO、1999〜 | Form 990・mission・財務・grants | 一部無料 / API は有料 | 強: 米国 NPO 最大データ。弱: 有料 API、米国限定 | https://www.guidestar.org/ |
| Charity Commission for England and Wales | UK 政府 | UK、現役+一部歴史 | 登録番号・財務・受託者・活動 | 完全オープン / API・bulk daily | 強: 完全オープン。弱: UK 限定 | https://register-of-charities.charitycommission.gov.uk/ |
| 内閣府 NPO ホームページ | 内閣府 | 日本、1998〜 | 法人名・所轄庁・事業報告 | 完全オープン / CSV ダウンロード | 強: 日本 NPO 法人公式。弱: API 限定的、機械可読性低 | https://www.npo-homepage.go.jp/ |

### 政府・公的組織

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| GovInfo | GPO (US) | 米国連邦、1873〜 | 議会記録・連邦規則・公的組織記述 | 完全オープン / API | 強: 米国連邦の包括的歴史。弱: 構造化データは限定 | https://www.govinfo.gov/ |
| EU Open Data Portal (data.europa.eu) | EU 出版局 | EU、加盟国 1.7M+ データセット | 機関データセット・公的団体 | 完全オープン / SPARQL・API | 強: 加盟国横断統合。弱: 内容ばらつき | https://data.europa.eu/ |
| UN Data | UN | グローバル、加盟国 | 統計・組織関連 | オープン | 強: グローバル比較可能。弱: 国レベル、組織単位は薄 | https://data.un.org/ |

### ESG・インパクト

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| MSCI ESG Ratings | MSCI | グローバル上場中心 | ESG スコア・ESG リスク | 有料 | 強: 機関投資家標準。弱: 高額・上場中心 | https://www.msci.com/our-solutions/esg-investing |
| Sustainalytics | Morningstar | グローバル 16,000+ 法人 | ESG リスクレーティング・controversies | 有料 / API | 強: GRI 連携、標準化スコア。弱: 有料 | https://www.sustainalytics.com/esg-data |
| B Corps Directory | B Lab | グローバル、~9,000 認証 (2025) | B Impact 認証・スコア | 完全オープン閲覧 | 強: ミッション駆動企業の発見。弱: 自己選択バイアス | https://www.bcorporation.net/find-a-b-corp |
| GRI Standards / Reports Database | GRI | グローバル ESG レポート | sustainability reports 提出 | オープン閲覧 | 強: 国際標準。弱: レポート PDF 中心、構造化弱い | https://www.globalreporting.org/ |

### 歴史データセット

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| Maddison Project Database 2023 | Groningen Growth and Development Centre | 169 カ国、AD 1〜2022 | GDP per capita・人口、PPP 換算 | CC-BY / CSV ダウンロード | 強: 古代〜現代の経済規模、組織研究の文脈データ。弱: 国レベル、組織単位なし | https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023 |
| Seshat: Global History Databank | Evolution Institute | 新石器〜近代初期、グローバル | 政治・社会組織コード化・専門家コーディング | オープンアクセス（学術） | 強: 古代社会の政治・社会組織。弱: サンプリング選別、現代以降は弱 | https://seshatdatabank.info/ |
| Cliodynamics datasets (Turchin 等) | Peter Turchin 他 | 古代〜近代 | 帝国・人口・暴力・組織形態 | 学術公開 | 強: マクロ歴史の組織進化。弱: アグリゲーション、サンプル制限 | https://peterturchin.com/ |

### 人類学的データ

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| D-PLACE | Max Planck EVA + 共同 | グローバル、文化集団 1,400+ | 文化・言語・環境・社会組織コード | CC-BY / API・dump | 強: 文化的多様性のオープン統合。弱: 公式組織より文化集団中心 | https://d-place.org/ |
| eHRAF World Cultures | Yale HRAF | 300+ 文化、民族誌 | 民族誌全文・トピック・SCCS 紐付け | 機関ライセンス | 強: 全文民族誌、SCCS 統合。弱: 有料、民族誌中心 | https://hraf.yale.edu/ |
| Standard Cross-Cultural Sample (SCCS) | Murdock & White (1969) | 186 文化サンプル | 社会組織変数 2,000+ | オープン | 強: 通文化比較の標準。弱: 古典的、186 サンプルに限定 | https://en.wikipedia.org/wiki/Standard_Cross-Cultural_Sample |

### ネットワーク・関係・リーク

| 名称 | 提供元 | 対象期間・地域 | 主要フィールド | 利用条件 | 強み・弱み | URL |
|---|---|---|---|---|---|---|
| ICIJ Offshore Leaks | ICIJ | 1970s〜2020s 漏洩文書由来、800,000+ オフショア法人 | 法人・個人・住所・関係（4 ネットワーク統合） | 検索無料 / CSV+Neo4j ダウンロード | 強: タックスヘイブン関係性の世界唯一の網羅。弱: 漏洩偏り、アジア薄 | https://offshoreleaks.icij.org/ |
| Common Crawl | Common Crawl Foundation | Web スナップショット、月次 | 全 Web データ | 無料 / S3 | 強: 組織サイト網羅、NLP で抽出可能。弱: 構造化なし、要 ETL | https://commoncrawl.org/ |
| GLEIF Level 2 (Who Owns Whom) | GLEIF | LEI 保有法人 | 直接親・最終親関係 | CC0 | 強: グローバル所有関係、無料。弱: LEI 取得法人のみ | https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom |

---

## カバレッジ・マップ

### 時代 × 組織種別

| | 古代・中世 (〜1500) | 近世 (1500–1800) | 近代 (1800–1945) | 戦後 (1945–2000) | 現代 (2000–) |
|---|---|---|---|---|---|
| **営利法人** | Wikidata 断片、Seshat | Wikidata, Seshat, 史料 | EDGAR (1934-)、Companies House、Compustat (1950-) | Compustat, CRSP, Orbis | OpenCorporates, GLEIF, gBizINFO, EDINET, INITIAL |
| **NPO・宗教・市民組織** | Seshat, eHRAF, 史料 | Seshat, eHRAF | 部分 (国別資料) | Candid 米国 (1999-) | Candid, Charity Commission, 内閣府 NPO |
| **政府・公的** | Wikidata, Seshat | Wikidata, GovInfo (US 1873-) | GovInfo, 各国アーカイブ | UN Data, GovInfo | EU Open Data, UN Data, GovInfo |
| **学術・研究** | 断片 (Wikidata) | 断片 | 断片 | MAG（廃止）レガシー | OpenAlex, ROR, Crossref |
| **ギルド・協同組合** | 史料・Wikipedia のみ | 史料・Wikipedia のみ | 史料散在 | 国別協同組合連合資料 | 部分（B Corp 等） |
| **インフォーマル・運動** | ほぼなし | ほぼなし | ほぼなし | 断片 | 断片 (SNS等から要抽出) |

### 地域カバレッジ

| 地域 | 法人実体 | 財務 | スタートアップ | NPO | 学術 |
|---|---|---|---|---|---|
| 北米 | 厚 | 厚 | 厚 | 厚 (Candid) | 厚 |
| EU/UK | 厚 (Companies House等) | 中 | 中 | 中 (Charity Comm.) | 厚 |
| 日本 | 厚 (gBizINFO/法人番号) | 中 (EDINET) | 中 (INITIAL) | 中 (内閣府) | 中 (ROR) |
| 中国 | 限定（公開薄） | 限定 | 限定 | 限定 | 中 (OpenAlex) |
| グローバル南 | 薄〜中 (国による) | 薄 | 薄 | 薄 | 薄 |
| 中東・アフリカ | 薄 | 薄 | 薄 | 薄 | 薄 |

---

## 利用優先度 Top 10

1. **Wikidata** — 古代〜現代を統合し inception/dissolution・関係を CC0 で SPARQL 取得可、系譜分析の基盤レイヤー
2. **OpenCorporates + GLEIF (LEI Level 1+2)** — 現代法人実体とその所有関係を世界規模で取得する事実上唯一のオープン基盤
3. **OpenAlex + ROR** — 学術組織と知識生産ネットワークを完全オープンで取得、系譜の認識的側面を捉える
4. **gBizINFO + 法人番号公表サイト + EDINET** — 日本法人の最深ローカルデータ、研究者の地理的アンカーとして必須
5. **Seshat: Global History Databank** — 近代以前の組織形態を構造化、現存データで唯一の古代〜近代横断
6. **Maddison Project 2023** — 組織を取り巻くマクロ経済環境を AD 1〜現代でカバー、文脈レイヤー
7. **ICIJ Offshore Leaks** — 公式記録に現れない関係性ネットワークを補完、組織の「裏側の系譜」を可視化
8. **Internet Archive Wayback Machine** — 消えた組織・Web 上の歴史的痕跡、独自スクレイピングの貴重な過去復元手段
9. **Crunchbase** — 新興・スタートアップ層を低コストで継続把握、生まれたての組織を捉える
10. **D-PLACE + SCCS** — 通文化比較の社会組織変数、組織の「種類」概念を相対化する人類学的基盤

---

## ライセンス・倫理上の留意

- **CC0 / 完全オープン**: Wikidata, GLEIF, ROR, OpenAlex, Crossref, Maddison, Companies House, gBizINFO, EDINET, Charity Commission, USPTO, PatentsView, GovInfo, EU Open Data, UN Data — 商用利用・再配布可、引用は推奨
- **CC-BY / CC-BY-SA**: DBpedia, Wikipedia, D-PLACE, Maddison（バージョン依存） — 帰属表示要、SA は派生物にも継承
- **CC-NC（非商用のみ）**: OpenSanctions の bulk — 商用には別ライセンス必要
- **有料・再配布不可**: Compustat, CRSP, Orbis, S&P Capital IQ, PitchBook, CB Insights, MSCI, Sustainalytics, eHRAF, INITIAL/SPEEDA, PATSTAT — 大学ライセンス経由で論文掲載可だがデータセット公開は不可
- **API 別途エンタープライズ契約**: Crunchbase, Candid — 無料閲覧と API 利用条件が大きく異なる
- **倫理的留意**:
  - ICIJ Offshore Leaks は実在の個人・関係を含む。研究公表時は対象選別と文脈化が必要
  - 個人情報を含む役員・所有者データは GDPR・個人情報保護法に注意
  - 民族誌（eHRAF/D-PLACE/SCCS）は植民地文脈で収集されたものを含む。記述的引用のみで、Indigenous Data Sovereignty を尊重
  - 組織の「死」（破綻・解散）データは関係者にとってセンシティブ、現存組織の不利益にならない配慮

---

## 既存データで埋まらないギャップ（独自収集の必要領域）

1. **近代以前のフォーマル組織の体系的記録** — Seshat 以外に古代〜中世のギルド・修道院・商社を網羅したデータベースは存在しない。歴史史料からの構築が必要
2. **組織の「死」（解散・破綻・自然消滅）の体系的記録** — 法人登記の閉鎖は記録されるが、その「原因」「後継組織」「文化的継承」は捉えられていない
3. **インフォーマル組織・運動・ネットワーク** — オンライン運動、コミュニティ、ボランティア集団など法人化されない組織の系譜
4. **組織の「文化」「言語」「価値観」の時系列** — 内部文化・言語・自己認識の変遷をコード化したデータは皆無、独自エスノグラフィー必要
5. **組織間の「思想的影響」「人材の系譜」** — どの組織から誰が出てどの組織を作ったかの追跡（VC 系譜の一部は Crunchbase で見えるが体系的でない）
6. **グローバル南の組織データ** — アフリカ・中東・南アジア・ラテンアメリカは公的・商用ともに極めて薄い
7. **協同組合・相互扶助組織の継続的データ** — 国別連合資料はあるが横断データなし
8. **「組織のメタボリズム」指標** — 構成員の入れ替わり、リソース流入出、外界とのインタラクションは標準化されていない
9. **組織創業意図・神話・物語** — 創業ストーリーを構造化したデータは存在せず、IR 資料・自伝・インタビューから抽出が必要

---

## 未確認・要追跡

- **gBizINFO 2026 年 1 月新システム移行** の API 仕様変更点 — 仕様書の最終版を要確認
- **EDINET API v2 (2026 年 4 月版)** — 最新仕様と歴史データ取得範囲の検証
- **GRID** — ROR への移管が進行中、最新ステータス未確認
- **GuideStar/Candid API の最新料金体系** — 公開されておらず個別問い合わせ要
- **PATSTAT の学術ライセンス費用** — EPO 経由、機関契約条件未確認
- **eHRAF の機関ライセンス** — 大学契約有無で利用可否が決まる
- **The Lens の API 商用条件** — Cambia 個別交渉
- **Common Crawl からの組織サイト抽出パイプライン** — 既存 OSS の有無
- **Seshat の最新リリース・データ更新頻度** — 2026 年時点の更新状況
- **中国の法人データオープン度** — 国家信用信息公示系統の API・スクレイプ可能性は要調査
- **韓国 DART (KIND)** — EDINET 相当、未調査
- **インドの MCA データ** — Ministry of Corporate Affairs の API 状況未確認
- **WIPO INSPIRE** — IP 特許統計のオープン度・カバレッジ詳細
- **OpenSanctions 商用ライセンス費用帯** — 公開されているが研究機関向け条件は要確認
