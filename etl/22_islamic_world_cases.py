#!/usr/bin/env python3
"""イスラム文明圏 5 ケース完全注釈

ケース:
  1. アル・アズハル (Al-Azhar, 970/972-) — 世界最古級の継続的教育機関 (モスク+大学)
  2. バイト・アル=ヒクマ (Bayt al-Hikma / House of Wisdom, c.786-1258) — アッバース朝翻訳機関
  3. オスマン・ティマール制 (Ottoman timar, 14c-1831) — 軍事封建的徴税権ネットワーク
  4. ナクシュバンディー教団 (Naqshbandi tariqa, c.1380-) — スンニ派最大級スーフィー教団
  5. スレイマニエ・キュリエ (Süleymaniye Külliyesi, 1557-) — モスク+教育+病院+救貧の永久ワクフ複合体

既存 18 ケース (西欧+日本+一部非西洋) との比較で「イスラム文明圏組織が薄い」を解消。
helper パターンは etl/04_representative_cases.py を踏襲。

文献 (実在確認済み):
  - Lapidus, I.M. (2014) A History of Islamic Societies (3rd ed., Cambridge UP)
  - Hodgson, M.G.S. (1974) The Venture of Islam (3 vols., Univ of Chicago)
  - İnalcık, H. (1973) The Ottoman Empire: The Classical Age 1300-1600
  - İnalcık, H. & Quataert, D. (1994) An Economic and Social History of the Ottoman Empire
  - Trimingham, J.S. (1971) The Sufi Orders in Islam (Oxford UP)
  - Necipoğlu, G. (2005) The Age of Sinan: Architectural Culture in the Ottoman Empire
  - Gutas, D. (1998) Greek Thought, Arabic Culture (Routledge)

Relations (既存ケースとの接続):
  - Bayt al-Hikma → Bologna (knowledge_transfer; 翻訳経由のギリシア・アラビア科学伝播)
  - Al-Azhar ↔ ベネディクト会 (mimetic_isomorphism, no_direct_contact;
                                 並行進化的な永続教育宗教機関)
  - Ottoman timar → Mughal mansabdar (knowledge_transfer; 軍事-行政制度の継承)
  - Süleymaniye waqf → Mondragón (parallel; 長期 endowment governance の比較)
  - Naqshbandi → 比叡山 (parallel; 神秘主義系譜伝授組織)
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

    inserted = []

    # ----- helpers (04 パターン踏襲) -----
    def get_form_id(taxonomy, code):
        row = cur.execute(
            "SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
            (taxonomy, code),
        ).fetchone()
        return row[0] if row else None

    def find_org(name_like):
        row = cur.execute(
            "SELECT organization_id FROM organization WHERE canonical_name LIKE ? LIMIT 1",
            (name_like,),
        ).fetchone()
        return row[0] if row else None

    def add_source(stype, title, **kw):
        sid = uid()
        cur.execute(
            """INSERT INTO source (source_id, source_type, title, authors, publication_date,
                publisher, locator, accessed_at, reliability_score, reliability_basis,
                license, redistribution)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sid, stype, title,
             json.dumps(kw.get("authors")) if kw.get("authors") else None,
             kw.get("publication_date"),
             kw.get("publisher"),
             json.dumps(kw.get("locator")) if kw.get("locator") else None,
             kw.get("accessed_at"),
             kw.get("reliability_score"),
             kw.get("reliability_basis"),
             kw.get("license"),
             kw.get("redistribution", "attribution_required"),
            ),
        )
        return sid

    def add_claim(entity_type, entity_id, field_path, value_kind, claim_value,
                  source_id, confidence, recorded_by="claude_code_v1", note=None):
        cid = uid()
        cur.execute(
            """INSERT INTO claim (claim_id, entity_type, entity_id, field_path, value_kind,
                claim_value, source_id, confidence, recorded_by, interpretation_note)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (cid, entity_type, entity_id, field_path, value_kind,
             json.dumps(claim_value, ensure_ascii=False) if claim_value is not None else None,
             source_id, confidence, recorded_by, note),
        )
        return cid

    def add_org(canonical_name, **kw):
        oid = uid()
        cur.execute(
            """INSERT INTO organization (organization_id, canonical_name, alternate_names,
                description, primary_form_id, geo_scope, start_date, start_date_precision,
                end_date, end_date_precision, status, attributes, external_ids)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (oid, canonical_name,
             json.dumps(kw.get("alternate_names"), ensure_ascii=False) if kw.get("alternate_names") else None,
             kw.get("description"),
             kw.get("primary_form_id"),
             json.dumps(kw.get("geo_scope"), ensure_ascii=False) if kw.get("geo_scope") else None,
             kw.get("start_date"), kw.get("start_date_precision"),
             kw.get("end_date"), kw.get("end_date_precision"),
             kw.get("status", "unknown"),
             json.dumps(kw.get("attributes"), ensure_ascii=False) if kw.get("attributes") else None,
             json.dumps(kw.get("external_ids"), ensure_ascii=False) if kw.get("external_ids") else None,
            ),
        )
        return oid

    def assign_form(org_id, taxonomy, code, is_primary=False, valid_from=None, valid_to=None,
                    confidence=0.8, claim_id=None):
        form_id = get_form_id(taxonomy, code)
        if not form_id:
            print(f"  [warn] missing form {taxonomy}/{code} — skipped for {org_id[:8]}")
            return None
        aid = uid()
        cur.execute(
            """INSERT INTO organization_form_assignment
                (assignment_id, organization_id, form_id, valid_from, valid_to,
                 is_primary, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (aid, org_id, form_id, valid_from, valid_to,
             1 if is_primary else 0, confidence, claim_id),
        )
        if is_primary:
            cur.execute("UPDATE organization SET primary_form_id=? WHERE organization_id=?",
                        (form_id, org_id))
        return aid

    def add_act(org_id, atype, **kw):
        aid = uid()
        cur.execute(
            """INSERT INTO activity (activity_id, organization_id, activity_type, domain,
                description, inputs, outputs, scale, orientation, valid_from, valid_to,
                confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (aid, org_id, atype, kw.get("domain"),
             kw.get("description"),
             json.dumps(kw.get("inputs"), ensure_ascii=False) if kw.get("inputs") else None,
             json.dumps(kw.get("outputs"), ensure_ascii=False) if kw.get("outputs") else None,
             json.dumps(kw.get("scale"), ensure_ascii=False) if kw.get("scale") else None,
             kw.get("orientation", "unspecified"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id"),
            ),
        )
        return aid

    def add_func(org_id, func_type_id, mechanism=None, activity_id=None,
                 valid_from=None, valid_to=None, confidence=None, claim_id=None):
        fid = uid()
        cur.execute(
            """INSERT INTO function_record (function_id, organization_id, function_type_id,
                mechanism, activity_id, valid_from, valid_to, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (fid, org_id, func_type_id,
             json.dumps(mechanism, ensure_ascii=False) if mechanism else None,
             activity_id, valid_from, valid_to, confidence, claim_id),
        )
        return fid

    def add_imp(org_id, domain, metric_name, metric_value, direction, time_horizon,
                evaluation_method=None, valid_from=None, valid_to=None,
                confidence=None, claim_id=None, affected_scope=None):
        iid = uid()
        cur.execute(
            """INSERT INTO impact_record (impact_id, organization_id, impact_domain,
                metric_name, metric_value, direction, time_horizon, affected_scope,
                evaluation_method, valid_from, valid_to, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, org_id, domain, metric_name,
             json.dumps(metric_value, ensure_ascii=False),
             direction, time_horizon,
             json.dumps(affected_scope, ensure_ascii=False) if affected_scope else None,
             evaluation_method, valid_from, valid_to, confidence, claim_id),
        )
        return iid

    def add_relation(src, tgt, rtype, **kw):
        rid = uid()
        cur.execute(
            """INSERT INTO relation (relation_id, source_organization_id, target_organization_id,
                relation_type, directionality, valid_from, valid_to, strength, strength_basis,
                relation_attributes, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rid, src, tgt, rtype, kw.get("directionality", "directed"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("strength"), kw.get("strength_basis"),
             json.dumps(kw.get("relation_attributes"), ensure_ascii=False) if kw.get("relation_attributes") else None,
             kw.get("confidence"), kw.get("claim_id")),
        )
        return rid

    def add_event(etype, **kw):
        eid = uid()
        cur.execute(
            """INSERT INTO event (event_id, event_type, event_date, event_date_precision,
                description, participants, causes, outcomes, location,
                dissolution_cause, vsr_label, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, etype, kw.get("event_date"),
             kw.get("event_date_precision", "unknown"),
             kw.get("description"),
             json.dumps(kw.get("participants"), ensure_ascii=False) if kw.get("participants") else None,
             json.dumps(kw.get("causes"), ensure_ascii=False) if kw.get("causes") else None,
             json.dumps(kw.get("outcomes"), ensure_ascii=False) if kw.get("outcomes") else None,
             json.dumps(kw.get("location"), ensure_ascii=False) if kw.get("location") else None,
             kw.get("dissolution_cause"), kw.get("vsr_label"),
             kw.get("confidence"), kw.get("claim_id")),
        )
        return eid

    def link_event_org(event_id, org_id, role):
        cur.execute(
            """INSERT OR IGNORE INTO event_organization
                (event_organization_id, event_id, organization_id, role)
               VALUES (?,?,?,?)""",
            (uid(), event_id, org_id, role),
        )

    # ============================================================
    # Sources (実在文献)
    # ============================================================
    src_lapidus = add_source("secondary_literature",
        "Lapidus, I.M. (2014) A History of Islamic Societies (3rd ed.)",
        authors=["Ira M. Lapidus"], publication_date="2014-01-01",
        publisher="Cambridge University Press",
        reliability_score=0.9,
        reliability_basis="イスラム社会史の標準教科書、3版を重ね広範に参照される")

    src_hodgson = add_source("secondary_literature",
        "Hodgson, M.G.S. (1974) The Venture of Islam (3 vols.)",
        authors=["Marshall G.S. Hodgson"], publication_date="1974-01-01",
        publisher="University of Chicago Press",
        reliability_score=0.9,
        reliability_basis="イスラム文明史の三部作、文明論的枠組みの古典")

    src_inalcik_ottoman = add_source("secondary_literature",
        "İnalcık, H. (1973) The Ottoman Empire: The Classical Age 1300-1600",
        authors=["Halil İnalcık"], publication_date="1973-01-01",
        publisher="Weidenfeld & Nicolson",
        reliability_score=0.95,
        reliability_basis="オスマン古典期研究の決定版、トルコ国立公文書館一次史料に依拠")

    src_inalcik_econ = add_source("secondary_literature",
        "İnalcık, H. & Quataert, D. (eds, 1994) An Economic and Social History of the Ottoman Empire",
        authors=["Halil İnalcık", "Donald Quataert"], publication_date="1994-01-01",
        publisher="Cambridge University Press",
        reliability_score=0.9,
        reliability_basis="ティマール統計・徴税台帳に基づく社会経済史")

    src_trimingham = add_source("secondary_literature",
        "Trimingham, J.S. (1971) The Sufi Orders in Islam",
        authors=["J. Spencer Trimingham"], publication_date="1971-01-01",
        publisher="Oxford University Press",
        reliability_score=0.85,
        reliability_basis="スーフィー教団の制度史としてもっとも参照される古典")

    src_necipoglu = add_source("secondary_literature",
        "Necipoğlu, G. (2005) The Age of Sinan: Architectural Culture in the Ottoman Empire",
        authors=["Gülru Necipoğlu"], publication_date="2005-01-01",
        publisher="Reaktion Books",
        reliability_score=0.95,
        reliability_basis="スレイマニエの waqfiyya 文書を含む建築・社会史の総合研究")

    src_gutas = add_source("secondary_literature",
        "Gutas, D. (1998) Greek Thought, Arabic Culture",
        authors=["Dimitri Gutas"], publication_date="1998-01-01",
        publisher="Routledge",
        reliability_score=0.9,
        reliability_basis="バイト・アル=ヒクマ翻訳運動の最新研究、政治経済的文脈を強調")

    src_alazhar_wp = add_source("secondary_literature",
        "Wikipedia: Al-Azhar University",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Al-Azhar_University"},
        accessed_at="2026-05-02",
        reliability_score=0.55,
        reliability_basis="二次情報源、Britannica や学術文献と相互チェックが必要",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_houseofwisdom_wp = add_source("secondary_literature",
        "Wikipedia: House of Wisdom",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/House_of_Wisdom"},
        accessed_at="2026-05-02",
        reliability_score=0.5,
        reliability_basis="近年研究では Bayt al-Hikma の'institution'像に懐疑的見解 (Gutas) — Wikipedia は古いナラティブを残す",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_naqshbandi_wp = add_source("secondary_literature",
        "Wikipedia: Naqshbandi Order / Baha al-Din Naqshband",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Naqshbandi_Order"},
        accessed_at="2026-05-02",
        reliability_score=0.55,
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_suleymaniye_wp = add_source("secondary_literature",
        "Wikipedia: Süleymaniye Mosque",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/S%C3%BCleymaniye_Mosque"},
        accessed_at="2026-05-02",
        reliability_score=0.6,
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_timar_wp = add_source("secondary_literature",
        "Wikipedia: Timar / Sipahi (cross-checked with İnalcık)",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Timar"},
        accessed_at="2026-05-02",
        reliability_score=0.55,
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    # 既存ターゲット組織を取得
    bologna_id     = find_org("ボローニャ大学%")
    benedictines_id = find_org("ベネディクト会%")
    mansabdar_id   = find_org("ムガル朝マンサブダール%")
    mondragon_id   = find_org("Mondrag%")
    enryakuji_id   = find_org("比叡山%")

    print(f"target lookup: bologna={bologna_id and bologna_id[:8]}, "
          f"benedictines={benedictines_id and benedictines_id[:8]}, "
          f"mansabdar={mansabdar_id and mansabdar_id[:8]}, "
          f"mondragon={mondragon_id and mondragon_id[:8]}, "
          f"enryakuji={enryakuji_id and enryakuji_id[:8]}")

    # ============================================================
    # CASE 19: Al-Azhar (970/972-)
    # ============================================================
    azhar = add_org("アル・アズハル (Al-Azhar Mosque & University)",
        alternate_names=[
            {"name": "al-Jāmiʿ al-Azhar", "lang": "ar"},
            {"name": "Al-Azhar University", "lang": "en"},
            {"name": "ジャーミア・アズハル", "lang": "ja"},
        ],
        description=(
            "970 年 (建造開始) -972 年 (開設) にファーティマ朝のジャウハル・シキッリーが "
            "新都カイロに建立したモスクを起源とする。当初はシーア派 (イスマーイール派) の宣布拠点だが、"
            "1171 年サラディンによるアイユーブ朝樹立後にスンニ派の中心へ転換、12c 末以降には"
            "ジャーミア (大学) としての教育機能が拡張。マムルーク・オスマン期を通じて "
            "イスラム法学・神学の最高権威機関となり、現在も継続稼働。1961 年法 (ナーセル改革) で"
            "近代大学としてイスラム諸学+世俗諸学を併設、世界最古級の継続教育機関の一つ。"
        ),
        geo_scope={"hq": "Cairo, Egypt", "spread": "global Sunni Islamic education network"},
        start_date="0972-06-24", start_date_precision="exact",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={"founder": "Jawhar al-Siqilli (Fatimid commander, under Caliph al-Mu'izz)",
                    "longevity_years": 1054,
                    "innovations": ["継続的イジャーザ (修了証) 制度", "ハラカ (学習サークル)",
                                    "waqf 永久基金で教師俸給維持"],
                    "shift": "Shia (Fatimid) → Sunni (Ayyubid 1171)"},
        external_ids={"wikidata": "Q190120"})
    inserted.append(("organization", azhar, "Al-Azhar"))

    azhar_claim = add_claim("organization", azhar, "start_date", "partial",
        {"date": "972-06-24", "context": "建造開始 970 年、開設 972 年。Lapidus と Britannica で確認"},
        src_lapidus, 0.9,
        note="教育機関としての確立は 12c 末以降。'大学'創立年と単純に同視できない (Makdisi 議論)")
    assign_form(azhar, "historical_era", "monastery", is_primary=False,
                confidence=0.5,
                claim_id=add_claim("organization_form_assignment", azhar, "form", "partial",
                    {"reasoning": "monastery 概念とモスク=マドラサ=ワクフ複合体は機能的に類比可能だが厳密には別カテゴリ"},
                    src_lapidus, 0.5,
                    note="既存 taxonomy にイスラム教育機関の専用 form code がないため類縁の monastery を partial 対応"))
    assign_form(azhar, "legal_form", "waqf", is_primary=True,
                valid_from="0972-06-24", confidence=0.9, claim_id=azhar_claim)
    assign_form(azhar, "mintzberg_1989", "professional_bureaucracy",
                valid_from="1961-01-01", confidence=0.7,
                claim_id=add_claim("organization_form_assignment", azhar, "form", "partial",
                    {"reasoning": "1961 年改革後の近代大学化により Mintzberg の専門官僚制概念が一定適合"},
                    src_lapidus, 0.7))

    a_azhar_teach = add_act(azhar, "religious_education", domain="知識",
        description="クルアーン解釈・ハディース・フィクフ・カラーム・アラビア語学の教授。ハラカ (学習サークル) とイジャーザ (修了証) による知識継承",
        outputs={"graduates": "ulama (イスラム学者)", "fatwas": "issued continuously"},
        scale={"current_students_world_total": "~500K (本校+附属高校網)"},
        orientation="exploitation", valid_from="0972-06-24", confidence=0.9)

    a_azhar_fatwa = add_act(azhar, "religious_jurisprudence", domain="統治",
        description="ファトワー (法的見解) の発行、四大法学派 (ハナフィー・マーリキー・シャーフィイー・ハンバリー) の権威機関",
        orientation="exploitation", valid_from="1171-01-01", confidence=0.85)

    add_func(azhar, "miller_01_reproducer",
             mechanism={"means": ["イジャーザ制度による師弟伝授",
                                  "卒業生が世界各地でマドラサ・モスクを設立"]},
             confidence=0.9)
    add_func(azhar, "miller_17_memory",
             mechanism={"means": ["写本・図書館 (al-Azhar Library)",
                                  "口承イスナード (伝承連鎖) の保持"]},
             confidence=0.95)
    add_func(azhar, "miller_03_ingestor",
             mechanism={"means": ["waqf 寄進による永久財源",
                                  "学生からの授業料は伝統的に無し (waqf が教師俸給を負担)"]},
             confidence=0.9)
    add_func(azhar, "vsm_s5_policy_identity",
             mechanism={"means": ["シャイフ・アル=アズハル (大長老)",
                                  "四法学派の調和的並列",
                                  "1961 年改革で世俗諸学併設だが伝統権威継続"]},
             confidence=0.85)
    add_func(azhar, "miller_02_boundary",
             mechanism={"means": ["ウラマー資格認定 (イジャーザ)",
                                  "シャイフ・アル=アズハル の任免はカイロ政権と連動"]},
             confidence=0.85)

    add_imp(azhar, "文化", "ulama_reproduction",
            {"description": "1000 年以上にわたり世界中のスンニ派ウラマーを再生産、フィクフ・カラームの規範形成"},
            "positive", "intergenerational",
            evaluation_method="historical_interpretation",
            confidence=0.9,
            affected_scope={"region": "global_sunni_islam", "duration_years": 1054})

    add_imp(azhar, "政治", "religious_authority",
            {"description": "オスマン以降エジプト政権との緊張・協調関係を通じて公的宗教権威を保持。"
                            "サダト・ムバーラク・シーシー期にも国家正統化機能"},
            "descriptive", "intergenerational",
            evaluation_method="historical_interpretation", confidence=0.8)

    add_imp(azhar, "経済", "waqf_endowment_scale",
            {"description": "アイユーブ・マムルーク・オスマン期に集積された waqf 資産は中東最大級、"
                            "1952 年エジプト革命後に部分国有化"},
            "descriptive", "long_term", confidence=0.8)

    e_azhar_found = add_event("founding",
        event_date="0972-06-24", event_date_precision="exact",
        description="ファーティマ朝のジャウハル・シキッリーがカイロ建設の一環として Al-Azhar モスクを完成",
        location={"city": "Cairo, Egypt"},
        causes={"political": "ファーティマ朝の新都建設とシーア派宣布拠点の必要"},
        outcomes={"new_org": "Al-Azhar Mosque"},
        vsr_label="variation", confidence=0.9)
    link_event_org(e_azhar_found, azhar, "founder")

    e_azhar_sunni = add_event("reform",
        event_date="1171-01-01", event_date_precision="year",
        description="サラディンによるアイユーブ朝樹立、Al-Azhar はシーア派からスンニ派教育機関へ転換",
        causes={"political": "ファーティマ朝崩壊と宗派的再定義"},
        outcomes={"sect_shift": "Shia → Sunni", "institutional_continuity": "preserved"},
        vsr_label="retention", confidence=0.85)
    link_event_org(e_azhar_sunni, azhar, "transformed")

    e_azhar_modernize = add_event("reform",
        event_date="1961-07-05", event_date_precision="exact",
        description="ナーセル政権下の Law No. 103/1961 により近代大学として再編、世俗諸学 (医学・工学・農学等) 併設",
        causes={"political": "アラブ社会主義改革", "secular": "近代国家プロジェクト"},
        outcomes={"new_form": "modern_university_with_sharia_core"},
        vsr_label="retention", confidence=0.95)
    link_event_org(e_azhar_modernize, azhar, "transformed")

    # ============================================================
    # CASE 20: Bayt al-Hikma (House of Wisdom, c.786-1258)
    # ============================================================
    bayt = add_org("バイト・アル=ヒクマ (Bayt al-Ḥikma / House of Wisdom)",
        alternate_names=[
            {"name": "Bayt al-Ḥikma", "lang": "ar"},
            {"name": "House of Wisdom", "lang": "en"},
            {"name": "知恵の館", "lang": "ja"},
        ],
        description=(
            "アッバース朝の翻訳・知識集積機関。起源は al-Manṣūr (位 754-775) または "
            "Hārūn al-Rashīd (位 786-809) のササン朝模倣の宮廷図書館。"
            "al-Maʾmūn (位 813-833) のもとで翻訳運動の中心となり、ギリシア・ペルシア・"
            "インド由来の哲学・医学・天文学・数学文献をアラビア語へ大量翻訳。"
            "1258 年モンゴル軍によるバグダード陥落で物理的に消滅。"
            "Gutas (1998) は institution としての連続性を慎重に扱い、"
            "むしろアッバース朝の'翻訳運動'という分散的政策の象徴と位置づける。"
        ),
        geo_scope={"hq": "Baghdad", "translation_network": "Greek/Syriac/Pahlavi/Sanskrit → Arabic"},
        start_date="0786-01-01", start_date_precision="period",
        end_date="1258-02-10", end_date_precision="exact",
        status="extinct",
        attributes={"period": "c.786-1258 (~470 years)",
                    "key_caliphs": ["al-Mansur", "Harun al-Rashid", "al-Ma'mun"],
                    "translators": ["Hunayn ibn Ishaq", "Thabit ibn Qurra", "al-Khwarizmi"],
                    "fields": ["philosophy", "mathematics", "astronomy", "medicine", "alchemy"]},
        external_ids={"wikidata": "Q236077"})
    inserted.append(("organization", bayt, "Bayt al-Hikma"))

    bayt_claim = add_claim("organization", bayt, "start_date", "partial",
        {"date_range": "786-833", "context": "起源年は議論あり。Hārūn 治下を起源説とする見解と、"
                                              "al-Maʾmūn 期の '翻訳運動' を制度化された機関と区別すべき (Gutas) との見解"},
        src_gutas, 0.7,
        note="Wikipedia 系の年代主張 (786 年起源) と学術研究 (al-Maʾmūn 期に institutional shape) の差異を反映")
    assign_form(bayt, "historical_era", "ancient_bureaucracy", is_primary=True,
                valid_from="0786-01-01", valid_to="1258-02-10",
                confidence=0.6, claim_id=bayt_claim)

    a_bayt_translate = add_act(bayt, "knowledge_translation", domain="知識",
        description="ギリシア・シリア・ペルシア・サンスクリット文献のアラビア語訳。"
                    "Hunayn ibn Ishaq 父子は二段階校訂 (シリア語 → アラビア語) を確立",
        inputs={"source_languages": ["Greek", "Syriac", "Pahlavi", "Sanskrit"],
                "patrons": ["caliphs", "Banu Musa brothers", "wealthy elites"]},
        outputs={"translated_works": "数百巻 (Galen, Aristotle, Ptolemy, Euclid 等)",
                 "innovations": ["二段階翻訳", "技術用語アラビア語化"]},
        orientation="exploration", valid_from="0786-01-01", valid_to="1258-02-10", confidence=0.9)

    a_bayt_research = add_act(bayt, "scientific_research", domain="知識",
        description="天文観測 (Maraghan/Baghdad 観測表)、代数・幾何学発展 (al-Khwarizmi)、医学辞典編纂",
        outputs={"works": ["Kitab al-Jabr (代数の起源)", "Zij al-Sindhind", "al-Razi 医学全集"]},
        orientation="exploration", valid_from="0813-01-01", valid_to="1258-02-10", confidence=0.85)

    add_func(bayt, "miller_15_decoder",
             mechanism={"means": ["二段階翻訳プロセス (Greek→Syriac→Arabic)",
                                  "Hunayn ibn Ishaq の校訂法"]},
             activity_id=a_bayt_translate, confidence=0.9)
    add_func(bayt, "miller_17_memory",
             mechanism={"means": ["写本収集 (ビザンツ・サーサーン両帝国の遺産統合)",
                                  "アラビア語標準化された科学用語"]},
             confidence=0.9)
    add_func(bayt, "miller_03_ingestor",
             mechanism={"means": ["カリフ俸給 (パトロン制)",
                                  "ビザンツへの遣使による写本獲得 (ex. al-Maʾmūn → Leo VI 提案)"]},
             confidence=0.85)
    add_func(bayt, "miller_19_encoder",
             mechanism={"means": ["アラビア語による科学新語創出",
                                  "後代イスラム諸学・スコラ学への伝播形式の準備"]},
             confidence=0.85)
    add_func(bayt, "vsm_s4_intelligence_strategy",
             mechanism={"means": ["カリフ・パトロンによる戦略的知識獲得 (政治正統化と実用知識の両狙い)",
                                  "Gutas: 翻訳運動はアッバース朝の political-economic project"]},
             confidence=0.8)

    add_imp(bayt, "知識", "translation_corpus_size",
            {"description": "古代ギリシア科学の主要著作の大半をアラビア語化、"
                            "後の 12c ヨーロッパ翻訳運動 (Toledo School 等) の主要源泉"},
            "positive", "intergenerational",
            evaluation_method="comparison",
            affected_scope={"target": "global_scientific_corpus", "duration_years": 1500},
            confidence=0.9)

    add_imp(bayt, "経済", "patronage_economy",
            {"description": "カリフ・廷臣・商人による翻訳出資は中東知識経済の最初期モデル"},
            "positive", "long_term", confidence=0.7)

    add_imp(bayt, "政治", "abbasid_legitimation",
            {"description": "Gutas: 翻訳運動はアッバース朝のシャー (ペルシア) 帝国継承イデオロギーと、"
                            "ムウタジラ派合理主義神学の政治的バックアップ機能"},
            "descriptive", "long_term",
            evaluation_method="historical_interpretation", confidence=0.75)

    e_bayt_found = add_event("founding",
        event_date="0786-01-01", event_date_precision="period",
        description="アッバース朝宮廷図書館として漸進的に成立 (Hārūn al-Rashīd 治下に拡張)",
        location={"city": "Baghdad"},
        causes={"political": "アッバース朝のサーサーン継承イデオロギー",
                "intellectual": "イスラム神学・法学発展に伴うギリシア論理学の必要"},
        vsr_label="variation", confidence=0.7)
    link_event_org(e_bayt_found, bayt, "founder")

    e_bayt_mamun = add_event("reform",
        event_date="0830-01-01", event_date_precision="period",
        description="al-Maʾmūn 治下で翻訳運動が制度的頂点へ。観測所併設、Hunayn 派の校訂体制確立",
        causes={"political": "ムウタジラ派 mihna 政策と知識正統化"},
        outcomes={"institutional_form": "translation+research_complex"},
        vsr_label="retention", confidence=0.8)
    link_event_org(e_bayt_mamun, bayt, "transformed")

    e_bayt_destroyed = add_event("dissolution",
        event_date="1258-02-10", event_date_precision="exact",
        description="モンゴル軍 (フレグ) のバグダード攻略で破壊。チグリス川にインクの黒で流れたと伝承",
        dissolution_cause="war_destruction",
        causes={"war": "Mongol Invasion (Hülegü)", "political": "アッバース朝最終崩壊"},
        outcomes={"successor": None,
                  "diaspora": "学者は Maragheh 観測所 (1259-) や Cairo へ離散"},
        vsr_label="selection", confidence=0.9)
    link_event_org(e_bayt_destroyed, bayt, "dissolved")

    # ============================================================
    # CASE 21: Ottoman Timar System (14c-1831)
    # ============================================================
    timar = add_org("オスマン・ティマール制 (Ottoman Timar System)",
        alternate_names=[
            {"name": "Tımar Sistemi", "lang": "tr"},
            {"name": "Ottoman timar / sipahi system", "lang": "en"},
            {"name": "ティマール制", "lang": "ja"},
        ],
        description=(
            "オスマン朝が 14c 中葉から 19c 初頭まで運用した軍事封建的徴税権配分システム。"
            "国家所有地 (mîrî 地) の徴税権を sipahi (騎兵) に時限的に付与、見返りに "
            "rüzname (徴兵動員) と装備自弁を要求。所有でなく徴税権 (用益権)、相続も基本的に不可。"
            "ビザンツ pronoia 制度を 15c 後半に標準化。古典期 (16c) には約 4 万 timar 保有者を擁し "
            "オスマン軍主力。17c 以降 iltizam (徴税請負) と çiftlik (大農場) に侵食され衰退、"
            "1831 年マフムト 2 世により正式廃止。組織論的には'契約条件付き徴税権ネットワーク' という "
            "ガバナンス・イノベーションとして稀有な事例 (İnalcık)。"
        ),
        geo_scope={"core": "Anatolia, Rumelia (Balkans)",
                   "extent": "Ottoman heartland (excluding Egypt, Hejaz, Yemen)"},
        start_date="1362-01-01", start_date_precision="century",
        end_date="1831-01-01", end_date_precision="year",
        status="extinct",
        attributes={"holders_classical_peak": "~40,000 sipahis (16c)",
                    "innovations": ["国家所有・用益権分離", "non-inheritable",
                                    "tahrir defteri (徴税台帳) で 30 年毎に再調査"],
                    "abolition": "1831 by Mahmud II (新軍 nizam-ı cedid 編成の前提)"},
        external_ids={"wikidata": "Q1144675"})
    inserted.append(("organization", timar, "Ottoman timar"))

    timar_claim = add_claim("organization", timar, "start_date", "partial",
        {"context": "14c 半ばに Murad I 治下で原型出現、15c 後半 Mehmed II 期に標準化"},
        src_inalcik_ottoman, 0.9,
        note="制度の始期は段階的、'創立日'を定めにくい")
    assign_form(timar, "historical_era", "weberian_bureaucracy", is_primary=False,
                confidence=0.5,
                claim_id=add_claim("organization_form_assignment", timar, "form", "partial",
                    {"reasoning": "tahrir 台帳・kanunname (法令集) による文書主義はパートリアル・ヴェーバー的"},
                    src_inalcik_ottoman, 0.5))
    assign_form(timar, "historical_era", "ancient_bureaucracy", is_primary=True,
                valid_from="1362-01-01", valid_to="1831-01-01",
                confidence=0.7, claim_id=timar_claim)
    assign_form(timar, "legal_form", "guild", confidence=0.3,
                claim_id=add_claim("organization_form_assignment", timar, "form", "partial",
                    {"reasoning": "現代法人カテゴリと適合せず、参考レベル"},
                    src_inalcik_ottoman, 0.3))
    assign_form(timar, "mintzberg_1989", "machine_bureaucracy", confidence=0.5,
                claim_id=add_claim("organization_form_assignment", timar, "form", "partial",
                    {"reasoning": "規格化された業務 (徴税・徴兵) と中央集権だが時代錯誤的適用"},
                    src_inalcik_econ, 0.5))

    a_timar_levy = add_act(timar, "fiscal_administration", domain="統治",
        description="国家所有地 (mîrî) の租税徴収権を時限的に sipahi へ付与。"
                    "tahrir defteri (徴税台帳) を約 30 年毎に更新",
        inputs={"land": "miri (state-owned arable)",
                "cadastral_basis": "tahrir survey"},
        outputs={"revenue_to_sipahi": "annual ~3,000-20,000 akçe (sub-zeamet level)",
                 "central_treasury_share": "via has (ruler) / paşmaklık 等"},
        scale={"sipahi_count_16c": 40000, "land_coverage": "Anatolia + Rumelia"},
        orientation="exploitation", valid_from="1362-01-01", valid_to="1831-01-01", confidence=0.9)

    a_timar_mil = add_act(timar, "military_operations", domain="軍事",
        description="騎兵 (sipahi) の動員。timar 収入の規模に応じて装備兵 (cebelu) 同伴義務",
        outputs={"cavalry_strength_classical": "~70,000 (sipahi+cebelu)"},
        orientation="exploitation", valid_from="1362-01-01", valid_to="1700-01-01", confidence=0.9)

    add_func(timar, "miller_03_ingestor",
             mechanism={"means": ["tahrir 台帳に基づく徴税",
                                  "öşür (収穫税)・çift resmi (ヤク税) 等の体系"]},
             activity_id=a_timar_levy, confidence=0.9)
    add_func(timar, "miller_04_distributor",
             mechanism={"means": ["sancakbey (郡守) を介した timar berat (発令書) 配分",
                                  "中央 (defterhane) → 地方 (sancak) の二層構造"]},
             confidence=0.85)
    add_func(timar, "miller_18_decider",
             mechanism={"means": ["スルタン (帝勅 berat)",
                                  "kanunname (法令集) による条件規定",
                                  "kazasker (軍法官) による紛争裁定"]},
             confidence=0.85)
    add_func(timar, "miller_17_memory",
             mechanism={"means": ["tahrir defteri (詳細台帳) と icmal defteri (要約)",
                                  "オスマン文書館 (現 BOA) に大量現存"]},
             confidence=0.95)
    add_func(timar, "vsm_s3_internal_control",
             mechanism={"means": ["tahrir 30 年再調査による再分配",
                                  "cebelu 数の検閲 (mecmua-i sefer)"]},
             confidence=0.85)

    add_imp(timar, "経済", "fiscal_capacity",
            {"description": "貨幣経済が浅い段階での税収徴収・兵力動員の同時解決。"
                            "古典期オスマン軍の主力騎兵を低貨幣コストで維持"},
            "positive", "long_term",
            evaluation_method="comparison",
            affected_scope={"region": "Ottoman_heartland", "period_years": 470},
            confidence=0.85)

    add_imp(timar, "政治", "centralization_paradox",
            {"description": "用益権・非世襲条項により欧州封建制と異なり地方貴族化を抑制 — "
                            "中央集権維持のためのガバナンス装置"},
            "positive", "long_term", confidence=0.85)

    add_imp(timar, "経済", "decline_mechanism",
            {"description": "17c 以降 iltizam (徴税請負) と çiftlik (商業的大農場) に駆逐される過程で "
                            "農村経済格差・地方名家 (ayan) 台頭を招く"},
            "negative", "long_term", confidence=0.8)

    e_timar_origin = add_event("founding",
        event_date="1362-01-01", event_date_precision="century",
        description="Murad I 治下で原型成立、Mehmed II (位 1444-46, 1451-81) 期に kanunname で標準化",
        location={"region": "Anatolia + Rumelia"},
        causes={"political": "ビザンツ pronoia 制度のオスマン的再編"},
        vsr_label="variation", confidence=0.8)
    link_event_org(e_timar_origin, timar, "founder")

    e_timar_abolish = add_event("dissolution",
        event_date="1831-01-01", event_date_precision="year",
        description="マフムト 2 世が timar 制を正式廃止、新軍 (Asakir-i Mansure-i Muhammediye) と俸給軍へ移行",
        dissolution_cause="obsolescence",
        causes={"political": "1826 年イェニチェリ廃止と中央集権化",
                "military": "ヨーロッパ近代軍に対応できない騎兵中心",
                "economic": "iltizam・çiftlik による事実上の侵食"},
        outcomes={"successor": "salaried_modern_army"},
        vsr_label="selection", confidence=0.9)
    link_event_org(e_timar_abolish, timar, "dissolved")

    # ============================================================
    # CASE 22: Naqshbandi Tariqa (c.1380-)
    # ============================================================
    naqsh = add_org("ナクシュバンディー教団 (Naqshbandi Tariqa)",
        alternate_names=[
            {"name": "Naqshbandiyya", "lang": "ar"},
            {"name": "Tariqa-i Naqshbandiyya", "lang": "fa"},
            {"name": "ナクシュバンディーヤ", "lang": "ja"},
        ],
        description=(
            "Bahā' al-Dīn Naqshband (1318-1389, ブハラ近郊) を eponym とするスンニ派スーフィー教団。"
            "Khwajagan 系譜を母体に 14c 後半に成立、'silent dhikr (静かな唱念)'、シャリーア厳守、"
            "現世参与 ('khalwat dar anjuman' / 群衆の中の閑寂) を特徴とする。"
            "シルシラ (霊的系譜) は唯一アブー・バクル経由でムハンマドへ遡るとされる。"
            "中央アジア → インド (Mujaddidī 派, Aḥmad Sirhindī, 17c) → オスマン (Khalidī 派, 19c) と"
            "拡散、現存最大級の世界的スンニ派教団。"
        ),
        geo_scope={"origin": "Bukhara, Transoxiana",
                   "spread": ["Central Asia", "South Asia", "Ottoman lands", "Caucasus", "global diaspora"]},
        start_date="1380-01-01", start_date_precision="decade",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={"founder": "Bahā' al-Dīn Naqshband (1318-1389)",
                    "longevity_years": 645,
                    "innovations": ["silent dhikr",
                                    "engagement-not-withdrawal",
                                    "lineage via Abu Bakr (unique among major orders)"],
                    "major_branches": ["Mujaddidiyya (17c)", "Khalidiyya (19c)", "Haqqaniyya (20c)"]},
        external_ids={"wikidata": "Q1064809"})
    inserted.append(("organization", naqsh, "Naqshbandi"))

    naqsh_claim = add_claim("organization", naqsh, "start_date", "partial",
        {"date": "c.1380", "context": "Bahā' al-Dīn Naqshband 没年 1389、生前にすでに弟子集団形成。"
                                       "正式な tariqa 化は弟子世代以降と見る (Trimingham)"},
        src_trimingham, 0.8,
        note="教団形成は eponymous master 周辺で漸進的、創立日を厳密に確定できない")
    assign_form(naqsh, "historical_era", "monastery", is_primary=False,
                confidence=0.5,
                claim_id=add_claim("organization_form_assignment", naqsh, "form", "partial",
                    {"reasoning": "tariqa は monastery と異なり俗世内活動を前提、partial 適用"},
                    src_trimingham, 0.5))
    assign_form(naqsh, "legal_form", "monastic_order", is_primary=True,
                valid_from="1380-01-01", confidence=0.6, claim_id=naqsh_claim,
                )
    assign_form(naqsh, "mintzberg_1989", "missionary", confidence=0.85,
                claim_id=add_claim("organization_form_assignment", naqsh, "form", "present",
                    {"reasoning": "イデオロギー統合 (silsila + adab) が支配的調整メカニズム"},
                    src_trimingham, 0.85))

    a_naqsh_dhikr = add_act(naqsh, "religious_practice", domain="儀礼",
        description="silent dhikr (静かな唱念)、瞑想 (murāqaba)、シャイフへの精神的指導 (suhba)",
        outputs={"spiritual_attainment": "fanā / baqā (神秘的合一・継続)",
                 "discipline": "8 then 11 principles (kalimāt al-qudsiyya)"},
        orientation="exploitation", valid_from="1380-01-01", confidence=0.9)

    a_naqsh_silsila = add_act(naqsh, "lineage_transmission", domain="知識",
        description="シャイフ → ムリード (弟子) への ijāza・khilāfa (継承免許) 付与による系譜継承",
        outputs={"new_shaykhs": "数千人スケールの世界的継承",
                 "branches": ["Mujaddidiyya", "Khalidiyya", "Haqqaniyya"]},
        orientation="exploration", valid_from="1380-01-01", confidence=0.9)

    a_naqsh_polit = add_act(naqsh, "political_engagement", domain="政治",
        description="Khwāja Aḥrār (15c, ティムール朝)、Aḥmad Sirhindī (17c, ムガル帝国)、"
                    "Khālid al-Baghdādī (19c, オスマン) など歴代シャイフが政治介入",
        orientation="exploration", valid_from="1450-01-01", confidence=0.85)

    add_func(naqsh, "miller_01_reproducer",
             mechanism={"means": ["silsila (霊的系譜)",
                                  "khilāfa (代理職) 任命による教団分岐再生産"]},
             activity_id=a_naqsh_silsila, confidence=0.95)
    add_func(naqsh, "vsm_s5_policy_identity",
             mechanism={"means": ["8/11 原理 (kalimāt al-qudsiyya)",
                                  "Bahā' al-Dīn の adab (倫理規律)"]},
             confidence=0.9)
    add_func(naqsh, "miller_13_channel_and_net",
             mechanism={"means": ["巡礼・遍歴 (rihla) によるシャイフ間交流",
                                  "tekke / khānaqāh / zāwiya のネットワーク"]},
             confidence=0.85)
    add_func(naqsh, "miller_17_memory",
             mechanism={"means": ["師の言行録 (malfūẓāt)",
                                  "Maktūbāt (Sirhindī の書簡集) 等の写本伝承"]},
             confidence=0.9)
    add_func(naqsh, "vsm_s4_intelligence_strategy",
             mechanism={"means": ["政治権力との戦略的距離調整 (Khwāja Aḥrār・Sirhindī モデル)",
                                  "国家・社会への積極参与 ('khalwat dar anjuman')"]},
             confidence=0.8)

    add_imp(naqsh, "文化", "spiritual_lineage_reach",
            {"description": "中央アジア・南アジア・オスマン世界・近現代世界規模で継続する最大級スンニ派教団"},
            "positive", "intergenerational",
            evaluation_method="historical_interpretation",
            affected_scope={"region": "global_sunni_islam", "duration_years": 645},
            confidence=0.9)

    add_imp(naqsh, "政治", "imperial_court_influence",
            {"description": "ティムール朝・ムガル帝国・オスマン後期で宮廷顧問的立場、"
                            "Aḥmad Sirhindī はムガルの shariah 強化に影響"},
            "descriptive", "long_term",
            evaluation_method="historical_interpretation", confidence=0.8)

    add_imp(naqsh, "社会", "anti_colonial_mobilization",
            {"description": "19c コーカサス (Shamil)、中央アジア (Andijan), 北アフリカで抗植民闘争動員"},
            "descriptive", "medium_term", confidence=0.75)

    e_naqsh_found = add_event("founding",
        event_date="1380-01-01", event_date_precision="decade",
        description="Bahā' al-Dīn Naqshband 周辺の弟子集団化、後継世代で tariqa 化",
        location={"city": "Bukhara region"},
        causes={"intellectual": "Khwajagan 系譜の継承と独自路線 (silent dhikr)"},
        vsr_label="variation", confidence=0.8)
    link_event_org(e_naqsh_found, naqsh, "founder")

    e_naqsh_mujaddidi = add_event("reform",
        event_date="1600-01-01", event_date_precision="year",
        description="Aḥmad Sirhindī (1564-1624) によるムジャッディディー派形成、ムガル朝でシャリーア重視",
        outcomes={"new_branch": "Mujaddidiyya"},
        vsr_label="retention", confidence=0.85)
    link_event_org(e_naqsh_mujaddidi, naqsh, "transformed")

    e_naqsh_khalidi = add_event("reform",
        event_date="1820-01-01", event_date_precision="year",
        description="Mawlānā Khālid al-Baghdādī (1779-1827) による Khalidiyya 派形成、"
                    "オスマン帝国・コーカサスで急拡大",
        outcomes={"new_branch": "Khalidiyya"},
        vsr_label="retention", confidence=0.85)
    link_event_org(e_naqsh_khalidi, naqsh, "transformed")

    # ============================================================
    # CASE 23: Süleymaniye Külliyesi (1557-)
    # ============================================================
    suley = add_org("スレイマニエ・キュリエ (Süleymaniye Külliyesi)",
        alternate_names=[
            {"name": "Süleymaniye Mosque Complex", "lang": "en"},
            {"name": "Süleymaniye Camii ve Külliyesi", "lang": "tr"},
            {"name": "スレイマニエ複合体", "lang": "ja"},
        ],
        description=(
            "オスマン皇帝 Süleyman I (位 1520-1566) が 1550-1557 年にイスタンブールに建立した "
            "ワクフ複合体 (külliye)。建築家ミマール・スィナンの最高傑作の一つで、"
            "中央モスクの周囲に 4 法学派マドラサ・ハディース学院・医学校・病院 (dār al-shifā)・"
            "公共炊き出し場 (imaret)・隊商宿・ハマム・墓廟 (Süleyman & Hürrem) を配する。"
            "永久ワクフ (waqf khayrī) として土地・店舗・農地・税収を寄進、教師俸給・学生奨学金・"
            "貧困者食事を 5 世紀にわたり提供。1924 年 waqf 国有化までガバナンス継続、"
            "現在も建築物群として継続稼働 (機能の一部は世俗官庁へ移管)。"
        ),
        geo_scope={"hq": "Istanbul (Fatih district)",
                   "endowment_assets": "lands across Anatolia & Rumelia"},
        start_date="1557-01-01", start_date_precision="year",
        end_date=None, end_date_precision=None,
        status="transformed",
        attributes={"founder": "Süleyman I (the Magnificent)",
                    "architect": "Mimar Sinan",
                    "construction": "1550-1557 (mausoleums to 1559)",
                    "components": ["mosque", "4 Sunni-school madrasas", "Dar al-Hadith",
                                   "medical school", "hospital", "imaret", "caravanserai", "hamam", "tombs"],
                    "endowment_doc": "waqfiyya 1557 (kept in BOA)"},
        external_ids={"wikidata": "Q188074"})
    inserted.append(("organization", suley, "Süleymaniye Külliyesi"))

    suley_claim = add_claim("organization", suley, "start_date", "present",
        {"date": "1557", "context": "本体モスク完成・waqfiyya 登録の年。Necipoğlu と建築刻文で確認"},
        src_necipoglu, 0.95,
        note="マウソレウムまでの完工は 1559、waqfiyya 文書には 1557 を foundation date とする")
    assign_form(suley, "legal_form", "waqf", is_primary=True,
                valid_from="1557-01-01", valid_to="1924-01-01",
                confidence=0.95, claim_id=suley_claim)
    assign_form(suley, "historical_era", "monastery", confidence=0.55,
                claim_id=add_claim("organization_form_assignment", suley, "form", "partial",
                    {"reasoning": "monastery は機能類似だが内部居住共同体ではない、partial 比較"},
                    src_necipoglu, 0.55))
    assign_form(suley, "mintzberg_1989", "missionary", confidence=0.7,
                claim_id=add_claim("organization_form_assignment", suley, "form", "partial",
                    {"reasoning": "宗教的価値観による調整支配だが多機能複合 (病院・学校・救貧) で adhocracy 要素も"},
                    src_necipoglu, 0.7))

    a_suley_edu = add_act(suley, "religious_education", domain="知識",
        description="4 法学派マドラサ + Dar al-Hadith による上級イスラム法学教育、卒業生はオスマン司法・教育職へ",
        outputs={"graduates_per_year_estimate": "~50-100 ulama (16-19c)",
                 "career_track": "kadi, müderris, müfti"},
        orientation="exploitation", valid_from="1557-01-01", valid_to="1924-01-01", confidence=0.85)

    a_suley_health = add_act(suley, "healthcare", domain="医療",
        description="Dār al-shifā (病院) と医学校 (Dār al-tıb) による医療提供と医師育成、ムスリム・非ムスリム問わず無料",
        outputs={"capacity": "数十床 + 外来", "specialties": ["内科", "眼科", "精神病床"]},
        scale={"continuity_years": 367},
        orientation="exploitation", valid_from="1557-01-01", valid_to="1924-01-01", confidence=0.85)

    a_suley_charity = add_act(suley, "charitable_provision", domain="社会",
        description="imaret (公共炊き出し) で日 1000-3000 食、貧困者・旅人・学生に無料配給",
        outputs={"meals_per_day_peak": 3000, "beneficiaries": "非ムスリムも含む"},
        orientation="exploitation", valid_from="1557-01-01", valid_to="1924-01-01", confidence=0.85)

    a_suley_endow = add_act(suley, "endowment_management", domain="統治",
        description="ワクフ財産 (土地・店舗・農地・徴税権) からの収益で教師・医師・職員俸給と運営費を賄う",
        inputs={"asset_classes": ["agricultural land", "urban shops", "tax revenue rights"]},
        outputs={"annual_revenue_classical": "~50,000-100,000 akçe (estimate)"},
        orientation="exploitation", valid_from="1557-01-01", valid_to="1924-01-01", confidence=0.8)

    add_func(suley, "miller_07_matter_energy_storage",
             mechanism={"means": ["waqf 不動産 (永久所有不可分)",
                                  "穀物倉 (anbar)・調理施設"]},
             confidence=0.9)
    add_func(suley, "miller_03_ingestor",
             mechanism={"means": ["ワクフ財産からの賃料・地代",
                                  "皇室追加寄進"]},
             activity_id=a_suley_endow, confidence=0.9)
    add_func(suley, "miller_04_distributor",
             mechanism={"means": ["mütevelli (受託管理者) → 各機能職員への俸給配分",
                                  "imaret での食事配給ルーチン"]},
             confidence=0.9)
    add_func(suley, "miller_18_decider",
             mechanism={"means": ["mütevelli (waqf 管理人、当初は皇族 → 後に bureaucrat)",
                                  "kadi の監督"]},
             confidence=0.85)
    add_func(suley, "vsm_s5_policy_identity",
             mechanism={"means": ["waqfiyya 文書 (1557) が永久に職務・俸給率・条件を規定",
                                  "Süleyman I の創設者意図 (敬神+公共福祉+王朝威信)"]},
             confidence=0.95)
    add_func(suley, "miller_01_reproducer",
             mechanism={"means": ["卒業生がオスマン全土でマドラサ・モスク網に再生産",
                                  "他キュリエ (Selimiye, Sultanahmet) のテンプレート提供"]},
             confidence=0.85)

    add_imp(suley, "文化", "architectural_canon",
            {"description": "オスマン古典建築の完成形、後の Selimiye (1574)・Sultanahmet (1616) のモデル"},
            "positive", "intergenerational",
            evaluation_method="historical_interpretation", confidence=0.95)

    add_imp(suley, "社会", "welfare_provision",
            {"description": "5 世紀にわたり医療・教育・救貧を都市住民・旅人・非ムスリムに無料提供"},
            "positive", "intergenerational",
            affected_scope={"city": "Istanbul", "duration_years": 367},
            confidence=0.9)

    add_imp(suley, "経済", "endowment_capitalization",
            {"description": "オスマン経済における waqf セクターは GDP の数 % 規模 (Çizakça 推計)、"
                            "近代以前の最大級非市場資産動員"},
            "descriptive", "long_term",
            evaluation_method="comparison", confidence=0.75)

    add_imp(suley, "政治", "dynastic_legitimation",
            {"description": "Süleyman の 'Kanuni' (法制定者) 像と一体、王朝威信・敬神・公共福祉の三位一体"},
            "positive", "long_term", confidence=0.85)

    e_suley_found = add_event("founding",
        event_date="1557-01-01", event_date_precision="year",
        description="Süleymaniye 本体モスク完成、waqfiyya 登録",
        location={"city": "Istanbul"},
        causes={"political": "Süleyman の王朝建築プログラム",
                "religious": "法制定者としての敬神事業"},
        outcomes={"new_org": "Süleymaniye Külliyesi waqf"},
        vsr_label="variation", confidence=0.95)
    link_event_org(e_suley_found, suley, "founder")

    e_suley_nationalize = add_event("reorganization",
        event_date="1924-03-03", event_date_precision="exact",
        description="トルコ共和国 1924 年 Tevhid-i Tedrisat (教育統一法) と waqf 国有化により "
                    "ワクフは Vakıflar Genel Müdürlüğü (国家ワクフ庁) 管轄へ、機能分離",
        causes={"political": "ケマル主義の世俗化改革",
                "legal": "Caliphate 廃止と宗教制度再編"},
        outcomes={"governance_form": "state_managed_heritage",
                  "function_split": "教育→世俗大学, 病院→保健省, 宗教→Diyanet"},
        vsr_label="selection", confidence=0.95)
    link_event_org(e_suley_nationalize, suley, "transformed")

    # ============================================================
    # Relations (既存 18 ケースとの接続)
    # ============================================================

    # (1) Bayt al-Hikma → Bologna (knowledge_transfer; 翻訳経由)
    if bologna_id:
        rel_claim = add_claim("relation", "pending", "type", "present",
            {"reasoning": "12c Toledo School と Sicily 翻訳運動を経由したアラビア語 → ラテン語 "
                          "Aristotle・Avicenna・Averroes 文献流入が Bologna 法学・自由七科の素材を提供。"
                          "Haskins (1923) と Burnett (2001) で確認"},
            src_gutas, 0.7,
            note="直接的継承ではなく Toledo・Salerno 経由の二段階継承。chain は薄いが確実")
        add_relation(bayt, bologna_id, "knowledge_transfer",
            valid_from="0900-01-01", valid_to="1258-02-10",
            relation_attributes={"transfer_path": "Bayt al-Hikma → Andalus/Sicily Latin translators → Bologna",
                                 "transferred": ["Aristotle commentaries", "Avicenna (Ibn Sina) Canon",
                                                  "Galen via Hunayn", "al-Khwarizmi algebra"],
                                 "intermediaries": ["Toledo School (Gerard of Cremona)", "Salerno"],
                                 "delay_years": "200-400"},
            strength=0.5, strength_basis="間接的だが文献継承は明確",
            confidence=0.7, claim_id=rel_claim)

    # (2) Al-Azhar ↔ ベネディクト会 (parallel mimetic_isomorphism with no_direct_contact)
    if benedictines_id:
        rel_claim = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "永続的宗教教育機関という構造的並行 — 永久 endowment、"
                          "規範書 (Rule of Benedict / waqfiyya)、卒業証 (oblate professio / ijāza)、"
                          "リトル/ハラカ — を no direct contact で発展。"
                          "DiMaggio & Powell の mimetic isomorphism より '構造的同型' (parallel evolution)"},
            src_lapidus, 0.45,
            note="直接接触は無い、'mimetic_isomorphism' は緩い meaning。比較のための関係付けに留める")
        add_relation(azhar, benedictines_id, "mimetic_isomorphism",
            directionality="undirected",
            valid_from="0972-06-24",
            relation_attributes={"contact": "no_direct_contact",
                                 "convergent_features": ["permanent_endowment",
                                                          "written_rule_or_charter",
                                                          "credential_chain (ijāza / professio)",
                                                          "education + worship + welfare integration"],
                                 "interpretation": "parallel evolution under similar functional pressures"},
            strength=0.3, strength_basis="構造的並行、因果的継承なし",
            confidence=0.45, claim_id=rel_claim)

    # (3) Ottoman timar → Mughal mansabdar (knowledge_transfer; 制度継承)
    if mansabdar_id:
        rel_claim = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "両制度は (a) ペルシア=トルコ系統治伝統 (Ilkhanid・Timurid) を共通祖先とし、"
                          "(b) 軍事サービスと土地/賃金の交換、(c) 非世襲・国家権限性を共有。"
                          "Mughal 側がオスマン制を直接模倣した史料は薄いが、"
                          "Babur (オスマン火砲導入)・Akbar (mansabdar 体系化) の人的・知識的接触あり。"
                          "Athar Ali (1985) と İnalcık (1973) で議論"},
            src_inalcik_ottoman, 0.55,
            note="共通祖先からの並行発達 + 部分的影響、'純粋 succession' でない")
        add_relation(timar, mansabdar_id, "knowledge_transfer",
            valid_from="1571-01-01", valid_to="1700-01-01",
            relation_attributes={"shared_origin": "Ilkhanid/Timurid iqta + soyurghal traditions",
                                 "transferred_features": ["land-revenue-for-service exchange",
                                                           "non-hereditary in principle",
                                                           "central cadastral basis"],
                                 "differences": ["mansab is rank+pay (zat/sawar), timar is land grant",
                                                  "mansabdar can be paid in cash (naqdi) or jagir"],
                                 "evidence": "Babur (1526) brought Ottoman gunpowder doctrine; "
                                             "Akbar's bureaucratic systematization 1571-"},
            strength=0.4, strength_basis="共通祖先 + 限定的直接影響",
            confidence=0.55, claim_id=rel_claim)

    # (4) Süleymaniye waqf → Mondragón (parallel; long-term endowment governance)
    if mondragon_id:
        rel_claim = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "永続性をめざす受益者集合的ガバナンス・分配機構という意味で構造比較可能。"
                          "Süleymaniye=皇室寄進トップダウン永続 vs Mondragón=協同組合員ボトムアップ集合体、"
                          "両者とも'資本の死蔵化 (capital lock-in)'と'機能多角化' "
                          "(教育+医療+生産)を実現 (Çizakça 2000)。直接の継承関係はない"},
            src_necipoglu, 0.4,
            note="分析的比較のための parallel 関係、causal 継承ではない")
        add_relation(suley, mondragon_id, "mimetic_isomorphism",
            directionality="undirected",
            valid_from="1956-01-01",
            relation_attributes={"contact": "no_direct_contact",
                                 "convergent_features": ["permanent_capital_lock_in",
                                                          "multi_function_integration (edu+health+production)",
                                                          "non-distributable_surplus",
                                                          "founder_charter_governing_in_perpetuity"],
                                 "comparison_axis": "long-term endowment / cooperative governance",
                                 "differences": ["top-down royal (waqf) vs bottom-up worker (cooperative)",
                                                  "Islamic theological vs Catholic social teaching framing"]},
            strength=0.25, strength_basis="比較分析的並行",
            confidence=0.4, claim_id=rel_claim)

    # (5) Naqshbandi → 比叡山 (parallel; mystical lineage transmission)
    if enryakuji_id:
        rel_claim = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "霊的師弟系譜 (silsila / 法脈) による知識・修行の世代間継承、"
                          "瞑想実修 (murāqaba / 止観)、政治権力との関係調整、"
                          "教団の地理的拡散様式が構造的に並行。直接接触なし、"
                          "比較宗教学的視点での parallel"},
            src_trimingham, 0.4,
            note="直接接触ゼロ、比較構造論レベルの関係")
        add_relation(naqsh, enryakuji_id, "mimetic_isomorphism",
            directionality="undirected",
            valid_from="1380-01-01",
            relation_attributes={"contact": "no_direct_contact",
                                 "convergent_features": ["mystical_lineage_transmission (silsila / 法脈)",
                                                          "meditation_practice (murāqaba / 止観)",
                                                          "decentralized_lodge_network (khānaqāh / 末寺)",
                                                          "political_engagement_with_courts"],
                                 "comparison_axis": "mystical/contemplative monasticism with worldly engagement",
                                 "key_difference": "Naqshbandi: silent dhikr in marketplace; Tendai: mountain enclosure"},
            strength=0.25, strength_basis="比較構造論並行",
            confidence=0.4, claim_id=rel_claim)

    # 内部関係 (イスラム圏内部の継承・関係)
    # Bayt al-Hikma → Al-Azhar (知的気風の連続)
    rel_claim = add_claim("relation", "pending", "type", "partial",
        {"reasoning": "アッバース朝知識の遺産が Fatimid Cairo の Dar al-Ilm (1004) を経由して "
                      "Al-Azhar の学術文化基盤を形成。間接的だが確実な系譜的接続"},
        src_lapidus, 0.7)
    add_relation(bayt, azhar, "knowledge_transfer",
        valid_from="0972-06-24", valid_to="1258-02-10",
        relation_attributes={"intermediary": "Dar al-Ilm Cairo (1004-1171, Fatimid)",
                             "transferred": ["philosophical theology", "translated sciences",
                                              "manuscript collection practices"]},
        strength=0.5, strength_basis="間接だが実在する系譜",
        confidence=0.7, claim_id=rel_claim)

    # Süleymaniye ← Naqshbandi (オスマン後期 Khalidi 派が complex 内マドラサで影響力)
    rel_claim = add_claim("relation", "pending", "type", "partial",
        {"reasoning": "19c オスマンで Khalidiyya 派 Naqshbandi がスレイマニエを含む帝都マドラサ網に浸透、"
                      "ulama 養成に影響"},
        src_trimingham, 0.55)
    add_relation(naqsh, suley, "normative_pressure",
        valid_from="1820-01-01", valid_to="1924-01-01",
        relation_attributes={"mechanism": "Khalidiyya scholars teaching at imperial madrasas",
                             "influence_type": "spiritual + curricular"},
        strength=0.4, strength_basis="人的浸透の史料あり",
        confidence=0.55, claim_id=rel_claim)

    # Süleymaniye → Al-Azhar (オスマン期に Al-Azhar はオスマン宗主権下、Süleymaniye がトップキュリエとして影響)
    rel_claim = add_claim("relation", "pending", "type", "partial",
        {"reasoning": "1517 年オスマンによるエジプト征服後、Al-Azhar はオスマン宗教政策下に置かれ、"
                      "Süleymaniye マドラサが帝国 ulama カリキュラムの規範を提供"},
        src_inalcik_ottoman, 0.6)
    add_relation(suley, azhar, "normative_pressure",
        valid_from="1557-01-01", valid_to="1798-01-01",
        relation_attributes={"context": "Ottoman suzerainty over Egypt 1517-1798",
                             "mechanism": "imperial madrasa hierarchy with Süleymaniye at top",
                             "limit": "Al-Azhar retained substantial autonomy in fiqh"},
        strength=0.35, strength_basis="制度的従属",
        confidence=0.6, claim_id=rel_claim)

    # Timar → Süleymaniye (waqf 用地の供給源)
    rel_claim = add_claim("relation", "pending", "type", "partial",
        {"reasoning": "スレイマニエ・ワクフ財産の一部は元 timar 地から皇室寄進 (mülk 化を経由) で確保された。"
                      "İnalcık (1973) が手続きを記述"},
        src_inalcik_econ, 0.65)
    add_relation(timar, suley, "supply_chain",
        valid_from="1557-01-01", valid_to="1700-01-01",
        relation_attributes={"transfer_mechanism": "miri → mülk → waqf re-conversion by sultan",
                             "asset_type": "agricultural land revenues"},
        strength=0.4, strength_basis="制度的接続あるが金額規模は限定的",
        confidence=0.65, claim_id=rel_claim)

    conn.commit()

    # ============================================================
    # Verification
    # ============================================================
    org_ids = (azhar, bayt, timar, naqsh, suley)
    cur.execute(f"SELECT COUNT(*) FROM organization WHERE organization_id IN ({','.join(['?']*5)})", org_ids)
    print(f"\n=== 5 Islamic-world cases verification ===")
    print(f"organizations created: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM organization_form_assignment WHERE organization_id IN ({','.join(['?']*5)})", org_ids)
    print(f"form assignments: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM activity WHERE organization_id IN ({','.join(['?']*5)})", org_ids)
    print(f"activities: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM function_record WHERE organization_id IN ({','.join(['?']*5)})", org_ids)
    print(f"functions: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM impact_record WHERE organization_id IN ({','.join(['?']*5)})", org_ids)
    print(f"impacts: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM event WHERE event_id IN (SELECT event_id FROM event_organization WHERE organization_id IN ({','.join(['?']*5)}))", org_ids)
    print(f"events linked: {cur.fetchone()[0]}")

    cur.execute(f"SELECT COUNT(*) FROM relation WHERE source_organization_id IN ({','.join(['?']*5)}) OR target_organization_id IN ({','.join(['?']*5)})", org_ids + org_ids)
    print(f"relations involving these 5: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM organization")
    print(f"\nTotal organizations in DB: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM relation")
    print(f"Total relations in DB: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM source")
    print(f"Total sources in DB: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claim")
    print(f"Total claims in DB: {cur.fetchone()[0]}")

    print("\n=== inserted cases ===")
    for entity_type, eid, name in inserted:
        print(f"  {entity_type:20s}  {eid[:12]}...  {name}")

    conn.close()


if __name__ == "__main__":
    main()
