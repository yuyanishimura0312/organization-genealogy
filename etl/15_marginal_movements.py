#!/usr/bin/env python3
"""Stream O: 周縁・運動・先住民の 5 ケース完全注釈

ケース:
  1. Black Panther Party (BPP, 1966-1982) — リーダー型革命運動、Survival Programs、FBI COINTELPRO 弾圧で解体
  2. Self-Employed Women's Association (SEWA, 1972-) — インド女性自営労働組合、Mahila SEWA Bank (1974) を内包
  3. Iroquois / Haudenosaunee Confederacy (推定 c.1142-1660 範囲、現存) — Great Law of Peace、6 nation 評議会
  4. Linux Kernel Community (1991-) — メーリングリスト型開発体、benevolent dictator + maintainers
  5. Anonymous (2003-) — リーダーレス・分散ハクティビズム集合体

既存ケースとの relation:
  - SEWA → Mondragón (mimetic, 協同組合連帯モデル比較)
  - SEWA → Grameen Bank (mimetic, 1974 SEWA Bank が Grameen 1983 に先行する女性向け金融)
  - Iroquois → Wikimedia Foundation (normative_pressure, 合意形成規範の引用関係を示唆)
  - Linux Kernel Community → Linux Foundation (subsidiary 的構造、母体 community → 後設の財団)
  - BPP → Anonymous (mimetic_isomorphism、リーダー型 vs リーダーレスの対照ペア。
                     直接の継承ではなく抗議・大衆運動の組織形態の系譜上の対照)

Indigenous Data Sovereignty (IDSov / CARE Principles 2019) 配慮:
  - Iroquois Confederacy について:
      * 創設年は単一日付を主張せず、scholarly range (c.1142 — Mann & Fields 1997 の天文学的推定 /
        c.1450-1660 — 多数派学説) を併記して partial 値で記録。
      * 内部統治・儀礼の詳細は記述せず、外部から観察可能な「制度形態」レベルに留める。
      * 出典は外部学術文献 (Wikipedia, Britannica, Fenton 1998) のみで、
        Haudenosaunee Confederacy 公式サイト (haudenosauneeconfederacy.com) に言及する場合も
        「先住民自治体の自己記述として参照」と明示し、外部研究者の解釈と分離。
      * 主張は「記述的 (descriptive)」レベルに限定し、impact_record の direction は descriptive。
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"


def uid():
    return uuid.uuid4().hex


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # ---------------- helpers ----------------
    def add_source(stype, title, **kw):
        sid = uid()
        cur.execute(
            "INSERT INTO source (source_id, source_type, title, authors, publication_date, "
            "publisher, locator, accessed_at, reliability_score, reliability_basis, license, redistribution) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (sid, stype, title,
             json.dumps(kw.get("authors")) if kw.get("authors") else None,
             kw.get("publication_date"), kw.get("publisher"),
             json.dumps(kw.get("locator")) if kw.get("locator") else None,
             kw.get("accessed_at"),
             kw.get("reliability_score"), kw.get("reliability_basis"),
             kw.get("license"), kw.get("redistribution", "attribution_required")))
        return sid

    def add_claim(et, eid, fp, vk, val, src, conf, by="claude_stream_o", note=None):
        cid = uid()
        cur.execute(
            "INSERT INTO claim (claim_id, entity_type, entity_id, field_path, value_kind, "
            "claim_value, source_id, confidence, recorded_by, interpretation_note) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cid, et, eid, fp, vk,
             json.dumps(val, ensure_ascii=False) if val is not None else None,
             src, conf, by, note))
        return cid

    def add_org(name, **kw):
        oid = uid()
        cur.execute(
            "INSERT INTO organization (organization_id, canonical_name, alternate_names, "
            "description, primary_form_id, geo_scope, start_date, start_date_precision, "
            "end_date, end_date_precision, status, attributes, external_ids) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (oid, name,
             json.dumps(kw.get("alternate_names"), ensure_ascii=False) if kw.get("alternate_names") else None,
             kw.get("description"), kw.get("primary_form_id"),
             json.dumps(kw.get("geo_scope"), ensure_ascii=False) if kw.get("geo_scope") else None,
             kw.get("start_date"), kw.get("start_date_precision"),
             kw.get("end_date"), kw.get("end_date_precision"),
             kw.get("status", "unknown"),
             json.dumps(kw.get("attributes"), ensure_ascii=False) if kw.get("attributes") else None,
             json.dumps(kw.get("external_ids"), ensure_ascii=False) if kw.get("external_ids") else None))
        return oid

    def assign_form(oid, tax, code, **kw):
        row = cur.execute(
            "SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
            (tax, code)).fetchone()
        if not row:
            return None
        cur.execute(
            "INSERT INTO organization_form_assignment "
            "(assignment_id, organization_id, form_id, valid_from, valid_to, is_primary, confidence, claim_id) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (uid(), oid, row[0], kw.get("valid_from"), kw.get("valid_to"),
             1 if kw.get("is_primary") else 0,
             kw.get("confidence", 0.8), kw.get("claim_id")))
        if kw.get("is_primary"):
            cur.execute("UPDATE organization SET primary_form_id=? WHERE organization_id=?",
                        (row[0], oid))

    def add_act(oid, atype, **kw):
        aid = uid()
        cur.execute(
            "INSERT INTO activity (activity_id, organization_id, activity_type, domain, "
            "description, inputs, outputs, scale, orientation, valid_from, valid_to, confidence, claim_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (aid, oid, atype, kw.get("domain"), kw.get("description"),
             json.dumps(kw.get("inputs"), ensure_ascii=False) if kw.get("inputs") else None,
             json.dumps(kw.get("outputs"), ensure_ascii=False) if kw.get("outputs") else None,
             json.dumps(kw.get("scale"), ensure_ascii=False) if kw.get("scale") else None,
             kw.get("orientation", "unspecified"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")))
        return aid

    def add_func(oid, ft, **kw):
        fid = uid()
        cur.execute(
            "INSERT INTO function_record (function_id, organization_id, function_type_id, "
            "mechanism, beneficiaries, dependency, activity_id, valid_from, valid_to, confidence, claim_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (fid, oid, ft,
             json.dumps(kw.get("mechanism"), ensure_ascii=False) if kw.get("mechanism") else None,
             json.dumps(kw.get("beneficiaries"), ensure_ascii=False) if kw.get("beneficiaries") else None,
             json.dumps(kw.get("dependency"), ensure_ascii=False) if kw.get("dependency") else None,
             kw.get("activity_id"), kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")))
        return fid

    def add_imp(oid, dom, mname, mval, dir_, hor, **kw):
        iid = uid()
        cur.execute(
            "INSERT INTO impact_record (impact_id, organization_id, impact_domain, metric_name, "
            "metric_value, direction, time_horizon, affected_scope, evaluation_method, "
            "valid_from, valid_to, confidence, claim_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (iid, oid, dom, mname,
             json.dumps(mval, ensure_ascii=False),
             dir_, hor,
             json.dumps(kw.get("affected_scope"), ensure_ascii=False) if kw.get("affected_scope") else None,
             kw.get("evaluation_method"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")))
        return iid

    def add_event(etype, **kw):
        eid = uid()
        cur.execute(
            "INSERT INTO event (event_id, event_type, event_date, event_date_precision, "
            "description, participants, causes, outcomes, location, dissolution_cause, vsr_label, "
            "confidence, claim_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (eid, etype, kw.get("event_date"), kw.get("event_date_precision","unknown"),
             kw.get("description"),
             json.dumps(kw.get("participants"), ensure_ascii=False) if kw.get("participants") else None,
             json.dumps(kw.get("causes"), ensure_ascii=False) if kw.get("causes") else None,
             json.dumps(kw.get("outcomes"), ensure_ascii=False) if kw.get("outcomes") else None,
             json.dumps(kw.get("location"), ensure_ascii=False) if kw.get("location") else None,
             kw.get("dissolution_cause"), kw.get("vsr_label"),
             kw.get("confidence"), kw.get("claim_id")))
        return eid

    def link_eo(eid, oid, role):
        cur.execute(
            "INSERT OR IGNORE INTO event_organization "
            "(event_organization_id, event_id, organization_id, role) VALUES (?,?,?,?)",
            (uid(), eid, oid, role))

    def add_relation(src, tgt, rtype, **kw):
        rid = uid()
        cur.execute(
            "INSERT INTO relation (relation_id, source_organization_id, target_organization_id, "
            "relation_type, directionality, valid_from, valid_to, strength, strength_basis, "
            "relation_attributes, confidence, claim_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (rid, src, tgt, rtype, kw.get("directionality", "directed"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("strength"), kw.get("strength_basis"),
             json.dumps(kw.get("relation_attributes"), ensure_ascii=False) if kw.get("relation_attributes") else None,
             kw.get("confidence"), kw.get("claim_id")))
        return rid

    def find_org_exact(name):
        row = cur.execute(
            "SELECT organization_id FROM organization WHERE canonical_name=? LIMIT 1",
            (name,)).fetchone()
        return row[0] if row else None

    inserted = []

    # ============================================================
    # SOURCES
    # ============================================================
    src_bpp_wp = add_source("secondary_literature",
        "Wikipedia: Black Panther Party",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Black_Panther_Party"},
        accessed_at="2026-05-02", reliability_score=0.55,
        reliability_basis="二次情報源、複数の一次史料を参照",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_bpp_britannica = add_source("secondary_literature",
        "Britannica: Black Panther Party",
        publisher="Encyclopaedia Britannica",
        locator={"url": "https://www.britannica.com/topic/Black-Panther-Party"},
        accessed_at="2026-05-02", reliability_score=0.7,
        reliability_basis="編集された百科事典、編集者監督あり")

    src_bpp_johnson = add_source("secondary_literature",
        "Johnson, O.A. III, 'Explaining the Demise of the Black Panther Party'",
        authors=["Ollie A. Johnson III"],
        publisher="The Black Panther Party Reconsidered (ed. Charles E. Jones, 1998)",
        publication_date="1998-01-01",
        reliability_score=0.85,
        reliability_basis="BPP 解体過程の学術論考")

    src_bpp_nmaahc = add_source("secondary_literature",
        "Smithsonian NMAAHC: The Black Panther Party",
        publisher="National Museum of African American History and Culture",
        locator={"url": "https://nmaahc.si.edu/explore/stories/black-panther-party-challenging-police-and-promoting-social-change"},
        accessed_at="2026-05-02", reliability_score=0.85,
        reliability_basis="国立博物館の編集物、一次史料アーカイブを背景に持つ")

    src_sewa_wp = add_source("secondary_literature",
        "Wikipedia: Self Employed Women's Association",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Self_Employed_Women%27s_Association"},
        accessed_at="2026-05-02", reliability_score=0.55,
        license="CC-BY-SA-4.0")

    src_sewa_official = add_source("primary_text",
        "SEWA Official History",
        publisher="Self-Employed Women's Association",
        locator={"url": "https://www.sewa.org/about-us/history/"},
        accessed_at="2026-05-02", reliability_score=0.8,
        reliability_basis="組織自身の公式自己記述、一次資料として扱う",
        license="reference_only", redistribution="attribution_required")

    src_sewa_bhatt = add_source("primary_text",
        "Bhatt, E.R. (2006) We Are Poor but So Many: The Story of Self-Employed Women in India",
        authors=["Ela R. Bhatt"], publication_date="2006-01-01",
        publisher="Oxford University Press", reliability_score=0.85,
        reliability_basis="SEWA 創設者自伝・組織史の一次証言")

    # Iroquois — Indigenous Data Sovereignty 配慮で出典は学術文献優先
    src_iroquois_wp = add_source("secondary_literature",
        "Wikipedia: Haudenosaunee / Great Law of Peace",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Great_Law_of_Peace",
                 "secondary_url": "https://en.wikipedia.org/wiki/Iroquois"},
        accessed_at="2026-05-02", reliability_score=0.55,
        license="CC-BY-SA-4.0")

    src_iroquois_fenton = add_source("secondary_literature",
        "Fenton, W.N. (1998) The Great Law and the Longhouse",
        authors=["William N. Fenton"], publication_date="1998-01-01",
        publisher="University of Oklahoma Press", reliability_score=0.85,
        reliability_basis="Haudenosaunee 政治制度史の代表的人類学研究。"
                          "ただし外部研究者視点であり、内部口承との緊張は別途認識")

    src_iroquois_mann_fields = add_source("secondary_literature",
        "Mann, B.A. & Fields, J.L. (1997) 'A Sign in the Sky: Dating the League of the Haudenosaunee'",
        authors=["Barbara A. Mann", "Jerry L. Fields"],
        publication_date="1997-01-01",
        publisher="American Indian Culture and Research Journal 21(2)",
        reliability_score=0.7,
        reliability_basis="日食データから 1142 年と推定。後続研究で議論あり")

    src_iroquois_self = add_source("primary_text",
        "Haudenosaunee Confederacy — Confederacy's Creation (公式自己記述)",
        publisher="Haudenosaunee Confederacy",
        locator={"url": "https://www.haudenosauneeconfederacy.com/confederacys-creation/"},
        accessed_at="2026-05-02", reliability_score=0.85,
        reliability_basis="Haudenosaunee 自身による公式自己記述。"
                          "IDSov/CARE Principles に従い、内部解釈の権威として記録。"
                          "外部分析と区別して扱う",
        license="reference_only", redistribution="restricted")

    src_linux_corbet = add_source("secondary_literature",
        "Corbet, J. & Kroah-Hartman, G. (annual) Linux Kernel Development reports",
        authors=["Jonathan Corbet", "Greg Kroah-Hartman"],
        publisher="Linux Foundation",
        locator={"url": "https://www.linuxfoundation.org/resources/publications"},
        accessed_at="2026-05-02", reliability_score=0.85,
        reliability_basis="Linux カーネル開発統計の年次報告")

    src_linux_torvalds_email = add_source("primary_text",
        "Torvalds, L. (1991-08-25) 'What would you like to see most in minix?' (Linux release announcement)",
        authors=["Linus Torvalds"], publication_date="1991-08-25",
        publisher="comp.os.minix newsgroup",
        locator={"archive": "Google Groups comp.os.minix"},
        reliability_score=0.95,
        reliability_basis="Linux 公開アナウンスメントの原電子メール")

    src_linux_raymond = add_source("secondary_literature",
        "Raymond, E.S. (1999) The Cathedral and the Bazaar",
        authors=["Eric S. Raymond"], publication_date="1999-01-01",
        publisher="O'Reilly", reliability_score=0.7,
        reliability_basis="Linux 開発モデルを bazaar として理論化した古典。"
                          "イデオロギー的偏向あり、参照レベル")

    src_anon_coleman = add_source("secondary_literature",
        "Coleman, G. (2014) Hacker, Hoaxer, Whistleblower, Spy: The Many Faces of Anonymous",
        authors=["Gabriella Coleman"], publication_date="2014-01-01",
        publisher="Verso", reliability_score=0.85,
        reliability_basis="Anonymous の参与観察に基づく人類学的研究")

    src_anon_wp = add_source("secondary_literature",
        "Wikipedia: Anonymous (hacker group)",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Anonymous_(hacker_group)"},
        accessed_at="2026-05-02", reliability_score=0.55,
        license="CC-BY-SA-4.0")

    # ============================================================
    # CASE 1: Black Panther Party (1966-1982)
    # ============================================================
    bpp = add_org("Black Panther Party (BPP)",
        alternate_names=[
            {"name": "Black Panther Party for Self-Defense (1966-1968)", "lang": "en"},
            {"name": "ブラックパンサー党", "lang": "ja"},
            {"name": "BPP", "lang": "en"},
        ],
        description="1966 年 10 月 15 日に Bobby Seale と Huey P. Newton がカリフォルニア州オークランドで設立した黒人解放革命政党。"
                    "Ten-Point Program (1966) を綱領、警察ブルタリティへの市民武装監視 (cop-watch) と "
                    "Free Breakfast for Children (1969-) など Survival Programs を実施。"
                    "FBI COINTELPRO の弾圧、内部分裂、Newton の腐敗などにより衰退、1982 年に Oakland Community School 閉鎖をもって事実上解体。",
        geo_scope={"hq": "Oakland, California", "chapters": "全米主要都市", "international": ["Algiers (国際支部)"]},
        start_date="1966-10-15", start_date_precision="exact",
        end_date="1982-12-31", end_date_precision="year",
        status="extinct",
        attributes={
            "founders": ["Bobby Seale", "Huey P. Newton"],
            "membership_peak_estimate": 2000,
            "membership_peak_year": 1968,
            "membership_late": 27,
            "membership_late_year": 1980,
            "ideology": ["Black Power", "revolutionary socialism", "Marxism-Leninism", "self-defense"],
            "key_documents": ["Ten-Point Program (October 1966)", "The Black Panther newspaper (1967-1980)"],
        },
        external_ids={"wikidata": "Q241997"})
    inserted.append(("organization", bpp, "Black Panther Party"))

    bpp_claim = add_claim("organization", bpp, "start_date", "present",
        {"date": "1966-10-15", "context": "Seale と Newton による Oakland での結党"},
        src_bpp_nmaahc, 0.95, note="Smithsonian NMAAHC を含む複数二次史料で一致")

    assign_form(bpp, "historical_era", "platform", confidence=0.4,
                claim_id=add_claim("organization_form_assignment", bpp, "form", "partial",
                    {"reasoning": "現代型 platform ではないが、革命運動と community service の "
                                  "混合プラットフォームと暫定的に位置づけ。primary ではない"},
                    src_bpp_johnson, 0.4))
    assign_form(bpp, "mintzberg_1989", "missionary", is_primary=True, confidence=0.8,
                claim_id=add_claim("organization_form_assignment", bpp, "form", "present",
                    {"reasoning": "イデオロギー (Ten-Point Program) による標準化と、強い使命感主導の調整"},
                    src_bpp_johnson, 0.8))
    assign_form(bpp, "mintzberg_1989", "simple", confidence=0.6,
                claim_id=add_claim("organization_form_assignment", bpp, "form", "partial",
                    {"reasoning": "創設期は Newton/Seale 中央権威の simple structure。"
                                  "後期は missionary 要素と political 要素が混在"},
                    src_bpp_wp, 0.6))
    assign_form(bpp, "laloux_2014", "red", confidence=0.55,
                claim_id=add_claim("organization_form_assignment", bpp, "form", "partial",
                    {"reasoning": "Laloux の枠組み適用は時代錯誤。Newton 中心のカリスマ的権威構造を "
                                  "Red 的と暫定整理するが解釈は慎重に"},
                    src_bpp_johnson, 0.55))

    # Activities
    act_bpp_copwatch = add_act(bpp, "armed_community_self_defense", domain="政治",
        description="Oakland 市内で警察パトロールを市民武装監視。"
                    "California 公開銃携帯法 (当時) を活用し、警察執行を公衆視認下に置く戦術",
        outputs={"action": "cop-watch patrols", "documentation": "市民権教示資料"},
        orientation="exploitation",
        valid_from="1966-10-15", valid_to="1968-12-31", confidence=0.85)

    act_bpp_breakfast = add_act(bpp, "community_service_program", domain="社会保障",
        description="Free Breakfast for Children (1969 年 1 月開始、Oakland St. Augustine's 聖公会教会)。"
                    "1969 年に 20,000 児童に給食、1971 年に 36 都市で展開と報告",
        outputs={"program": "Free Breakfast for Children",
                 "scale_1969": "20000 children/year (Party 自己報告)",
                 "scale_1971_cities": 36},
        scale={"national_reach": "36+ cities", "duration_years": "1969-late_1970s"},
        orientation="exploitation",
        valid_from="1969-01-01", valid_to="1980-12-31", confidence=0.85)

    act_bpp_publishing = add_act(bpp, "movement_press", domain="伝達",
        description="The Black Panther 党新聞の発行 (1967-1980)。週刊、ピーク発行部数 約 25 万",
        outputs={"newspaper": "The Black Panther",
                 "peak_circulation": 250000},
        orientation="exploitation",
        valid_from="1967-04-25", valid_to="1980-12-31", confidence=0.7)

    # Functions
    add_func(bpp, "miller_18_decider",
             mechanism={"means": ["Central Committee (Newton, Seale, Cleaver, Hilliard ら)",
                                  "Minister of Defense (Newton)",
                                  "Chairman (Seale)"],
                        "note": "強いカリスマ的中央権威。後期に Newton 専制化"},
             confidence=0.85)
    add_func(bpp, "vsm_s5_policy_identity",
             mechanism={"means": ["Ten-Point Program (1966 年 10 月)",
                                  "Three Main Rules of Discipline / Eight Points of Attention"],
                        "note": "毛沢東の解放軍規律から借用したアイデンティティ規範"},
             confidence=0.85)
    add_func(bpp, "miller_19_encoder",
             mechanism={"means": ["The Black Panther newspaper",
                                  "公の「ベレー帽 + 革ジャン + ショットガン」象徴体系"]},
             activity_id=act_bpp_publishing, confidence=0.85)
    add_func(bpp, "miller_06_producer",
             mechanism={"means": ["Survival Programs: 朝食、医療診療所、衣類配布、"
                                  "Sickle Cell Anemia Foundation 検査、liberation schools"]},
             activity_id=act_bpp_breakfast, confidence=0.85)
    add_func(bpp, "miller_02_boundary",
             mechanism={"means": ["Party member 認定、章 (chapter) 加盟手続き、"
                                  "中央委員会による除名権"]},
             confidence=0.7)
    add_func(bpp, "miller_11_input_transducer",
             mechanism={"means": ["コミュニティ視察、被害者インタビュー、警察ブルタリティ証拠収集"]},
             confidence=0.7)

    # Impact
    add_imp(bpp, "政治", "police_accountability_movement",
            {"description": "後の警察説明責任運動 (#BlackLivesMatter, copwatch 系団体) の先駆け。"
                            "市民武装監視と社会プログラムを結合した革命組織モデルの参照点"},
            "descriptive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"region": "United States",
                            "successor_movements": ["BLM (2013-)", "copwatch organizations"]},
            confidence=0.7,
            claim_id=add_claim("impact_record", "pending", "type", "present",
                {"reasoning": "影響史は学術的に確立されているが因果連鎖は単線的でない"},
                src_bpp_nmaahc, 0.7))

    add_imp(bpp, "社会", "free_school_meal_template",
            {"description": "Free Breakfast for Children が後の連邦 School Breakfast Program 拡充 "
                            "(1975) への政治圧力源となったとする学説あり"},
            "positive", "long_term",
            evaluation_method="historical_interpretation",
            affected_scope={"target": "U.S. school nutrition policy"},
            confidence=0.6)

    add_imp(bpp, "政治", "state_repression_target",
            {"description": "FBI COINTELPRO の主要標的。Fred Hampton 暗殺 (1969-12-04) など、"
                            "国家による抑圧的弾圧の典型ケースとして組織研究で参照"},
            "negative", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"target": "BPP itself, civil liberties record"},
            confidence=0.85)

    # Events
    e_bpp_founding = add_event("founding",
        event_date="1966-10-15", event_date_precision="exact",
        description="Bobby Seale と Huey P. Newton がカリフォルニア州オークランドで Black Panther Party for Self-Defense を結党",
        participants=["Bobby Seale", "Huey P. Newton"],
        causes={"political": "Watts riots (1965) 後の警察ブルタリティ問題",
                "intellectual": "Malcolm X 暗殺、Fanon 受容、Maoism"},
        outcomes={"new_org": "BPP", "innovation": "armed cop-watch + community service モデル"},
        location={"city": "Oakland, California"},
        vsr_label="variation", confidence=0.95)
    link_eo(e_bpp_founding, bpp, "founder")

    e_bpp_breakfast_start = add_event("reform",
        event_date="1969-01-01", event_date_precision="month",
        description="Free Breakfast for Children プログラム開始 (Oakland St. Augustine's 聖公会教会)",
        outcomes={"new_activity": "Survival Programs の起点",
                  "rapid_growth": "1971 年に 36 都市へ展開"},
        vsr_label="retention", confidence=0.85)
    link_eo(e_bpp_breakfast_start, bpp, "transformed")

    e_bpp_dissolution = add_event("dissolution",
        event_date="1982-12-31", event_date_precision="year",
        description="Oakland Community School 閉鎖をもって BPP が事実上解体。"
                    "1980 年時点で実働メンバー 27 名にまで縮小",
        dissolution_cause="political_purge",
        causes={"state_repression": "FBI COINTELPRO による分裂工作",
                "internal": "Newton-Cleaver 派閥分裂 (1971)、Newton の腐敗・薬物問題",
                "external": "リーダー暗殺 (Hampton 1969)、メンバー大量逮捕"},
        outcomes={"successor_movements": ["BLM 系列", "copwatch 系列"]},
        vsr_label="selection", confidence=0.85)
    link_eo(e_bpp_dissolution, bpp, "dissolved")

    # ============================================================
    # CASE 2: SEWA — Self-Employed Women's Association (1972-)
    # ============================================================
    sewa = add_org("Self-Employed Women's Association (SEWA)",
        alternate_names=[
            {"name": "SEWA", "lang": "en"},
            {"name": "セワ / インド自営女性協会", "lang": "ja"},
        ],
        description="1972 年 4 月 12 日にエラ・バット (Ela R. Bhatt) がインド・グジャラート州アフマダーバードで設立した、"
                    "インフォーマル経済の女性労働者向け労働組合。Mahatma Gandhi が 1918 年に組織した "
                    "Textile Labour Association (TLA) の女性部から派生。1974 年には Mahila SEWA Sahakari Bank "
                    "を協同組合銀行として設立し、組合員所有の貯蓄主導型マイクロファイナンスを展開。"
                    "現在 380 万人 (2026 時点組織発表) の組合員を 20 州以上に擁する。",
        geo_scope={"hq": "Ahmedabad, Gujarat, India",
                   "states": "20+ Indian states",
                   "international_affiliates": ["WIEGO", "HomeNet International"]},
        start_date="1972-04-12", start_date_precision="exact",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "founder": "Ela R. Bhatt (1933-2022)",
            "membership_2013": 1919676,
            "membership_2024_self_reported": 3780000,
            "registered_as": "trade union (1972), with cooperative bank arm (1974)",
            "innovations": ["インフォーマル経済の労働組合化",
                            "貯蓄主導型協同組合銀行",
                            "女性自己雇用者の集団交渉"],
            "awards": ["Right Livelihood Award (1984, Bhatt)", "Magsaysay Award (1977)"],
        },
        external_ids={"wikidata": "Q1124302"})
    inserted.append(("organization", sewa, "SEWA"))

    sewa_claim = add_claim("organization", sewa, "start_date", "present",
        {"date": "1972-04-12", "context": "アフマダーバードで労働組合として登録"},
        src_sewa_official, 0.9, note="SEWA 公式史と Wikipedia で一致")

    assign_form(sewa, "legal_form", "cooperative", is_primary=True, confidence=0.85,
                claim_id=add_claim("organization_form_assignment", sewa, "form", "present",
                    {"reasoning": "労働組合 + 協同組合銀行 + 協同組合連合 (SEWA Federation) のハイブリッド構造。"
                                  "primary としては cooperative 性が支配的"},
                    src_sewa_bhatt, 0.85))
    assign_form(sewa, "mintzberg_1989", "missionary", confidence=0.75,
                claim_id=add_claim("organization_form_assignment", sewa, "form", "present",
                    {"reasoning": "Gandhian 価値観 (sat, ahimsa, sarvodaya) による標準化が支配的"},
                    src_sewa_bhatt, 0.75))
    assign_form(sewa, "laloux_2014", "green", confidence=0.6,
                claim_id=add_claim("organization_form_assignment", sewa, "form", "partial",
                    {"reasoning": "ステークホルダー多元性、価値観主導は green 的。Teal 化の制度的兆候は限定的"},
                    src_sewa_wp, 0.6))

    # Activities
    act_sewa_organize = add_act(sewa, "labor_organizing", domain="政治",
        description="家事労働者・行商・ビーディー巻き工・廃品回収者など、インフォーマル経済 11 業種以上の女性組織化",
        outputs={"organized_trades": "11+ informal sector trades",
                 "advocacy": "minimum wage, social protection"},
        orientation="exploration",
        valid_from="1972-04-12", confidence=0.85)

    act_sewa_bank = add_act(sewa, "cooperative_finance", domain="金融",
        description="Mahila SEWA Sahakari Bank: 4,000 名の女性自営業者が出資し 1974 年に協同組合銀行として設立。"
                    "貯蓄主導型 — 信用提供の前にまず預金参加を求める。組合員選出役員、組合員設定金利",
        inputs={"deposits": "members_only", "share_capital": "4000_founding_members"},
        outputs={"loans": "to women self-employed",
                 "savings_products": "members"},
        orientation="exploration",
        valid_from="1974-05-20", confidence=0.85)

    act_sewa_federation = add_act(sewa, "cooperative_federation_governance", domain="統治",
        description="SEWA Cooperative Federation を通じた業種別協同組合 (廃品回収、刺繍、農産物加工、児童ケア等) の連邦運営",
        orientation="exploitation",
        valid_from="1992-01-01", confidence=0.8)

    # Functions
    add_func(sewa, "miller_18_decider",
             mechanism={"means": ["代議員制総会 (組合員選出)",
                                  "女性のみで構成される理事会"]},
             activity_id=act_sewa_federation, confidence=0.85)
    add_func(sewa, "miller_03_ingestor",
             mechanism={"means": ["組合員月会費", "Mahila SEWA Bank 預金",
                                  "国際協力機関助成 (Ford Foundation, ILO 等)"]},
             confidence=0.8)
    add_func(sewa, "vsm_s5_policy_identity",
             mechanism={"means": ["Gandhian 11 Questions (full employment, food security, "
                                  "shelter, health, child care, asset ownership, "
                                  "organising, leadership, self-reliance, education, social protection)"]},
             confidence=0.85)
    add_func(sewa, "miller_01_reproducer",
             mechanism={"means": ["他州への支部展開 (SEWA Bharat 1984-)、"
                                  "国際版 (HomeNet, WIEGO 共同設立) を通じた組織形態の伝播"]},
             confidence=0.8)
    add_func(sewa, "miller_06_producer",
             mechanism={"means": ["業種別協同組合での集団生産・販売"]},
             activity_id=act_sewa_federation, confidence=0.75)

    # Impact
    add_imp(sewa, "経済", "informal_sector_unionization",
            {"description": "インフォーマル経済の労働組合化という先例、"
                            "ILO の Decent Work アジェンダ (1999) と Convention 177 (Home Work, 1996) への影響"},
            "positive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"region": "global informal labor",
                            "policy_target": "ILO Convention 177 (1996)"},
            confidence=0.8)

    add_imp(sewa, "経済", "women_microfinance_pioneer",
            {"description": "1974 年の Mahila SEWA Bank 設立は Grameen Bank 公式設立 (1983) に 9 年先行する "
                            "女性向け協同組合金融の先駆。貯蓄主導型は Grameen の信用主導型と構造的に対照",
             "founding_member_count": 4000},
            "positive", "long_term",
            evaluation_method="comparison",
            affected_scope={"contrast_org": "Grameen Bank (1983-)"},
            confidence=0.85)

    add_imp(sewa, "社会", "membership_scale",
            {"description": "現在 380 万人 (組織自己報告 2024) の女性労働者を 20 州以上で組織",
             "year": 2024, "members": 3780000},
            "descriptive", "long_term",
            evaluation_method="self_report",
            confidence=0.6,
            claim_id=add_claim("impact_record", "pending", "type", "partial",
                {"reasoning": "組合員数は組織自己報告。第三者監査は限定的"},
                src_sewa_official, 0.6,
                note="self-report は確度を下げる"))

    # Events
    e_sewa_founding = add_event("founding",
        event_date="1972-04-12", event_date_precision="exact",
        description="Ela Bhatt が Ahmedabad で SEWA を労働組合として登録",
        participants=["Ela Bhatt"],
        causes={"institutional_origin": "TLA (Textile Labour Association, 1918) 女性部"},
        outcomes={"new_org": "SEWA"},
        location={"city": "Ahmedabad, Gujarat"},
        vsr_label="variation", confidence=0.95)
    link_eo(e_sewa_founding, sewa, "founder")

    e_sewa_bank = add_event("reform",
        event_date="1974-05-20", event_date_precision="month",
        description="Mahila SEWA Sahakari Bank 設立、4,000 名の女性自営業者が出資",
        outcomes={"new_subsidiary": "Mahila SEWA Sahakari Bank",
                  "innovation": "貯蓄主導型協同組合女性銀行"},
        vsr_label="variation", confidence=0.9)
    link_eo(e_sewa_bank, sewa, "transformed")

    # ============================================================
    # CASE 3: Iroquois / Haudenosaunee Confederacy
    # ============================================================
    # IDSov 配慮: 名称は Haudenosaunee を主、Iroquois (外名) を副
    iroquois = add_org("Haudenosaunee Confederacy (Iroquois)",
        alternate_names=[
            {"name": "Haudenosaunee", "lang": "en", "note": "self-designation, 'people of the longhouse'"},
            {"name": "Iroquois Confederacy", "lang": "en", "note": "exonym (外名)"},
            {"name": "Six Nations (after 1722)", "lang": "en"},
            {"name": "ホデノショニ連邦", "lang": "ja"},
            {"name": "イロコイ連邦", "lang": "ja", "note": "外名"},
        ],
        description="北米北東部 (現在のニューヨーク州・五大湖南岸〜カナダ) に存続する先住民連邦。"
                    "Mohawk, Oneida, Onondaga, Cayuga, Seneca の 5 nation で創設、"
                    "1722 年に Tuscarora を加え 6 nation 体制。Great Law of Peace (Kaianere'kó:wa) と "
                    "Grand Council (50 名の Hoyaneh / Sachems) による合議制ガバナンス。"
                    "母系社会で Clan Mother が Hoyaneh を選出・解任する権限を持つ。"
                    "創設年代は学説間で大きく分かれ、Haudenosaunee 自身および Mann & Fields (1997) は "
                    "1142 年 (日食) を採るのに対し、考古学・人類学の多数派は 1450-1600 年代を推定。"
                    "現代も自治政府として存続し、2026 年現在 Six Nations Reserve など複数の領域を管轄",
        geo_scope={"traditional_territory": "Haudenosaunee homeland (現 New York, Ontario, Quebec)",
                   "modern_reserves": ["Six Nations of the Grand River", "Akwesasne",
                                        "Onondaga Nation", "Tuscarora Nation", "Tonawanda Seneca",
                                        "Cattaraugus", "Allegany", "Oneida Nation"]},
        start_date=None,
        start_date_precision="unknown",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "founding_date_estimates": {
                "haudenosaunee_internal_and_mann_fields_1997": "1142 (solar eclipse 推定)",
                "western_archaeological_majority": "1450-1600 CE",
                "fenton_1998_synthesis": "「正確な日付は決定不能」と結論",
            },
            "founding_traditional": "Peacemaker (Deganawida) と Hiawatha による Five Nations の同盟形成",
            "constitutional_text": "Great Law of Peace / Kaianere'kó:wa (口承、後に Wampum belt で記録)",
            "council_size": 50,
            "council_title": "Hoyaneh / Sachem (50 chiefs)",
            "membership": ["Mohawk", "Oneida", "Onondaga", "Cayuga", "Seneca",
                            "Tuscarora (1722-)"],
            "governance_principles": ["consensus (decision by unanimity)",
                                       "matrilineal (Clan Mothers select Hoyaneh)",
                                       "seven generations principle"],
            "indigenous_data_sovereignty_note": "本レコードは外部学術文献に基づく描写。"
                                                  "内部統治・儀礼の詳細は外部研究に十全に表象できないため記述を制限している",
        },
        external_ids={"wikidata": "Q251655"})
    inserted.append(("organization", iroquois, "Haudenosaunee"))

    # Founding date は意図的に partial で記録 (単一日付主張を避ける)
    iroquois_date_claim = add_claim("organization", iroquois, "start_date", "partial",
        {"range_low": "1142",
         "range_high": "1660",
         "haudenosaunee_internal_position": "1142 (solar eclipse)",
         "western_majority_position": "1450-1600 CE",
         "interpretation": "確定不能の年代範囲。先住民の口承的時間と外部歴史学的時間の両立を尊重"},
        src_iroquois_fenton, 0.5,
        note="Indigenous Data Sovereignty 配慮: 単一日付を主張せず、"
             "内部・外部双方の見解を併記。partial 値で記録")

    iroquois_self_claim = add_claim("organization", iroquois, "founding_narrative", "present",
        {"reasoning": "Haudenosaunee Confederacy 公式自己記述として、Peacemaker と Hiawatha による "
                      "Five Nations 同盟形成という創設物語を内部権威として記録。"
                      "外部解釈と区別して保持する"},
        src_iroquois_self, 0.85,
        note="IDSov: 内部自己記述は内部権威として記録し、外部分析と分離して扱う")

    assign_form(iroquois, "historical_era", "tribe", is_primary=True, confidence=0.5,
                claim_id=add_claim("organization_form_assignment", iroquois, "form", "partial",
                    {"reasoning": "「氏族・部族」分類は外部視点の単純化。"
                                  "実態は連邦的政治体 (confederacy) であり、tribe 分類は不完全"},
                    src_iroquois_fenton, 0.5,
                    note="IDSov: 外部分類学への当てはめ自体が問題含み、partial で記録"))
    assign_form(iroquois, "historical_era", "chiefdom", confidence=0.4,
                claim_id=add_claim("organization_form_assignment", iroquois, "form", "partial",
                    {"reasoning": "Service の chiefdom 概念より複雑な構造を持つため、"
                                  "chiefdom 分類は近似的"},
                    src_iroquois_fenton, 0.4))
    assign_form(iroquois, "mintzberg_1989", "political", confidence=0.5,
                claim_id=add_claim("organization_form_assignment", iroquois, "form", "partial",
                    {"reasoning": "Mintzberg の political configuration は西洋組織を前提。"
                                  "完全な適用は時代錯誤・文化錯誤を伴う"},
                    src_iroquois_fenton, 0.5))

    # Activities — 外部観察可能な制度形態のみ記述、儀礼内容は記述しない
    act_iroquois_council = add_act(iroquois, "consensus_governance", domain="統治",
        description="Grand Council at Onondaga: 50 名の Hoyaneh による合議制決定。"
                    "Mohawk・Seneca が Older Brothers, Oneida・Cayuga・Tuscarora が Younger Brothers, "
                    "Onondaga が Firekeeper として全会一致を促す",
        scale={"council_seats": 50, "nations_represented": 6},
        orientation="exploitation",
        confidence=0.7,
        claim_id=add_claim("activity", "pending", "type", "present",
            {"reasoning": "外部学術文献で記述される制度の輪郭。詳細儀礼は本レコードでは扱わない"},
            src_iroquois_fenton, 0.7))

    act_iroquois_diplomacy = add_act(iroquois, "diaspora_diplomacy", domain="政治",
        description="17-18 世紀英仏蘭との条約外交、Wampum belt による条約記録 (Two Row Wampum 1613 など)",
        orientation="exploration",
        confidence=0.7)

    # Functions — 制度形態レベルのみ
    add_func(iroquois, "miller_18_decider",
             mechanism={"means": ["Grand Council (50 Hoyaneh)",
                                  "consensus (全会一致原則)",
                                  "Clan Mothers による Hoyaneh の選出・解任"]},
             activity_id=act_iroquois_council,
             confidence=0.7,
             claim_id=add_claim("function_record", "pending", "type", "present",
                 {"reasoning": "外部から観察可能な意思決定構造の概要"},
                 src_iroquois_fenton, 0.7))
    add_func(iroquois, "miller_17_memory",
             mechanism={"means": ["Wampum belts (口承記録の物質的補助)",
                                  "Faithkeepers (口承継承担当)"],
                        "note": "口承的伝達が中心。記録様式は外部の文書記録概念とは異なる"},
             confidence=0.6)
    add_func(iroquois, "vsm_s5_policy_identity",
             mechanism={"means": ["Great Law of Peace (Kaianere'kó:wa)",
                                  "Seven Generations 原則"]},
             confidence=0.7)
    add_func(iroquois, "miller_02_boundary",
             mechanism={"means": ["6 nation の領域確認、母系氏族 (clan) による帰属",
                                  "Adoption 制度 (敵対部族からの編入)"]},
             confidence=0.6)

    # Impact — direction は descriptive 中心 (価値判断を回避)
    add_imp(iroquois, "政治", "longstanding_consensus_governance",
            {"description": "数百年単位で機能する合議制連邦の存続例として、"
                            "比較政治学・組織研究で頻繁に参照"},
            "descriptive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"academic_field": "political science, organizational studies"},
            confidence=0.7,
            claim_id=add_claim("impact_record", "pending", "type", "present",
                {"reasoning": "descriptive direction で価値判断を回避"},
                src_iroquois_fenton, 0.7))

    add_imp(iroquois, "政治", "us_constitution_influence_thesis",
            {"description": "U.S. Concurrent Resolution H.Con.Res.331 (1988) は "
                            "Haudenosaunee の Great Law が U.S. 憲法に影響を与えたことを公式に認知。"
                            "ただし学術的には影響の規模・直接性に議論が継続",
             "us_resolution": "H.Con.Res.331 (100th Congress, 1988)"},
            "descriptive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"target": "U.S. constitutional thought"},
            confidence=0.5,
            claim_id=add_claim("impact_record", "pending", "type", "partial",
                {"reasoning": "影響説 (Influence Thesis) は学術的に争点。"
                              "Grinde & Johansen 1991 が肯定、Tooker 1988 が懐疑。partial で記録"},
                src_iroquois_fenton, 0.5))

    # Events — 創設は単一日付を持たないため event_date は記録せず precision=unknown
    e_iroquois_founding = add_event("founding",
        event_date=None, event_date_precision="unknown",
        description="Peacemaker (Deganawida) と Hiawatha による Five Nations 同盟形成、"
                    "Great Law of Peace の制定。年代は 1142-1660 の範囲で諸説あり",
        causes={"narrative": "5 nation 間の戦争を終わらせる平和創設物語"},
        outcomes={"new_org": "Haudenosaunee Confederacy",
                  "constitutional_text": "Great Law of Peace"},
        vsr_label="variation", confidence=0.5,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"reasoning": "創設年代は確定不能。event_date を null とし、precision を unknown で記録"},
            src_iroquois_fenton, 0.5,
            note="IDSov: 単一日付主張を避け、partial 値で記録"))
    link_eo(e_iroquois_founding, iroquois, "founder")

    e_iroquois_tuscarora = add_event("reform",
        event_date="1722-01-01", event_date_precision="year",
        description="Tuscarora が南部から移住し連邦に加盟、Five Nations から Six Nations へ",
        outcomes={"membership_change": "5 → 6 nations"},
        vsr_label="retention", confidence=0.85)
    link_eo(e_iroquois_tuscarora, iroquois, "transformed")

    # ============================================================
    # CASE 4: Linux Kernel Community (1991-)
    # ============================================================
    linux_kernel = add_org("Linux Kernel Community",
        alternate_names=[
            {"name": "Linux kernel developers", "lang": "en"},
            {"name": "LKML community", "lang": "en"},
            {"name": "Linux カーネルコミュニティ", "lang": "ja"},
        ],
        description="1991 年 8 月に Linus Torvalds が公開した Linux カーネルを継続的に開発する世界規模のオープンソース開発者集団。"
                    "正式法人を持たず、Linux Kernel Mailing List (LKML) と Git リポジトリを基盤に、"
                    "Linus Torvalds を Benevolent Dictator (BDFL) とし、約 100 名超の subsystem maintainer 階層、"
                    "数千名のコントリビューターを階層化した meritocratic 開発体。"
                    "2007 年設立の Linux Foundation は雇用・基盤提供を担うが、開発統治は community が独立に運営。"
                    "2025 年に Linux Kernel Continuity Document が起草され、Torvalds 不在時の Conclave による "
                    "後継選出プロトコルが整備された。",
        geo_scope={"type": "global_distributed",
                   "primary_communication": "Linux Kernel Mailing List (LKML)"},
        start_date="1991-08-25", start_date_precision="exact",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "founder": "Linus Torvalds",
            "governance_model": "Benevolent Dictator + Subsystem Maintainers",
            "primary_tools": ["Git (2005-)", "Linux Kernel Mailing List", "patchwork"],
            "succession_plan": "Linux Kernel Continuity Document (drafted 2025, Maintainer Summit Tokyo)",
            "release_cycle": "rc-based, ~9 weeks per major release",
            "annual_contributors_estimate": "4000+ developers per release",
        },
        external_ids={"wikidata": "Q14579"})
    inserted.append(("organization", linux_kernel, "Linux Kernel Community"))

    linux_claim = add_claim("organization", linux_kernel, "start_date", "present",
        {"date": "1991-08-25",
         "context": "Torvalds の comp.os.minix 投稿による Linux 公開アナウンスメント"},
        src_linux_torvalds_email, 0.95,
        note="原電子メールが現存する確定的日付")

    assign_form(linux_kernel, "historical_era", "platform", is_primary=True, confidence=0.7,
                claim_id=add_claim("organization_form_assignment", linux_kernel, "form", "present",
                    {"reasoning": "コードリポジトリと LKML が「開発者参加のためのプラットフォーム」を構成"},
                    src_linux_corbet, 0.7))
    assign_form(linux_kernel, "mintzberg_1989", "adhocracy", confidence=0.7,
                claim_id=add_claim("organization_form_assignment", linux_kernel, "form", "present",
                    {"reasoning": "プロジェクトベースの相互適応 + 専門家の自律性 + 技術的成果での評価"},
                    src_linux_raymond, 0.7))
    assign_form(linux_kernel, "mintzberg_1989", "professional_bureaucracy", confidence=0.55,
                claim_id=add_claim("organization_form_assignment", linux_kernel, "form", "partial",
                    {"reasoning": "subsystem maintainer 層の専門技能の標準化が支配的でもある"},
                    src_linux_corbet, 0.55))
    assign_form(linux_kernel, "laloux_2014", "teal", confidence=0.5,
                claim_id=add_claim("organization_form_assignment", linux_kernel, "form", "partial",
                    {"reasoning": "自己組織化的でフラットな部分があるが、BDFL モデルとの緊張あり。"
                                  "完全な teal とは言えない"},
                    src_linux_raymond, 0.5))

    # Activities
    act_linux_dev = add_act(linux_kernel, "open_source_development", domain="生産",
        description="Linux カーネルのソースコード開発。release candidate (rc) サイクルで約 9 週ごとにメジャーリリース。"
                    "patch を LKML に提出 → maintainer review → subsystem tree → Torvalds が main へ pull",
        outputs={"product": "Linux kernel",
                 "license": "GPL-2.0-only (コア)",
                 "release_cycle_weeks": 9},
        scale={"contributors_per_release_estimate": 4000,
               "lines_of_code_2024": "30M+ LOC"},
        orientation="mixed",
        valid_from="1991-08-25", confidence=0.9)

    act_linux_review = add_act(linux_kernel, "patch_review", domain="統治",
        description="LKML 上の patch review が技術的標準化と社会化の中核。"
                    "Reviewed-by: / Acked-by: / Signed-off-by: タグでアトリビューション",
        orientation="exploitation",
        valid_from="1991-08-25", confidence=0.9)

    # Functions
    add_func(linux_kernel, "miller_18_decider",
             mechanism={"means": ["Linus Torvalds = final merge authority for mainline",
                                  "subsystem maintainers (~100+) for sub-trees",
                                  "LKML consensus by technical merit"],
                        "succession": "Linux Kernel Continuity Document (2025) + TAB + Maintainer Summit Conclave"},
             confidence=0.9)
    add_func(linux_kernel, "miller_13_channel_and_net",
             mechanism={"means": ["Linux Kernel Mailing List (LKML)",
                                  "Git distributed VCS (Torvalds 開発, 2005-)",
                                  "patchwork / lore.kernel.org"]},
             activity_id=act_linux_review, confidence=0.95)
    add_func(linux_kernel, "miller_17_memory",
             mechanism={"means": ["Git history (cryptographic immutability)",
                                  "lore.kernel.org メールアーカイブ"]},
             confidence=0.95)
    add_func(linux_kernel, "miller_15_decoder",
             mechanism={"means": ["coding style (Documentation/process/coding-style.rst)",
                                  "checkpatch.pl による静的検査"]},
             confidence=0.85)
    add_func(linux_kernel, "miller_02_boundary",
             mechanism={"means": ["Signed-off-by 法的署名 (DCO)",
                                  "メイン tree への merge は Torvalds の特権"],
                        "note": "boundary は法的でなく社会的・技術的"},
             confidence=0.85)
    add_func(linux_kernel, "vsm_s5_policy_identity",
             mechanism={"means": ["Code of Conduct (2018-)",
                                  "Documentation/process/ ディレクトリ",
                                  "GPL-2.0 ライセンス"]},
             confidence=0.85)

    # Impact
    add_imp(linux_kernel, "技術", "dominant_kernel_software",
            {"description": "サーバー、Android、組込み、HPC、クラウド基盤で支配的なカーネル"},
            "descriptive", "long_term",
            evaluation_method="comparison",
            affected_scope={"market": "global compute infrastructure"},
            confidence=0.95)

    add_imp(linux_kernel, "技術", "open_source_governance_template",
            {"description": "Benevolent Dictator + Maintainers モデルの参照実装。"
                            "Git の発明 (2005) も派生効果としてソフトウェア工学を変革"},
            "positive", "intergenerational",
            evaluation_method="historical_interpretation",
            confidence=0.85)

    # Events
    e_linux_announce = add_event("founding",
        event_date="1991-08-25", event_date_precision="exact",
        description="Linus Torvalds が comp.os.minix newsgroup で Linux カーネルを公開アナウンス "
                    "('What would you like to see most in minix?')",
        participants=["Linus Torvalds"],
        outcomes={"new_org": "Linux Kernel Community"},
        vsr_label="variation", confidence=0.95)
    link_eo(e_linux_announce, linux_kernel, "founder")

    e_linux_git = add_event("platform_shift",
        event_date="2005-04-07", event_date_precision="exact",
        description="Linux 開発で Git が初使用 (BitKeeper ライセンス問題から自作)",
        causes={"trigger": "BitKeeper ライセンス紛争"},
        outcomes={"new_tool": "Git distributed VCS",
                  "side_effect": "後の GitHub/GitLab エコシステム"},
        vsr_label="variation", confidence=0.9)
    link_eo(e_linux_git, linux_kernel, "transformed")

    e_linux_succession = add_event("governance_change",
        event_date="2025-10-01", event_date_precision="month",
        description="Linux Kernel Maintainer Summit (Tokyo) で Linux Kernel Continuity Document が起草。"
                    "Torvalds 不在時の Conclave (TAB + Maintainer Summit 出席者) による後継プロトコル整備",
        causes={"motivation": "「getting grey and old」コミュニティの世代交代懸念"},
        outcomes={"new_governance": "Conclave succession protocol"},
        vsr_label="retention", confidence=0.85)
    link_eo(e_linux_succession, linux_kernel, "transformed")

    # ============================================================
    # CASE 5: Anonymous (2003-)
    # ============================================================
    anonymous = add_org("Anonymous",
        alternate_names=[
            {"name": "Anonymous collective", "lang": "en"},
            {"name": "アノニマス", "lang": "ja"},
        ],
        description="2003 年に画像掲示板 4chan の 'Anonymous' 既定ユーザー名を起点に発生した、"
                    "リーダーレス・分散・無会員の集合的識別子。2008 年の Project Chanology (Scientology 教会への抗議) で "
                    "ハクティビズム的政治運動へ転化。Guy Fawkes mask (V for Vendetta 由来) を象徴に、"
                    "DDoS、leak、メディア介入を行使。会員資格・指揮系統・集権意思決定が原理的に存在せず、"
                    "誰でも 'Anonymous' を名乗って行動可能。これにより組織研究では「リーダーレス・"
                    "leaderless resistance」「swarm organization」の代表的実例として扱われる。",
        geo_scope={"type": "global_online", "primary_loci": ["IRC (AnonOps)", "4chan", "Twitter", "Telegram"]},
        start_date="2003-01-01", start_date_precision="year",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "origin": "4chan 'Anonymous' default username (2003)",
            "transition_to_activism": "Project Chanology (2008-01-21~)",
            "symbol": "Guy Fawkes mask (V for Vendetta, 2006 film)",
            "membership_concept": "no formal membership; identifier-based participation",
            "leaderless": True,
            "key_operations": ["Project Chanology (2008)", "Operation Payback (2010, WikiLeaks 防衛)",
                                "OpTunisia / Arab Spring 支援 (2010-11)", "OpRussia (2022-)"],
        },
        external_ids={"wikidata": "Q1364"})
    inserted.append(("organization", anonymous, "Anonymous"))

    anon_claim = add_claim("organization", anonymous, "start_date", "partial",
        {"year": 2003,
         "context": "4chan の既定ユーザー名から派生したインフォーマルな起点"},
        src_anon_coleman, 0.7,
        note="正式設立日は存在しない。2003 年は 4chan 開設および "
             "Anonymous 名義での初期協調行動が発生した年として近似値で記録")

    assign_form(anonymous, "historical_era", "platform", is_primary=True, confidence=0.6,
                claim_id=add_claim("organization_form_assignment", anonymous, "form", "partial",
                    {"reasoning": "プラットフォーム的な開放性と参加の流動性が支配的だが、"
                                  "プラットフォーム所有者は存在しない。「nameless platform」と暫定整理"},
                    src_anon_coleman, 0.6))
    assign_form(anonymous, "mintzberg_1989", "adhocracy", confidence=0.55,
                claim_id=add_claim("organization_form_assignment", anonymous, "form", "partial",
                    {"reasoning": "プロジェクトベースの相互適応性は adhocracy 的だが、"
                                  "Mintzberg は組織境界の存在を前提しており、Anonymous には適用限界"},
                    src_anon_coleman, 0.55))
    assign_form(anonymous, "laloux_2014", "teal", confidence=0.4,
                claim_id=add_claim("organization_form_assignment", anonymous, "form", "partial",
                    {"reasoning": "自己組織化的だが、目的の不安定性 (lulz から activism へ揺らぐ) は "
                                  "Laloux の teal 像と異なる"},
                    src_anon_coleman, 0.4))

    # Activities
    act_anon_op = add_act(anonymous, "decentralized_collective_action", domain="政治",
        description="ad-hoc な 'Operation' (Op) を IRC 上で発議、自律参加者が DDoS, leak, "
                    "ストリート抗議を実行",
        outputs={"actions": ["DDoS attacks", "leaks", "street protests with masks",
                              "viral video releases"]},
        orientation="exploration", valid_from="2008-01-21", confidence=0.8)

    act_anon_meme = add_act(anonymous, "memetic_warfare", domain="文化",
        description="ミームと象徴 (Guy Fawkes mask, 'We are Legion') の流通による参加動員",
        orientation="exploration", valid_from="2008-01-21", confidence=0.7)

    # Functions
    add_func(anonymous, "miller_18_decider",
             mechanism={"means": ["IRC channel (AnonOps 等) での即興的合意",
                                  "誰でも Op を提案可能、参加・離脱は自由"],
                        "note": "意思決定の中央点は存在しない。決定は「行動した者の行動」によって事後的に確定"},
             confidence=0.6,
             claim_id=add_claim("function_record", "pending", "type", "partial",
                 {"reasoning": "decider が分散不在であることが定義的特徴"},
                 src_anon_coleman, 0.6))
    add_func(anonymous, "vsm_s5_policy_identity",
             mechanism={"means": ["Guy Fawkes mask",
                                  "'We are Legion. We do not forgive. We do not forget. Expect us.' (信条句)",
                                  "anti-authoritarianism, anti-censorship"],
                        "note": "policy は流動的で内部矛盾を許容"},
             confidence=0.7)
    add_func(anonymous, "miller_19_encoder",
             mechanism={"means": ["YouTube アナウンスメント動画 (mask + voice modulation)",
                                  "ミーム流通", "ハッシュタグ"]},
             activity_id=act_anon_meme, confidence=0.75)
    add_func(anonymous, "miller_02_boundary",
             mechanism={"means": ["なし — 'Anonymous' を名乗ることが参加",
                                  "事後的な相互承認のみ"],
                        "note": "境界の意図的な不在が組織原理"},
             confidence=0.7)

    # Impact
    add_imp(anonymous, "政治", "leaderless_movement_template",
            {"description": "リーダーレス・分散運動の組織モデルとして、"
                            "後の Occupy (2011)、香港抗議 (2019)、BLM 系列に参照される"},
            "descriptive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"successor_movements": ["Occupy (2011)", "Hong Kong 2019",
                                                     "Be Water 戦術系列"]},
            confidence=0.7)

    add_imp(anonymous, "政治", "scientology_pressure",
            {"description": "Project Chanology (2008) は Church of Scientology に対する持続的国際抗議の起点となり、"
                            "教会の社会的信用に長期的圧力を生成"},
            "descriptive", "long_term",
            confidence=0.7)

    add_imp(anonymous, "技術", "ddos_normalization_concern",
            {"description": "DDoS を政治抗議手段として正規化したことの倫理的・法的批判が継続。"
                            "Operation Payback (2010) で参加者多数が法的訴追を受けた"},
            "mixed", "long_term",
            confidence=0.7)

    # Events
    e_anon_origin = add_event("founding",
        event_date="2003-10-01", event_date_precision="year",
        description="4chan 開設 (2003-10-01) を契機に 'Anonymous' 既定ユーザー名から集合的識別子が発生",
        causes={"platform": "4chan founded by Christopher Poole (moot)"},
        outcomes={"new_collective_identifier": "Anonymous"},
        vsr_label="variation", confidence=0.7,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"reasoning": "「設立」概念が Anonymous には適用しにくく、年単位で近似"},
            src_anon_coleman, 0.7))
    link_eo(e_anon_origin, anonymous, "founder")

    e_anon_chanology = add_event("reform",
        event_date="2008-01-21", event_date_precision="exact",
        description="Project Chanology 開始: Tom Cruise の Scientology 動画削除工作への抗議を契機に、"
                    "Anonymous がトロール集団からハクティビズム運動へ転化",
        causes={"trigger": "Church of Scientology の動画削除要求"},
        outcomes={"transformation": "trolls → hacktivism collective",
                  "tactical_innovation": "DDoS + 街頭抗議 + Guy Fawkes mask"},
        vsr_label="variation", confidence=0.9)
    link_eo(e_anon_chanology, anonymous, "transformed")

    # ============================================================
    # RELATIONS: 既存ケースとの接続
    # ============================================================
    mondragon = find_org_exact("Mondragón Corporación Cooperativa (MCC)")
    grameen = find_org_exact("Grameen Bank")
    wikimedia = find_org_exact("Wikimedia Foundation")
    linux_foundation = find_org_exact("Linux Foundation")

    # SEWA → Mondragón (mimetic, 協同組合連帯モデル比較)
    if mondragon:
        rel_sewa_mondragon = add_relation(sewa, mondragon, "mimetic_isomorphism",
            valid_from="1992-01-01",
            relation_attributes={
                "transfer": "協同組合連邦運営 (federation of cooperatives) のモデル参照",
                "direction": "SEWA Cooperative Federation (1992-) は Mondragón モデルを国際比較研究で参照",
                "asymmetry": "SEWA は women's informal sector に特化、Mondragón は industrial worker"},
            strength=0.4, strength_basis="documented_comparative_studies",
            confidence=0.5,
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "比較研究での参照関係。直接的影響を強くは主張しない"},
                src_sewa_bhatt, 0.5,
                note="協同組合運動内での mimetic 関係。directが薄い"))

    # SEWA → Grameen (mimetic, 1974 SEWA Bank が 1983 Grameen に先行)
    if grameen:
        rel_sewa_grameen = add_relation(sewa, grameen, "mimetic_isomorphism",
            valid_from="1983-10-02",
            relation_attributes={
                "transfer": "女性向けマイクロファイナンスの先例として SEWA Bank (1974) が Grameen Bank (1983) に先行",
                "structural_contrast": "SEWA = 貯蓄主導型 (savings-led), Grameen = 信用主導型 (credit-led)",
                "direction": "SEWA → Grameen, ただし完全な制度継承ではなく時代的並行発展"},
            strength=0.45, strength_basis="documented_chronological_priority",
            confidence=0.55,
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "SEWA Bank が女性協同組合銀行として 9 年先行する事実は確立。"
                              "ただし Grameen 創設者 Yunus が SEWA を直接モデル化したという "
                              "強い一次史料は限定的"},
                src_sewa_bhatt, 0.55))

    # Iroquois → Wikimedia Foundation (normative_pressure, 合意形成規範の引用関係)
    if wikimedia:
        rel_iroquois_wiki = add_relation(iroquois, wikimedia, "normative_pressure",
            valid_from="2001-01-15",
            relation_attributes={
                "transfer": "合意形成 (consensus decision-making) 規範の参照関係",
                "direction": "Wikipedia コミュニティの consensus 規範議論で "
                              "Haudenosaunee Grand Council が引用される事例あり",
                "caveat": "直接の制度継承ではなく規範的参照。"
                          "Indigenous data sovereignty の観点から、参照関係は記述的に留める"},
            strength=0.2, strength_basis="incidental_normative_reference",
            confidence=0.4,
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "Wikipedia community で Haudenosaunee 合議制を参照する文書はあるが、"
                              "制度設計の直接源泉ではない。partial で弱い関係として記録"},
                src_iroquois_fenton, 0.4,
                note="IDSov 配慮: 関係を過剰主張しない"))

    # Linux Kernel Community → Linux Foundation (parent / financial host)
    if linux_foundation:
        rel_linux_lf = add_relation(linux_kernel, linux_foundation, "subsidiary",
            valid_from="2007-01-01",
            relation_attributes={
                "structure": "Linux Foundation は Linux Kernel Community の上流に置かれた "
                              "501(c)(6) 業界団体。Torvalds と一部 maintainer を雇用、"
                              "インフラを提供。ただし開発統治は community 独立",
                "asymmetry": "財務・雇用は LF, 開発意思決定は community",
                "directionality_note": "subsidiary の方向は逆解釈可能だが、"
                                        "本記録では community を母体、LF を後発設立の財団として記述"},
            strength=0.7, strength_basis="employment_and_infrastructure_dependency",
            confidence=0.85,
            claim_id=add_claim("relation", "pending", "type", "present",
                {"reasoning": "LF 設立 (2007) 時点で Kernel Community は既に 16 年存在。"
                              "LF は community を hosting する後発財団"},
                src_linux_corbet, 0.85,
                note="厳密な subsidiary ではなく hosting 関係だが、"
                     "relation_type 制約から subsidiary を選択"))

    # BPP → Anonymous (mimetic_isomorphism、リーダー型 vs リーダーレス対照ペア)
    rel_bpp_anon = add_relation(bpp, anonymous, "mimetic_isomorphism",
        valid_from="2003-10-01",
        relation_attributes={
            "transfer": "抗議的・反体制的「集合的アイデンティティ運動」という形式の継承",
            "structural_contrast": "BPP = リーダー型・カリスマ的中央権威・Ten-Point Program、"
                                    "Anonymous = リーダーレス・無綱領・参加識別子のみ",
            "comparative_value": "「組織を持つ抵抗 vs 組織を持たない抵抗」のコントラスト・ペア",
            "direction": "歴史的後続関係 (BPP 1966 → Anonymous 2003) としての形式進化",
            "no_direct_succession": "直接の人的・制度的継承はない。組織形態論上の対比として記録"},
        strength=0.2, strength_basis="formal_contrast_only",
        confidence=0.4,
        claim_id=add_claim("relation", "pending", "type", "partial",
            {"reasoning": "直接継承ではなく、組織形態論的な対照ペア。"
                          "影響史を強くは主張せず、形式進化の比較対象として記録"},
            src_anon_coleman, 0.4,
            note="弱い mimetic 関係として記録、主目的は対照分析の参照点"))

    conn.commit()

    # =========== Verification ===========
    org_ids = (bpp, sewa, iroquois, linux_kernel, anonymous)
    placeholders = ",".join("?" * len(org_ids))

    print("\n=== Stream O: marginal/movement/indigenous 5 cases ===")

    cur.execute(f"SELECT COUNT(*) FROM organization WHERE organization_id IN ({placeholders})", org_ids)
    print(f"organizations created      : {cur.fetchone()[0]}")
    cur.execute(f"SELECT COUNT(*) FROM organization_form_assignment WHERE organization_id IN ({placeholders})", org_ids)
    print(f"form assignments           : {cur.fetchone()[0]}")
    cur.execute(f"SELECT COUNT(*) FROM activity WHERE organization_id IN ({placeholders})", org_ids)
    print(f"activities                 : {cur.fetchone()[0]}")
    cur.execute(f"SELECT COUNT(*) FROM function_record WHERE organization_id IN ({placeholders})", org_ids)
    print(f"function_records           : {cur.fetchone()[0]}")
    cur.execute(f"SELECT COUNT(*) FROM impact_record WHERE organization_id IN ({placeholders})", org_ids)
    print(f"impact_records             : {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(DISTINCT e.event_id) FROM event e "
        "JOIN event_organization eo ON eo.event_id = e.event_id "
        f"WHERE eo.organization_id IN ({placeholders})", org_ids)
    print(f"events linked to new orgs  : {cur.fetchone()[0]}")
    cur.execute(
        f"SELECT COUNT(*) FROM relation WHERE source_organization_id IN ({placeholders}) "
        f"OR target_organization_id IN ({placeholders})",
        org_ids + org_ids)
    print(f"relations involving new orgs: {cur.fetchone()[0]}")

    print("\n--- inserted organizations ---")
    for et, eid, name in inserted:
        print(f"  {et:14s}  {eid[:12]}...  {name}")

    print("\n--- relation summary ---")
    cur.execute(
        f"SELECT r.relation_type, o1.canonical_name, o2.canonical_name, r.confidence "
        f"FROM relation r "
        f"JOIN organization o1 ON o1.organization_id = r.source_organization_id "
        f"JOIN organization o2 ON o2.organization_id = r.target_organization_id "
        f"WHERE r.source_organization_id IN ({placeholders}) "
        f"OR r.target_organization_id IN ({placeholders})",
        org_ids + org_ids)
    for rt, src, tgt, conf in cur.fetchall():
        print(f"  {rt:25s} {src[:30]:30s} -> {tgt[:30]:30s}  conf={conf}")

    cur.execute("SELECT COUNT(*) FROM organization")
    print(f"\nTotal organizations in DB now: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claim")
    print(f"Total claims in DB now       : {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM source")
    print(f"Total sources in DB now      : {cur.fetchone()[0]}")

    conn.close()


if __name__ == "__main__":
    main()
