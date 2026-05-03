#!/usr/bin/env python3
"""Phase 4 並列チーム G: デジタル時代 + 現存伝統 5 ケース temporal_facet 投入

対象 (organization_id 既存 verified 2026-05-03):
  - Anonymous              5fdc02de4aa9499ebfb5f65a79afac5a (2003-)
  - Wikimedia Foundation   86f92a01da2f444fb4b1f90563e1fff5 (2003-06-20-)
  - Linux Foundation       50552951e7194d2b87d5dcb604f4d7ca (2007-02-21-)
  - Hadza バンド            dba1923c55fe480795e0b646ba72df5e (現存狩猟採集)
  - Haudenosaunee Confed.  ad27b958944a4e11a5e9751533c3c07d (~1142?-)

設計原則:
  - 捏造禁止
  - confidence: Anonymous/WMF/Linux 0.7-0.85, Hadza/Iroquois 0.5-0.7
  - source: Coleman 2014 / WMF annual reports + Tkacz 2015 / Linux Foundation
    公式 reports / Marlowe 2010 / Mann 2000 + Wallace 1969 + Haudenosaunee
    Confederacy 公式 statements
  - 各 source に redistribution 必須
  - ENUM 厳格 (value_kind は 5 値: present/absent/partial/unknown/inapplicable)
  - Hadza/Iroquois facet には IDSov (Indigenous Data Sovereignty) 配慮を
    interpretation_note で明示
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "anonymous":   "5fdc02de4aa9499ebfb5f65a79afac5a",
    "wmf":         "86f92a01da2f444fb4b1f90563e1fff5",
    "linux":       "50552951e7194d2b87d5dcb604f4d7ca",
    "hadza":       "dba1923c55fe480795e0b646ba72df5e",
    "iroquois":    "ad27b958944a4e11a5e9751533c3c07d",
}


def uid():
    return uuid.uuid4().hex


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # ---- verify orgs exist ----
    for key, oid in ORG.items():
        row = cur.execute(
            "SELECT canonical_name FROM organization WHERE organization_id=?",
            (oid,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"organization not found: {key}={oid}")

    # ---- helpers ----
    def add_source(stype, title, **kw):
        sid = uid()
        cur.execute(
            "INSERT INTO source (source_id, source_type, title, authors, "
            "publication_date, publisher, locator, accessed_at, "
            "reliability_score, reliability_basis, bias_notes, license, "
            "redistribution) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                sid, stype, title,
                json.dumps(kw.get("authors")) if kw.get("authors") else None,
                kw.get("publication_date"), kw.get("publisher"),
                json.dumps(kw.get("locator")) if kw.get("locator") else None,
                kw.get("accessed_at"),
                kw.get("reliability_score"), kw.get("reliability_basis"),
                kw.get("bias_notes"),
                kw.get("license"),
                kw.get("redistribution", "attribution_required"),
            ),
        )
        return sid

    def add_claim(entity_type, entity_id, field_path, value_kind, value,
                  source_id, confidence, note=None,
                  recorded_by="claude_phase4_team_g_digital_extant"):
        cid = uid()
        cur.execute(
            "INSERT INTO claim (claim_id, entity_type, entity_id, field_path, "
            "value_kind, claim_value, source_id, confidence, recorded_by, "
            "interpretation_note) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                cid, entity_type, entity_id, field_path, value_kind,
                json.dumps(value, ensure_ascii=False) if value is not None else None,
                source_id, confidence, recorded_by, note,
            ),
        )
        return cid

    def add_facet(org_id, facet_type, facet_value, *,
                  valid_from=None, valid_from_precision=None,
                  valid_to=None, valid_to_precision=None,
                  confidence=None, source_id=None, note=None):
        facet_id = uid()
        claim_id = add_claim(
            "organization_temporal_facet", facet_id, "facet_value",
            "present", facet_value, source_id,
            confidence if confidence is not None else 0.6, note=note,
        )
        cur.execute(
            "INSERT INTO organization_temporal_facet "
            "(organization_facet_id, organization_id, valid_from, "
            "valid_from_precision, valid_to, valid_to_precision, "
            "facet_type, facet_value, confidence, claim_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                facet_id, org_id,
                valid_from, valid_from_precision,
                valid_to, valid_to_precision,
                facet_type,
                json.dumps(facet_value, ensure_ascii=False),
                confidence, claim_id,
            ),
        )
        return facet_id

    # =========================================================================
    # SOURCES
    # =========================================================================
    # ---- Anonymous ----
    src_coleman = add_source(
        "secondary_literature",
        "Coleman, G. (2014) Hacker, Hoaxer, Whistleblower, Spy: "
        "The Many Faces of Anonymous",
        authors=["Gabriella Coleman"],
        publication_date="2014",
        publisher="Verso Books",
        reliability_score=0.9,
        reliability_basis="Anonymous の人類学的民族誌の標準書。4chan 起源 (2003-)、"
                          "Project Chanology (2008)、Arab Spring 期 (2011)、"
                          "LulzSec 派生 (2011) を一次フィールドワークで記録。",
        bias_notes="参与観察者として一定の共感的立場、批判的視点は控えめ。",
        redistribution="attribution_required",
    )
    src_anon_wiki = add_source(
        "web",
        "Wikipedia: Anonymous (hacker group) - history and operations",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Anonymous_(hacker_group)"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="百科事典の整理。4chan /b/ 起源 2003 年、"
                          "Project Chanology 2008-01、Arab Spring 期 2011、"
                          "LulzSec 派生 2011-05 などの基本事実は確立。",
        redistribution="public_redistributable",
    )

    # ---- Wikimedia Foundation ----
    src_wmf_annual = add_source(
        "primary_text",
        "Wikimedia Foundation Annual Reports (2004-2024) and IRS Form 990 filings",
        authors=["Wikimedia Foundation"],
        publisher="Wikimedia Foundation",
        locator={"url": "https://wikimediafoundation.org/about/annual-report/"},
        accessed_at="2026-05-03",
        reliability_score=0.85,
        reliability_basis="WMF 公式年次報告書および IRS 990 提出書類。"
                          "2003-06-20 設立、ED 交代 (Gardner 2007-14, "
                          "Maher 2014-21, Iyer 2021-) は公式記録。",
        bias_notes="財団自己記述、批判的論点は限定的。",
        license="CC BY-SA 4.0",
        redistribution="public_redistributable",
    )
    src_tkacz = add_source(
        "secondary_literature",
        "Tkacz, N. (2015) Wikipedia and the Politics of Openness",
        authors=["Nathaniel Tkacz"],
        publication_date="2015",
        publisher="University of Chicago Press",
        reliability_score=0.85,
        reliability_basis="Wikipedia/WMF の制度化過程を批判的に分析した代表的研究。"
                          "Gardner 期のプロ化、コミュニティと財団の緊張を扱う。",
        bias_notes="批判理論的立場、財団側の自己理解とは距離あり。",
        redistribution="attribution_required",
    )
    src_wmf_strategy = add_source(
        "web",
        "Wikimedia 2030 Strategic Direction: Knowledge Equity and Knowledge as a Service",
        publisher="Wikimedia Foundation",
        locator={"url": "https://meta.wikimedia.org/wiki/Strategy/Wikimedia_movement/2017/Direction"},
        accessed_at="2026-05-03",
        reliability_score=0.8,
        reliability_basis="WMF 2017 戦略策定文書。Knowledge Equity を中核に据える"
                          "戦略転換を明示。Iyer 期の方向性に継承。",
        license="CC BY-SA 4.0",
        redistribution="public_redistributable",
    )

    # ---- Linux Foundation ----
    src_lf_official = add_source(
        "web",
        "Linux Foundation: About / Annual Reports / Project portfolio",
        publisher="Linux Foundation",
        locator={"url": "https://www.linuxfoundation.org/about"},
        accessed_at="2026-05-03",
        reliability_score=0.8,
        reliability_basis="Linux Foundation 公式情報。2007-02-21 OSDL + FSG 合併設立、"
                          "プロジェクト数・予算・メンバー企業数の年次推移を公開。",
        bias_notes="財団自己記述、内部ガバナンス論点は外部資料で補完が必要。",
        redistribution="attribution_required",
    )
    src_cncf = add_source(
        "web",
        "CNCF (Cloud Native Computing Foundation) - Annual Reports and Charter",
        publisher="Cloud Native Computing Foundation / Linux Foundation",
        locator={"url": "https://www.cncf.io/reports/"},
        accessed_at="2026-05-03",
        reliability_score=0.8,
        reliability_basis="CNCF 公式年次報告書。2015-12 Linux Foundation 傘下で設立、"
                          "Kubernetes graduation (2018-03) などのマイルストーン記録。",
        license="CC BY 4.0",
        redistribution="public_redistributable",
    )

    # ---- Hadza ----
    src_marlowe = add_source(
        "ethnography",
        "Marlowe, F.W. (2010) The Hadza: Hunter-Gatherers of Tanzania",
        authors=["Frank W. Marlowe"],
        publication_date="2010",
        publisher="University of California Press",
        reliability_score=0.9,
        reliability_basis="Hadza 研究の標準民族誌。長期フィールドワークに基づく"
                          "人口・移動パターン・平等主義的社会構造の記録。"
                          "Yaeda Valley 等の地理情報、20c 国家干渉史も整理。",
        bias_notes="人類学的記述、Hadza コミュニティ内部視点は当事者発言で補完が必要。"
                          "IDSov (Indigenous Data Sovereignty) の観点では学術記述の"
                          "一定限界がある。",
        redistribution="attribution_required",
    )
    src_hadza_land = add_source(
        "web",
        "Carbon Tanzania / UCRT: Hadza Yaeda Valley land tenure (2011)",
        publisher="Ujamaa Community Resource Team / Carbon Tanzania",
        locator={"url": "https://www.ujamaa-crt.or.tz/"},
        accessed_at="2026-05-03",
        reliability_score=0.7,
        reliability_basis="Hadza 土地保有権 (Yaeda Valley CCRO 2011) を仲介した"
                          "現地 NGO 公式情報。土地保有権付与の事実は確立。",
        bias_notes="コンサベーション NGO 視点、Hadza 当事者発言の一部のみ媒介。",
        redistribution="attribution_required",
    )

    # ---- Iroquois (Haudenosaunee) ----
    src_mann = add_source(
        "secondary_literature",
        "Mann, B.A. (2000) Iroquoian Women: The Gantowisas",
        authors=["Barbara Alice Mann"],
        publication_date="2000",
        publisher="Peter Lang",
        reliability_score=0.8,
        reliability_basis="Haudenosaunee 起源と Great Law of Peace の年代に関する"
                          "重要研究 (Mann & Fields 1997 の天文学的考察に基づく "
                          "1142 説を支持)。Seneca 系研究者による内部視点を含む。",
        bias_notes="1142 説は学界で議論あり、対立説 (~1450) も存在。"
                          "Haudenosaunee 内部視点を尊重する立場。",
        redistribution="attribution_required",
    )
    src_wallace = add_source(
        "secondary_literature",
        "Wallace, A.F.C. (1969) The Death and Rebirth of the Seneca",
        authors=["Anthony F.C. Wallace"],
        publication_date="1969",
        publisher="Knopf",
        reliability_score=0.85,
        reliability_basis="Iroquois (特に Seneca) 研究の古典。Handsome Lake の "
                          "Code of Handsome Lake (1799-) を含む 18-19c 変容の"
                          "標準的記述。",
        bias_notes="非先住民研究者による記述、現代の IDSov 基準では一定の留意要。",
        redistribution="attribution_required",
    )
    src_hcn_official = add_source(
        "web",
        "Haudenosaunee Confederacy official website: history, governance, Wampum",
        publisher="Haudenosaunee Confederacy / Onondaga Nation",
        locator={"url": "https://www.haudenosauneeconfederacy.com/"},
        accessed_at="2026-05-03",
        reliability_score=0.85,
        reliability_basis="Haudenosaunee Confederacy 公式自己記述。Great Law of Peace、"
                          "5/6 nations 構成、Tuscarora 加盟 1722、現代ガバナンス、"
                          "Doctrine of Discovery 反対声明など当事者公式情報。",
        bias_notes="Confederacy 公式立場、内部の異論や Six Nations Council vs. "
                          "Onondaga Council Fire 等の組織内多様性は他資料で補完。",
        redistribution="attribution_required",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # ---------- Anonymous --------------------------------------------------
    f = add_facet(
        ORG["anonymous"], "identity",
        {
            "phase": "4chan_origin",
            "dominant_identity": "4chan /b/ 板の匿名 trolling 集団 (proto-collective)",
            "brand_or_name": "Anonymous (4chan default username)",
            "notes": "2003 4chan 開設、デフォルトユーザー名 'Anonymous' から発生した"
                     "raid 文化。当初は組織化されない loose collective。",
        },
        valid_from="2003-10-01", valid_from_precision="year",
        valid_to="2007-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_coleman,
    )
    facets_inserted.append(("anonymous", "identity", "4chan_origin", f))

    f = add_facet(
        ORG["anonymous"], "identity",
        {
            "phase": "project_chanology",
            "dominant_identity": "オフライン抗議に踏み出した hacktivist 集団",
            "brand_or_name": "Anonymous (V for Vendetta マスクの象徴化)",
            "notes": "2008-01 Project Chanology (Scientology 反対) で "
                     "リアル抗議に展開、Guy Fawkes mask が global symbol 化。"
                     "Coleman (2014) は本期を 'public turn' と整理。",
        },
        valid_from="2008-01-15", valid_from_precision="exact",
        valid_to="2010-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_coleman,
    )
    facets_inserted.append(("anonymous", "identity", "project_chanology", f))

    f = add_facet(
        ORG["anonymous"], "membership",
        {
            "phase": "arab_spring_wikileaks_support",
            "basis": "ad-hoc operations cells (#OpTunisia, #OpEgypt, #OpPayback)",
            "eligibility": "IRC channel・Twitter ハッシュタグ参加で随時加入",
            "notes": "2010-12 #OpPayback (WikiLeaks 支援、PayPal/Visa DDoS)、"
                     "2011 #OpTunisia/#OpEgypt 等で Arab Spring に参与。"
                     "国際的政治アクターとしての認知が確立。",
        },
        valid_from="2010-12-01", valid_from_precision="exact",
        valid_to="2012-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_coleman,
    )
    facets_inserted.append(("anonymous", "membership", "arab_spring", f))

    f = add_facet(
        ORG["anonymous"], "governance",
        {
            "phase": "lulzsec_offshoot",
            "regime": "Anonymous 内部から派生した小規模専門グループ",
            "decision_locus": "LulzSec / AntiSec の 6-7 名コアチーム (Sabu et al.)",
            "notes": "2011-05 LulzSec 結成 (50 days)、Sony・FBI 関連サイト攻撃。"
                     "2011-06 解散、Sabu (Hector Monsegur) 2011-06 FBI 協力。"
                     "Anonymous の 'collective' から 'cell' への分化を示す。",
        },
        valid_from="2011-05-07", valid_from_precision="exact",
        valid_to="2012-03-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_anon_wiki,
        note="LulzSec は Anonymous 派生だが独立 brand。本 facet は Anonymous "
             "内部の組織分化として記録。",
    )
    facets_inserted.append(("anonymous", "governance", "lulzsec", f))

    f = add_facet(
        ORG["anonymous"], "identity",
        {
            "phase": "diffuse_post_2013",
            "dominant_identity": "拡散・分散化、複数の地域 cell と single-issue "
                                  "ops が並走する loose brand",
            "brand_or_name": "Anonymous (brand-as-mask, no central authority)",
            "notes": "2013 以降、Snowden 事件後の中心的 ops は減少。"
                     "Ferguson (2014)、#OpKKK (2015)、#OpRussia (2022 ウクライナ侵攻後) "
                     "等の散発的 ops。Brand としての継続。",
        },
        valid_from="2013-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.7, source_id=src_anon_wiki,
        note="Brand 継続性と組織実体の希薄化が並走。確定的 'end' を識別困難。",
    )
    facets_inserted.append(("anonymous", "identity", "diffuse", f))

    # ---------- Wikimedia Foundation ----------------------------------------
    f = add_facet(
        ORG["wmf"], "governance",
        {
            "phase": "founding_wales",
            "regime": "Founder-led 501(c)(3) NPO",
            "decision_locus": "Jimmy Wales 創設、初期 board は Wales 主導",
            "notes": "2003-06-20 Wales が Florida 州で WMF 設立、Wikipedia "
                     "の運営母体に。初期 board は Wales + Bomis 関係者中心。",
        },
        valid_from="2003-06-20", valid_from_precision="exact",
        valid_to="2007-06-30",   valid_to_precision="year",
        confidence=0.85, source_id=src_wmf_annual,
    )
    facets_inserted.append(("wmf", "governance", "founding_wales", f))

    f = add_facet(
        ORG["wmf"], "governance",
        {
            "phase": "gardner_professionalization",
            "regime": "ED-led professionalization (Sue Gardner 2007-14)",
            "decision_locus": "Executive Director (Gardner) 主導、board は監督役、"
                              "コミュニティ選出 board seat 制度導入",
            "key_bodies": ["Board of Trustees", "Executive Director",
                            "community-selected seats"],
            "notes": "2007-12 Sue Gardner ED 就任、職員数を数名から 200+ に拡大、"
                     "サンフランシスコ移転、財務基盤整備、5 年戦略策定。"
                     "Tkacz (2015) は本期を 'institutionalization' と分析。",
        },
        valid_from="2007-07-01", valid_from_precision="year",
        valid_to="2014-05-31",   valid_to_precision="exact",
        confidence=0.85, source_id=src_tkacz,
    )
    facets_inserted.append(("wmf", "governance", "gardner_period", f))

    f = add_facet(
        ORG["wmf"], "governance",
        {
            "phase": "maher_period",
            "regime": "ED 体制継続、グローバル展開重視",
            "decision_locus": "Katherine Maher ED (2014-06 acting, 2016-06 confirmed - 2021-04)",
            "notes": "2014-06 Maher acting ED、2016-06 正式 ED。グローバル South "
                     "重視、2030 戦略策定 (Knowledge Equity)、"
                     "API/wikidata 拡張、コロナ期の運営。",
        },
        valid_from="2014-06-01", valid_from_precision="exact",
        valid_to="2021-04-15",   valid_to_precision="exact",
        confidence=0.85, source_id=src_wmf_annual,
    )
    facets_inserted.append(("wmf", "governance", "maher_period", f))

    f = add_facet(
        ORG["wmf"], "governance",
        {
            "phase": "iyer_period",
            "regime": "CEO 体制 (title 変更)、Knowledge Equity 戦略実装期",
            "decision_locus": "Maryana Iyer (Maryana Iskander が正式名) CEO 2022-01-",
            "notes": "2021-09 announcement、2022-01 Iskander CEO 就任。"
                     "ED から CEO への呼称変更、Knowledge Equity 戦略の本格実装、"
                     "AI 時代への対応 (LLM 学習データ問題、API 商用化議論)。",
        },
        valid_from="2022-01-04", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_wmf_annual,
        note="Iyer は通称、正式名は Maryana Iskander。Iskander 期と表記される"
             "資料も多い。",
    )
    facets_inserted.append(("wmf", "governance", "iyer_period", f))

    f = add_facet(
        ORG["wmf"], "legitimation_basis",
        {
            "phase": "knowledge_equity_strategy",
            "basis": "Knowledge Equity (知識公平性) と Knowledge as a Service "
                     "を中核に据える 2030 戦略",
            "notes": "2017 策定の Wikimedia 2030 Strategic Direction で "
                     "'sum of all knowledge' から 'essential infrastructure of "
                     "knowledge' へ正統化基盤を再定義。グローバル South 包摂が中心。",
        },
        valid_from="2017-04-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_wmf_strategy,
    )
    facets_inserted.append(("wmf", "legitimation_basis", "knowledge_equity", f))

    f = add_facet(
        ORG["wmf"], "scale",
        {
            "phase": "growth_trajectory",
            "metric": "staff and revenue",
            "value_range": "staff: 2007 ~10 → 2014 ~200 → 2024 ~700; "
                           "revenue: FY2007 ~$2M → FY2014 ~$50M → FY2024 ~$180M",
            "notes": "WMF Annual Reports / Form 990 集計。職員数・収入とも"
                     "Gardner 期 (2007-14) に急拡大、その後も継続成長。",
        },
        valid_from="2003-06-20", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_wmf_annual,
    )
    facets_inserted.append(("wmf", "scale", "growth", f))

    # ---------- Linux Foundation --------------------------------------------
    f = add_facet(
        ORG["linux"], "governance",
        {
            "phase": "merger_founding",
            "regime": "OSDL + FSG 合併による新規 501(c)(6) 業界団体",
            "decision_locus": "Board of Directors (主要企業代表)、Executive Director "
                              "(Jim Zemlin 2007-)",
            "key_bodies": ["Board of Directors", "Technical Advisory Board",
                            "Executive Director"],
            "notes": "2007-02-21 Open Source Development Labs (OSDL) + Free "
                     "Standards Group (FSG) 合併で Linux Foundation 設立。"
                     "Jim Zemlin が ED 就任、Linus Torvalds をフェローとして雇用。",
        },
        valid_from="2007-02-21", valid_from_precision="exact",
        valid_to="2014-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_lf_official,
    )
    facets_inserted.append(("linux", "governance", "merger_founding", f))

    f = add_facet(
        ORG["linux"], "identity",
        {
            "phase": "linux_kernel_steward",
            "dominant_identity": "Linux カーネル開発の制度的後援団体",
            "brand_or_name": "Linux Foundation",
            "notes": "設立当初は Linux カーネル開発支援が中心アイデンティティ。"
                     "Linus Torvalds の雇用主、kernel.org 運営、"
                     "Linux Plumbers Conference 主催。",
        },
        valid_from="2007-02-21", valid_from_precision="exact",
        valid_to="2014-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_lf_official,
    )
    facets_inserted.append(("linux", "identity", "kernel_steward", f))

    f = add_facet(
        ORG["linux"], "governance",
        {
            "phase": "umbrella_foundation",
            "regime": "Multi-project umbrella foundation (umbrella org model)",
            "decision_locus": "各 sub-project (CNCF, Hyperledger, LF AI 等) は"
                              "独立 governing board を持ち、LF は財務・法務・"
                              "marketing をサポート",
            "key_bodies": ["LF Board", "CNCF TOC", "Hyperledger TSC",
                            "OpenJS, LF AI & Data, ...各プロジェクト governance"],
            "notes": "2015-12 CNCF (Cloud Native Computing Foundation) 設立を契機に"
                     "umbrella foundation モデルへ移行。2016 Hyperledger、"
                     "2018 LF Deep Learning (現 LF AI & Data)、2019 OpenJS 等。"
                     "現代では数十プロジェクトを統括。",
        },
        valid_from="2015-12-11", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_cncf,
    )
    facets_inserted.append(("linux", "governance", "umbrella", f))

    f = add_facet(
        ORG["linux"], "identity",
        {
            "phase": "umbrella_identity",
            "dominant_identity": "オープンソース基盤全般の institutional host "
                                  "(Linux + Cloud Native + Web 標準 + AI/Data)",
            "brand_or_name": "Linux Foundation (傘下に LF Projects)",
            "notes": "Kubernetes (CNCF), Hyperledger Fabric, Node.js, "
                     "PyTorch (2022 移管), OpenSSF など。'Linux' という名前は"
                     "歴史的 brand となり、実態は OSS インフラ全般。",
        },
        valid_from="2015-12-11", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_lf_official,
    )
    facets_inserted.append(("linux", "identity", "umbrella_identity", f))

    f = add_facet(
        ORG["linux"], "scale",
        {
            "phase": "growth_to_umbrella",
            "metric": "member companies and projects",
            "value_range": "members: 2007 ~70 → 2015 ~200 → 2024 ~1000+; "
                           "hosted projects: 2007 1 → 2024 ~900+ (含 sub-projects)",
            "notes": "Linux Foundation 公式 reports。CNCF 単独で hosted projects "
                     "200+ (2024)。財団全体予算は数億 USD レベル。",
        },
        valid_from="2007-02-21", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_lf_official,
    )
    facets_inserted.append(("linux", "scale", "growth", f))

    f = add_facet(
        ORG["linux"], "resource_base",
        {
            "phase": "corporate_membership_funded",
            "primary": "corporate membership fees (Platinum/Gold/Silver tiers)",
            "secondary": ["event revenue (KubeCon 等)", "training & certification",
                           "project-specific contributions"],
            "notes": "501(c)(6) 業界団体として企業会費が主収益。"
                     "Platinum members は Microsoft, Google, IBM, Intel, "
                     "Huawei, Meta 等。KubeCon は単独で大規模イベント収益。",
        },
        valid_from="2007-02-21", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_lf_official,
    )
    facets_inserted.append(("linux", "resource_base", "corporate_membership", f))

    # ---------- Hadza ------------------------------------------------------
    # IDSov 配慮: 個人や band 単位の詳細情報は避け、集合的・公知レベルに留める
    f = add_facet(
        ORG["hadza"], "membership",
        {
            "phase": "long_continuous_band",
            "basis": "Kinship + residential band (流動的・open membership)",
            "eligibility": "親族関係 + band への参加意思 (出入り自由)",
            "notes": "Hadza band は 20-30 名規模の流動的単位、固定的成員性は希薄。"
                     "Marlowe (2010) はメンバーシップの fluidity を中核特徴と整理。"
                     "数千年規模の hunter-gatherer 継続性が考古学・遺伝学から"
                     "示唆されるが、現代 'Hadzabe' という集合的 identity の"
                     "境界自体が連続的に再構成される。",
        },
        valid_from=None, valid_from_precision=None,
        valid_to=None,   valid_to_precision=None,
        confidence=0.6, source_id=src_marlowe,
        note="IDSov: Hadza コミュニティの自己定義を最優先。学術的記述は"
             "外部視点の限界を含む。具体的 band/個人情報は公知レベルに限定。",
    )
    facets_inserted.append(("hadza", "membership", "fluid_band", f))

    f = add_facet(
        ORG["hadza"], "governance",
        {
            "phase": "egalitarian_consensus",
            "regime": "Egalitarian, no formal leadership (acephalous)",
            "decision_locus": "成人男女の合議、特定の chief や council なし、"
                              "個人の autonomy 尊重",
            "notes": "Marlowe (2010) は Hadza を 'immediate-return egalitarian "
                     "society' の典型と分析。指導者の不在、富の蓄積拒否、"
                     "'demand sharing' 規範が中核。",
        },
        valid_from=None, valid_from_precision=None,
        valid_to=None,   valid_to_precision=None,
        confidence=0.65, source_id=src_marlowe,
        note="IDSov: 'egalitarian' は人類学的カテゴリ、Hadza 当事者の"
             "自己理解と一致するとは限らない。",
    )
    facets_inserted.append(("hadza", "governance", "egalitarian", f))

    f = add_facet(
        ORG["hadza"], "territory",
        {
            "phase": "state_settlement_attempts",
            "extent_label": "Tanzania 政府による定住化試行 (Yaeda Chini 等)",
            "key_regions": ["Yaeda Valley", "Mangola", "Lake Eyasi area"],
            "notes": "1960s-70s Tanzania 政府が複数の定住化プロジェクトを実施 "
                     "(教育・医療提供を伴う)。多くは Hadza 側の離脱で失敗、"
                     "森林・bush への帰還パターン。Marlowe (2010) 第 2 章に整理。",
        },
        valid_from="1964-01-01", valid_from_precision="decade",
        valid_to="1990-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_marlowe,
        note="IDSov: 国家干渉の記録は外部視点中心。Hadza 側の経験的記述は"
             "限定的な代表性に留まる。",
    )
    facets_inserted.append(("hadza", "territory", "state_settlement", f))

    f = add_facet(
        ORG["hadza"], "resource_base",
        {
            "phase": "tourism_intrusion",
            "primary": "hunter-gathering (継続的中核)",
            "secondary": ["cultural tourism (1990s-)",
                           "occasional wage labor",
                           "NGO 支援 (土地・教育)"],
            "notes": "1990s 以降 cultural tourism が拡大、一部 band で"
                     "観光収入が補助的役割。Marlowe (2010) は影響を限定的と"
                     "評価しつつ、長期的影響に懸念表明。",
        },
        valid_from="1990-01-01", valid_from_precision="decade",
        valid_to=None,           valid_to_precision=None,
        confidence=0.6, source_id=src_marlowe,
        note="IDSov: 観光化の影響評価は band 間で大きく異なる。"
             "コミュニティ自己評価を優先すべき領域。",
    )
    facets_inserted.append(("hadza", "resource_base", "tourism", f))

    f = add_facet(
        ORG["hadza"], "territory",
        {
            "phase": "yaeda_valley_land_tenure",
            "extent_label": "Yaeda Valley CCRO (Customary Certificate of Right of "
                             "Occupancy) による法的土地保有権",
            "key_regions": ["Yaeda Valley (~20,000 ha)"],
            "notes": "2011 Yaeda Valley Hadza に Tanzania 法制下の CCRO 付与、"
                     "Carbon Tanzania / UCRT 仲介の REDD+ プログラムと連動。"
                     "Hadza 史上初の集合的法的土地権の確立。",
        },
        valid_from="2011-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.7, source_id=src_hadza_land,
        note="IDSov: 土地保有権は Hadza コミュニティの自己決定強化として重要。"
             "REDD+ 仕組みへの当事者評価は多様。",
    )
    facets_inserted.append(("hadza", "territory", "ccro_2011", f))

    # ---------- Iroquois (Haudenosaunee) -----------------------------------
    f = add_facet(
        ORG["iroquois"], "governance",
        {
            "phase": "great_law_of_peace_founding",
            "regime": "Great Law of Peace (Kaianere'kó:wa) - 5 nations confederacy",
            "decision_locus": "Grand Council (50 sachems from 5 nations)、"
                              "Clan Mothers が sachem を nominate",
            "key_bodies": ["Grand Council", "Clan Mothers (Gantowisas)",
                            "5 nations (Mohawk, Oneida, Onondaga, Cayuga, Seneca)"],
            "notes": "Great Law of Peace 成立年代は学界で議論あり: "
                     "Mann & Fields (1997) は天文学的考察 (日食) から ~1142 年、"
                     "他の研究者は ~1450 年を支持。Haudenosaunee Confederacy 公式は "
                     "1142 説を支持。Peacemaker (Deganawida) と Hiawatha が"
                     "創設者として伝承。",
        },
        valid_from="1142-08-31", valid_from_precision="period",
        valid_to="1721-12-31",   valid_to_precision="year",
        confidence=0.55, source_id=src_mann,
        note="IDSov: 創設年代は Haudenosaunee 内部の口承伝統と外部学術の"
             "解釈が異なる。Confederacy 公式の 1142 説を採用するが、"
             "学術的不確実性は高い。precision='period' で表現。",
    )
    facets_inserted.append(("iroquois", "governance", "great_law", f))

    f = add_facet(
        ORG["iroquois"], "membership",
        {
            "phase": "tuscarora_addition",
            "basis": "5 nations → 6 nations 拡張",
            "eligibility": "Tuscarora が 1722 年に正式加盟 (Mohawk 後援)",
            "notes": "1722 Tuscarora Nation が 5 nations に加盟、'Six Nations' 体制に。"
                     "Tuscarora は North Carolina から避難してきた経緯。"
                     "Grand Council での発言は Mohawk を通じる構造 (歴史的に)。",
        },
        valid_from="1722-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_hcn_official,
        note="IDSov: Tuscarora 加盟の経緯は Six Nations 公式記録に依拠。",
    )
    facets_inserted.append(("iroquois", "membership", "tuscarora", f))

    f = add_facet(
        ORG["iroquois"], "legitimation_basis",
        {
            "phase": "influence_on_us_constitution",
            "basis": "米国独立思想・連邦制度設計への影響 (議論あり)",
            "notes": "Benjamin Franklin の Albany Plan (1754) や U.S. Constitution "
                     "の federalism に Haudenosaunee 政治モデルが影響したとする"
                     "解釈 (1988 U.S. Senate Concurrent Resolution 76 で公式承認)。"
                     "学界では影響度合いに議論あるが、Haudenosaunee 公式立場は"
                     "影響を主張。",
        },
        valid_from="1754-01-01", valid_from_precision="year",
        valid_to="1789-12-31",   valid_to_precision="year",
        confidence=0.6, source_id=src_hcn_official,
        note="IDSov: 米国憲法への影響は Haudenosaunee 自己理解の重要部分。"
             "学術的議論はあるが、当事者公式立場を尊重。",
    )
    facets_inserted.append(("iroquois", "legitimation_basis", "us_influence", f))

    f = add_facet(
        ORG["iroquois"], "territory",
        {
            "phase": "post_revolution_dispersal",
            "extent_label": "米国独立革命後の territory 分裂 (米国 vs. 英国側)",
            "key_regions": ["New York (Onondaga, Seneca, Tuscarora 等)",
                            "Ontario (Six Nations of the Grand River)",
                            "Quebec (Kahnawà:ke, Kanehsatà:ke - Mohawk)"],
            "notes": "1779 Sullivan Expedition で Iroquois 集落破壊。"
                     "Joseph Brant 率いる親英 Mohawk らは Ontario へ移住 "
                     "(Six Nations of the Grand River, 1784 Haldimand Tract)。"
                     "Onondaga 等は New York に残留。Confederacy は二分化。",
        },
        valid_from="1779-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_wallace,
        note="IDSov: 二分化は当事者経験として重要、外部記述は限界あり。",
    )
    facets_inserted.append(("iroquois", "territory", "post_revolution", f))

    f = add_facet(
        ORG["iroquois"], "governance",
        {
            "phase": "modern_dual_council",
            "regime": "現代の二重統治構造 (伝統的 Confederacy + 国家制度下の council)",
            "decision_locus": "Onondaga Council Fire (Onondaga, NY) と Six Nations "
                              "Grand River (Ontario) が並列、各 nation には別途"
                              "国家制度下の elected council (Indian Act / BIA)",
            "key_bodies": ["Haudenosaunee Confederacy Grand Council",
                            "Six Nations Council (Ontario, federal)",
                            "Tribal/Band Councils (各 nation)"],
            "notes": "20-21c の Confederacy は伝統的 sachems system を継続するが、"
                     "カナダ Indian Act (1876-) と米国 BIA 制度下で elected "
                     "council が並存。両者の正統性に内部緊張あり。",
        },
        valid_from="1924-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.7, source_id=src_hcn_official,
        note="IDSov: dual governance は当事者にとって sensitive な政治状況。"
             "Confederacy 公式立場は伝統的 governance の正統性を主張。"
             "1924 はカナダで Six Nations Grand River に elected council "
             "強制導入された年。",
    )
    facets_inserted.append(("iroquois", "governance", "modern_dual", f))

    f = add_facet(
        ORG["iroquois"], "legitimation_basis",
        {
            "phase": "doctrine_of_discovery_resistance",
            "basis": "Doctrine of Discovery (1493 Inter Caetera) への正統性闘争、"
                     "国際的先住民権利運動の中核アクター",
            "notes": "Haudenosaunee は 1923 Deskaheh の League of Nations 訴え以来、"
                     "国際舞台で sovereign nation status を主張。"
                     "2007 UN Declaration on Rights of Indigenous Peoples (UNDRIP) 採択、"
                     "2023 Vatican の Doctrine of Discovery 公式撤回への寄与。"
                     "Haudenosaunee passport の継続発行 (国際旅行に使用)。",
        },
        valid_from="1923-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_hcn_official,
        note="IDSov: 主権闘争は Haudenosaunee の中核的政治活動、"
             "公式自己記述を尊重した記録。",
    )
    facets_inserted.append(("iroquois", "legitimation_basis", "doctrine_resistance", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ
    # =========================================================================
    print("=" * 70)
    print(f"Phase 4 Team G: 投入 facet レコード数 = {len(facets_inserted)}")
    print("=" * 70)
    print()

    print("Q1. 組織別 facet 件数")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT o.canonical_name, COUNT(*) AS n
        FROM organization_temporal_facet f
        JOIN organization o ON o.organization_id = f.organization_id
        WHERE f.organization_id IN (?,?,?,?,?)
        GROUP BY o.canonical_name
        ORDER BY n DESC
        """,
        tuple(ORG.values()),
    ).fetchall()
    for name, n in rows:
        print(f"  {name}: {n} facets")
    print()

    print("Q2. facet_type 分布 (本投入分)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, COUNT(*)
        FROM organization_temporal_facet
        WHERE organization_id IN (?,?,?,?,?)
        GROUP BY facet_type ORDER BY 2 DESC
        """,
        tuple(ORG.values()),
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")
    print()

    print("Q3. Anonymous の identity 推移")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'identity'
        ORDER BY valid_from
        """,
        (ORG["anonymous"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('phase')}: "
              f"{v.get('dominant_identity')[:60]}...")
    print()

    print("Q4. WMF governance 推移 (ED/CEO 交代)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value, confidence
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'governance'
        ORDER BY valid_from
        """,
        (ORG["wmf"],),
    ).fetchall()
    for vf, vt, fv, conf in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | conf={conf} | {v.get('phase')}")
    print()

    print("Q5. IDSov 配慮の interpretation_note 検証 (Hadza/Iroquois)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT o.canonical_name, f.facet_type, c.interpretation_note
        FROM organization_temporal_facet f
        JOIN organization o ON o.organization_id = f.organization_id
        JOIN claim c ON c.claim_id = f.claim_id
        WHERE f.organization_id IN (?, ?)
          AND c.interpretation_note IS NOT NULL
        ORDER BY o.canonical_name, f.facet_type
        """,
        (ORG["hadza"], ORG["iroquois"]),
    ).fetchall()
    for name, ft, note in rows:
        head = "IDSov" if "IDSov" in (note or "") else "note"
        print(f"  [{head}] {name} / {ft}: {(note or '')[:80]}...")
    print()

    print(f"全 organization_temporal_facet 件数 (累計): "
          f"{cur.execute('SELECT COUNT(*) FROM organization_temporal_facet').fetchone()[0]}")

    conn.close()


if __name__ == "__main__":
    main()
