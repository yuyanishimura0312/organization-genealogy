#!/usr/bin/env python3
"""Phase 2: 6 多様性ケースの深掘り注釈

第1弾 5 ケースの偏り (西欧+日本近代) を補正:
  1. アシャンティ王国 (1670-1957) — 西アフリカ前植民地国家、stool authority
  2. ムガル朝マンサブダール制 (1571-1858) — 階級官僚兼地租受給者
  3. Hadza バンド (現代) — タンザニア、現存狩猟採集民、Boehm 平等主義
  4. Mondragón Corporación Cooperativa (1956-) — バスク協同組合連合
  5. Wikimedia Foundation (2003-) — オープンコモンズ運営
  6. 鴻池家 (1656-1899) — 江戸期豪商、海運+両替+大名貸

各ケースで Phase 2 重点項目を実装:
  - Activity / Function / Impact の機能分解
  - 東アジア・非西洋形態を「文化」に丸めず継承原理・信用・場で記述
  - 「死亡因果」「変容」を Event スキーマで明示
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

    # ---- helpers (subset of 04_representative_cases) ----
    def add_source(stype, title, **kw):
        sid = uid()
        cur.execute(
            """INSERT INTO source (source_id, source_type, title, authors, publication_date,
                publisher, locator, accessed_at, reliability_score, reliability_basis, license, redistribution)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sid, stype, title,
             json.dumps(kw.get("authors")) if kw.get("authors") else None,
             kw.get("publication_date"), kw.get("publisher"),
             json.dumps(kw.get("locator")) if kw.get("locator") else None,
             kw.get("accessed_at"),
             kw.get("reliability_score"),
             kw.get("reliability_basis"),
             kw.get("license"), kw.get("redistribution", "attribution_required")),
        )
        return sid

    def add_claim(et, eid, fp, vk, val, src, conf, by="claude_phase2", note=None):
        cid = uid()
        cur.execute(
            """INSERT INTO claim (claim_id, entity_type, entity_id, field_path, value_kind,
                claim_value, source_id, confidence, recorded_by, interpretation_note)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (cid, et, eid, fp, vk,
             json.dumps(val, ensure_ascii=False) if val is not None else None,
             src, conf, by, note),
        )
        return cid

    def add_org(name, **kw):
        oid = uid()
        cur.execute(
            """INSERT INTO organization (organization_id, canonical_name, alternate_names,
                description, primary_form_id, geo_scope, start_date, start_date_precision,
                end_date, end_date_precision, status, attributes, external_ids)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (oid, name,
             json.dumps(kw.get("alternate_names"), ensure_ascii=False) if kw.get("alternate_names") else None,
             kw.get("description"), kw.get("primary_form_id"),
             json.dumps(kw.get("geo_scope"), ensure_ascii=False) if kw.get("geo_scope") else None,
             kw.get("start_date"), kw.get("start_date_precision"),
             kw.get("end_date"), kw.get("end_date_precision"),
             kw.get("status", "unknown"),
             json.dumps(kw.get("attributes"), ensure_ascii=False) if kw.get("attributes") else None,
             json.dumps(kw.get("external_ids"), ensure_ascii=False) if kw.get("external_ids") else None),
        )
        return oid

    def assign_form(oid, tax, code, **kw):
        row = cur.execute("SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
                          (tax, code)).fetchone()
        if not row:
            return None
        aid = uid()
        cur.execute(
            """INSERT INTO organization_form_assignment
                (assignment_id, organization_id, form_id, valid_from, valid_to, is_primary, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (aid, oid, row[0], kw.get("valid_from"), kw.get("valid_to"),
             1 if kw.get("is_primary") else 0,
             kw.get("confidence", 0.8), kw.get("claim_id")),
        )
        if kw.get("is_primary"):
            cur.execute("UPDATE organization SET primary_form_id=? WHERE organization_id=?",
                        (row[0], oid))
        return aid

    def add_activity(oid, atype, **kw):
        aid = uid()
        cur.execute(
            """INSERT INTO activity (activity_id, organization_id, activity_type, domain,
                description, inputs, outputs, scale, orientation,
                valid_from, valid_to, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (aid, oid, atype, kw.get("domain"), kw.get("description"),
             json.dumps(kw.get("inputs"), ensure_ascii=False) if kw.get("inputs") else None,
             json.dumps(kw.get("outputs"), ensure_ascii=False) if kw.get("outputs") else None,
             json.dumps(kw.get("scale"), ensure_ascii=False) if kw.get("scale") else None,
             kw.get("orientation", "unspecified"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")),
        )
        return aid

    def add_func(oid, ftype_id, **kw):
        fid = uid()
        cur.execute(
            """INSERT INTO function_record (function_id, organization_id, function_type_id,
                mechanism, beneficiaries, dependency, activity_id,
                valid_from, valid_to, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (fid, oid, ftype_id,
             json.dumps(kw.get("mechanism"), ensure_ascii=False) if kw.get("mechanism") else None,
             json.dumps(kw.get("beneficiaries"), ensure_ascii=False) if kw.get("beneficiaries") else None,
             json.dumps(kw.get("dependency"), ensure_ascii=False) if kw.get("dependency") else None,
             kw.get("activity_id"), kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")),
        )
        return fid

    def add_impact(oid, dom, mname, mval, dir_, horizon, **kw):
        iid = uid()
        cur.execute(
            """INSERT INTO impact_record (impact_id, organization_id, impact_domain, metric_name,
                metric_value, direction, time_horizon, affected_scope, evaluation_method,
                valid_from, valid_to, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, oid, dom, mname,
             json.dumps(mval, ensure_ascii=False),
             dir_, horizon,
             json.dumps(kw.get("affected_scope"), ensure_ascii=False) if kw.get("affected_scope") else None,
             kw.get("evaluation_method"),
             kw.get("valid_from"), kw.get("valid_to"),
             kw.get("confidence"), kw.get("claim_id")),
        )
        return iid

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

    def link_eo(eid, oid, role):
        cur.execute("INSERT OR IGNORE INTO event_organization (event_organization_id, event_id, organization_id, role) VALUES (?,?,?,?)",
                    (uid(), eid, oid, role))

    inserted = []

    # ============ sources ============
    src_wilks = add_source("secondary_literature",
        "Wilks, I. (1975) Asante in the Nineteenth Century",
        authors=["Ivor Wilks"], publication_date="1975-01-01",
        publisher="Cambridge University Press", reliability_score=0.9,
        reliability_basis="アシャンティ研究の古典")
    src_athar_ali = add_source("secondary_literature",
        "Athar Ali, M. (1985) The Apparatus of Empire",
        authors=["M. Athar Ali"], publication_date="1985-01-01",
        publisher="Oxford University Press", reliability_score=0.9,
        reliability_basis="ムガル mansabdar 制度の決定的研究")
    src_marlowe = add_source("secondary_literature",
        "Marlowe, F. (2010) The Hadza: Hunter-Gatherers of Tanzania",
        authors=["Frank Marlowe"], publication_date="2010-01-01",
        publisher="University of California Press", reliability_score=0.9,
        reliability_basis="長期フィールドワークに基づく現代 Hadza 民族誌")
    src_whyte_mondragon = add_source("secondary_literature",
        "Whyte, W.F. & Whyte, K.K. (1991) Making Mondragón",
        authors=["William F. Whyte", "Kathleen K. Whyte"],
        publication_date="1991-01-01",
        publisher="ILR Press / Cornell", reliability_score=0.9)
    src_wmf_990 = add_source("primary_text",
        "Wikimedia Foundation IRS Form 990 filings",
        publisher="Wikimedia Foundation",
        locator={"url": "https://wikimediafoundation.org/about/financial-reports/"},
        accessed_at="2026-05-02", reliability_score=0.95,
        reliability_basis="米国非営利法人の年次税務開示文書",
        license="CC-BY-SA-3.0", redistribution="public_redistributable")
    src_konoike_history = add_source("secondary_literature",
        "宮本又次『鴻池善右衛門』(吉川弘文館, 1958)",
        authors=["宮本又次"], publication_date="1958-01-01",
        publisher="吉川弘文館", reliability_score=0.85,
        reliability_basis="鴻池家研究の標準的伝記、家所蔵文書を引用")

    # ============================================================
    # CASE 6: アシャンティ王国 (1670-1957)
    # ============================================================
    asante = add_org("アシャンティ王国 (Asante Empire)",
        alternate_names=[{"name":"Asante","lang":"en"},{"name":"Ashanti","lang":"en"},{"name":"アサンテ","lang":"ja"}],
        description="西アフリカの黄金海岸内陸部に栄えた前植民地国家。Sika Dwa Kofi (黄金の床几) を中心とする神秘的・政治的統合体で、首都クマシ周辺の州 (oman) が連合する形態。1701 年 Denkyira 戦勝で帝国化。1896 年に英領化、1957 年ガーナ独立で名目上の王権が回復。",
        geo_scope={"region":"West Africa","modern_country":"Ghana","capital":"Kumasi"},
        start_date="1670-01-01", start_date_precision="decade",
        end_date="1957-03-06", end_date_precision="exact",
        status="transformed",
        attributes={"founder":"Osei Tutu","golden_stool":"Sika Dwa Kofi",
                    "core_concept":"obi nkyere abofra Nyame (誰も子に神を教えない — 政治的正統性は伝統に内在)",
                    "subdivision":"oman (state)+ stool"},
        external_ids={"wikidata":"Q188026"})
    inserted.append(("organization", asante, "アシャンティ"))

    asante_claim = add_claim("organization", asante, "start_date", "partial",
        {"period":"c.1670-1701","note":"創立は概ね 1670 年代、帝国化は 1701 Denkyira 戦勝"},
        src_wilks, 0.85, note="単一日付ではなく形成過程")
    assign_form(asante, "historical_era", "ancient_bureaucracy", is_primary=True,
                valid_from="1701-01-01", valid_to="1896-01-31",
                confidence=0.7, claim_id=asante_claim,
                )
    assign_form(asante, "laloux_2014", "amber", confidence=0.65,
                claim_id=add_claim("organization_form_assignment", asante, "form", "partial",
                    {"reasoning":"Laloux Amber に近い (世襲・規範・神聖王権) が、コンセンサス側面 (Asantemanhyiamu 国民集会) も持つ"},
                    src_wilks, 0.65))

    act_asante_gold = add_activity(asante, "gold_trade", domain="交換",
        description="森林帯の砂金産地を掌握し、北方サヘル交易と大西洋商人の双方と取引",
        inputs={"resources":["gold dust","kola nuts","slaves"]},
        outputs={"trade_goods":["firearms","textiles","cowrie shells"]},
        orientation="exploitation",
        valid_from="1670-01-01", valid_to="1896-01-31", confidence=0.85)
    act_asante_war = add_activity(asante, "military_campaign", domain="軍事",
        description="Asante 軍は呼集制 (asafo company) で動員、1873-74 第二次 Anglo-Ashanti 戦争では 60,000 人規模",
        scale={"peak_force":60000},
        orientation="mixed",
        valid_from="1670-01-01", valid_to="1900-01-01", confidence=0.85)

    add_func(asante, "vsm_s5_policy_identity",
        mechanism={"means":["Sika Dwa Kofi (黄金の床几) が王権の物理的依代","Asantemanhyiamu (国民集会)"],
                   "note":"床几自体が国家の魂とされ、英国による奪取は禁忌"},
        confidence=0.9)
    add_func(asante, "miller_02_boundary",
        mechanism={"means":["state oath (great oath of Asante) — 違反=宗教的犯罪","oman (州) ごとの境界"]},
        confidence=0.85)
    add_func(asante, "miller_18_decider",
        mechanism={"means":["Asantehene (王) + Asantemanhyiamu","oman 単位の chief 評議会"]},
        confidence=0.85)
    add_func(asante, "miller_03_ingestor",
        mechanism={"means":["金鉱税","奴隷貿易税","属州貢納"]},
        activity_id=act_asante_gold, confidence=0.8)
    add_func(asante, "vsm_s1_operations",
        mechanism={"means":["asafo company (年齢階梯軍事組織)","各 oman の現地統治"]},
        activity_id=act_asante_war, confidence=0.8)

    add_impact(asante, "経済", "regional_trade_hub",
        {"description":"西アフリカ内陸-沿岸の金・奴隷貿易の中心","peak_period":"1700-1874"},
        "descriptive", "intergenerational",
        affected_scope={"region":"West Africa, ~1.5M sq km influence"},
        confidence=0.85)
    add_impact(asante, "文化", "cultural_continuity",
        {"description":"Akan 文化・Adinkra symbol・kente 織が現代ガーナまで継承"},
        "positive", "intergenerational", confidence=0.9)
    add_impact(asante, "政治", "anti_colonial_resistance",
        {"description":"4 度の Anglo-Ashanti 戦争 (1824-1900) で英国に組織的抵抗"},
        "descriptive", "long_term", confidence=0.9)

    e_asante_battle = add_event("founding",
        event_date="1701-01-01", event_date_precision="year",
        description="Denkyira 戦勝、Osei Tutu が初代 Asantehene として帝国を確立",
        causes={"strategic":"Komfo Anokye (司祭) による黄金の床几出現の儀礼"},
        outcomes={"new_state":"Asante Empire"},
        vsr_label="variation", confidence=0.85)
    link_eo(e_asante_battle, asante, "founder")

    e_asante_british = add_event("crisis",
        event_date="1896-01-31", event_date_precision="exact",
        description="第四次 Anglo-Ashanti 戦争で英国が Asantehene Prempeh I を流刑、保護領化",
        causes={"colonial":"英国の内陸進出"},
        outcomes={"status":"protectorate"},
        vsr_label="struggle", confidence=0.9)
    link_eo(e_asante_british, asante, "affected")

    e_asante_indep = add_event("revival",
        event_date="1957-03-06", event_date_precision="exact",
        description="ガーナ独立、Asante kingdom が文化的存在として復元",
        outcomes={"new_form":"cultural_traditional_authority"},
        vsr_label="retention", confidence=0.9)
    link_eo(e_asante_indep, asante, "revived")

    # ============================================================
    # CASE 7: ムガル朝マンサブダール制 (1571-1858)
    # ============================================================
    mansabdar = add_org("ムガル朝マンサブダール制 (Mansabdari System)",
        alternate_names=[{"name":"Mansabdari","lang":"hi"},{"name":"Mansab system","lang":"en"}],
        description="アクバル帝が 1571 年頃確立した、官位 (zat) と動員すべき騎兵数 (sawar) の二重ランクで官僚を格付けする制度。サラリーは現金ではなく徴税権 (jagir) として与えられ、官位は世襲不可。実態は階級的官僚制 + 軍事封建制のハイブリッド。",
        geo_scope={"region":"South Asia","empire":"Mughal","capital":["Agra","Delhi"]},
        start_date="1571-01-01", start_date_precision="decade",
        end_date="1858-08-02", end_date_precision="exact",
        status="extinct",
        attributes={"core_innovation":"zat (個人ランク) + sawar (騎兵数) の二重ランク",
                    "salary_form":"jagir (徴税権譲渡)",
                    "ranks":["10","20","100","500","1,000","5,000","7,000"],
                    "non_hereditary":"原則として世襲不可"},
        external_ids={"wikidata":"Q1373186"})
    inserted.append(("organization", mansabdar, "マンサブダール"))

    mansab_claim = add_claim("organization", mansabdar, "innovation", "present",
        {"feature":"二重ランク制度",
         "context":"アクバル前期の改革、1571-77 年に整備"},
        src_athar_ali, 0.9)
    assign_form(mansabdar, "historical_era", "ancient_bureaucracy", is_primary=True,
                valid_from="1571-01-01", valid_to="1858-08-02",
                confidence=0.85, claim_id=mansab_claim)

    act_mansab_admin = add_activity(mansabdar, "imperial_administration", domain="統治",
        description="徴税・軍事動員・地方裁判を mansabdar 個人が複合的に担う",
        inputs={"land_revenue":"diwani (民政) + nizamat (軍政・治安)"},
        scale={"peak_mansabdars":8000},
        orientation="exploitation",
        valid_from="1571-01-01", valid_to="1858-01-01", confidence=0.85)

    add_func(mansabdar, "miller_03_ingestor",
        mechanism={"means":["jagir (徴税権)","khalisa (皇室直轄地)"],
                   "note":"jagir は数年で別地に転換され、所領化を防ぐ"},
        activity_id=act_mansab_admin, confidence=0.9)
    add_func(mansabdar, "vsm_s3_internal_control",
        mechanism={"means":["dagh (馬の烙印登録)","chehra (兵士の人相書き)","定期査察"],
                   "purpose":"sawar 兵数が実態を反映するか検査"},
        confidence=0.9)
    add_func(mansabdar, "miller_18_decider",
        mechanism={"means":["皇帝 (Padshah) が個別 mansab を任免","wakil (宰相) が補佐"]},
        confidence=0.9)
    add_func(mansabdar, "miller_17_memory",
        mechanism={"means":["ペルシア語による行政記録 (akhbarat)","年代記 (Akbarnama, Padshahnama)"]},
        confidence=0.9)

    add_impact(mansabdar, "政治", "imperial_integration",
        {"description":"南アジア亜大陸を 250 年以上にわたって統治可能にした制度的基盤"},
        "descriptive", "intergenerational",
        affected_scope={"region":"South Asia","peak_population":"approx 100M-150M"},
        confidence=0.9)
    add_impact(mansabdar, "技術", "administrative_innovation",
        {"description":"二重ランク + 非世襲 + jagir 転換は、世襲封建制と純粋官僚制の中間として独自"},
        "positive", "long_term", confidence=0.85)

    e_mansab_founding = add_event("founding",
        event_date="1571-01-01", event_date_precision="decade",
        description="アクバル帝の改革により mansabdari 制度が体系化",
        participants={"emperor":"Akbar"},
        vsr_label="variation", confidence=0.85)
    link_eo(e_mansab_founding, mansabdar, "founder")

    e_mansab_decline = add_event("dissolution",
        event_date="1858-08-02", event_date_precision="exact",
        description="セポイの乱後、英領インド統治法によりムガル朝公式廃止",
        dissolution_cause="regulatory_dissolution",
        causes={"colonial":"British Crown Rule の確立"},
        outcomes={"successor":"British Indian Civil Service"},
        vsr_label="selection", confidence=0.95)
    link_eo(e_mansab_decline, mansabdar, "dissolved")

    # ============================================================
    # CASE 8: Hadza バンド (タンザニア)
    # ============================================================
    hadza = add_org("Hadza バンド (Hadzabe)",
        alternate_names=[{"name":"Hadza","lang":"en"},{"name":"ハッザ","lang":"ja"}],
        description="タンザニア北部 Eyasi 湖周辺に居住する現存の狩猟採集民。約 1,200-1,300 人。30-50 人規模の流動的バンドが季節的に分裂・再結合する平等主義集団。Boehm の reverse dominance hierarchy が現代に観察できる稀少例。",
        geo_scope={"region":"East Africa","country":"Tanzania","specific":"Lake Eyasi area"},
        start_date=None, start_date_precision="unknown",
        status="active",
        attributes={"population_total":"~1,200-1,300",
                    "band_size":"30-50",
                    "subsistence":"hunting + gathering (no agriculture/pastoralism)",
                    "language":"Hadzane (language isolate)",
                    "egalitarian":"Reverse Dominance Hierarchy (Boehm 1993)"},
        external_ids={"wikidata":"Q1184893"})
    inserted.append(("organization", hadza, "Hadza"))

    hadza_claim = add_claim("organization", hadza, "start_date", "inapplicable",
        {"reason":"狩猟採集バンドには『創立日』の概念が適用できない。継続的存在"},
        src_marlowe, 0.95,
        note="claim_value_kind=inapplicable の意義を実演 (Stream J 教訓)")
    assign_form(hadza, "historical_era", "hunter_gatherer_band", is_primary=True,
                confidence=0.95, claim_id=hadza_claim)

    act_hadza_hunt = add_activity(hadza, "hunting_gathering", domain="生産",
        description="男性が弓矢で狩猟、女性が球茎・蜂蜜・果実を採集。1日 4-6 時間労働",
        outputs={"food":["meat","tubers","honey","baobab","berries"]},
        scale={"daily_calories_per_capita":"~2,500-3,000"},
        orientation="exploitation",
        confidence=0.9)
    act_hadza_share = add_activity(hadza, "food_sharing", domain="互酬",
        description="獲物 (特に大型) は demand-sharing で全員に分配。蓄積を許さない強い社会的圧力",
        orientation="exploitation",
        confidence=0.95)

    add_func(hadza, "miller_04_distributor",
        mechanism={"means":["demand-sharing","逆転的支配階層による富の蓄積抑制"],
                   "note":"現代資本主義の対極にある分配機構"},
        activity_id=act_hadza_share, confidence=0.9)
    add_func(hadza, "miller_02_boundary",
        mechanism={"means":["流動的バンドメンバーシップ","親族紐帯 + 隣接バンドとの婚姻"],
                   "note":"境界は弱く、個人移動の自由度が極めて高い"},
        confidence=0.85)
    add_func(hadza, "vsm_s5_policy_identity",
        mechanism={"means":["神話・物語の共有 (Hadzane 言語)","儀礼 (epeme dance)"]},
        confidence=0.85)
    add_func(hadza, "miller_18_decider",
        mechanism={"means":["コンセンサス + ゴシップ + 嘲笑による自発的服従"],
                   "note":"中央集権なし、Boehm reverse dominance hierarchy"},
        confidence=0.95)

    add_impact(hadza, "知識", "evolutionary_baseline",
        {"description":"進化心理学・人類学において人類の祖先環境を推論する参照点"},
        "descriptive", "intergenerational",
        affected_scope={"discipline":"anthropology, evolutionary_psychology, public_health"},
        confidence=0.85)

    # ============================================================
    # CASE 9: Mondragón Corporación Cooperativa (1956-)
    # ============================================================
    mondragon = add_org("Mondragón Corporación Cooperativa (MCC)",
        alternate_names=[{"name":"Mondragon Corporation","lang":"en"},
                         {"name":"Mondragón","lang":"es"},
                         {"name":"モンドラゴン協同組合","lang":"ja"}],
        description="スペイン・バスク地方の協同組合連合。1956 年に司祭 José María Arizmendiarrieta の指導で 5 人の弟子が起業、現在は 70,000+ 名・100+ の協同組合を擁する。労働者所有、給与上限規制 (top:bottom 比 約 6.5:1)、教育・銀行・社会保障を内部化。",
        geo_scope={"hq":"Mondragón, Basque Country, Spain","operations":"global"},
        start_date="1956-01-01", start_date_precision="year",
        status="active",
        attributes={"founder":"José María Arizmendiarrieta",
                    "members_employees":"70,000+",
                    "cooperatives":"100+",
                    "pay_ratio_max":"~6.5:1",
                    "internal_bank":"Caja Laboral",
                    "education":"Mondragón University"},
        external_ids={"wikidata":"Q336268"})
    inserted.append(("organization", mondragon, "Mondragón"))

    mondragon_claim = add_claim("organization", mondragon, "governance_model", "present",
        {"model":"worker_owned_federated_cooperative","unique":"上限給与・内部銀行・教育"},
        src_whyte_mondragon, 0.9)
    assign_form(mondragon, "legal_form", "cooperative", is_primary=True,
                valid_from="1956-01-01", confidence=0.95, claim_id=mondragon_claim)
    assign_form(mondragon, "laloux_2014", "green", confidence=0.85,
                claim_id=add_claim("organization_form_assignment", mondragon, "form", "present",
                    {"reasoning":"Laloux Green: ステークホルダー型・価値駆動・分権的"},
                    src_whyte_mondragon, 0.85))

    act_mondragon_indust = add_activity(mondragon, "industrial_production", domain="生産",
        description="家電 (Fagor)、自動車部品、工作機械、建設、流通 (Eroski)",
        scale={"revenue_2023_eur":12.4e9,"employees":70000},
        orientation="exploitation",
        valid_from="1956-01-01", confidence=0.9)
    act_mondragon_finance = add_activity(mondragon, "internal_finance", domain="金融",
        description="Caja Laboral — 内部銀行、組合員からの預金で新規協同組合を融資",
        valid_from="1959-07-15", confidence=0.95)
    act_mondragon_edu = add_activity(mondragon, "cooperative_education", domain="教育",
        description="Mondragón University (1997-) と工学技術学校群、cooperativista 育成",
        orientation="exploration",
        valid_from="1943-01-01", confidence=0.95)

    add_func(mondragon, "miller_01_reproducer",
        mechanism={"means":["新規協同組合の spin-off","Mondragón University からのリーダー輩出"]},
        activity_id=act_mondragon_edu, confidence=0.9)
    add_func(mondragon, "vsm_s3_internal_control",
        mechanism={"means":["Cooperative Congress","Standing Committee","internal solidarity fund"],
                   "purpose":"組合間の資源融通とリスク共有"},
        confidence=0.9)
    add_func(mondragon, "miller_03_ingestor",
        mechanism={"means":["組合員出資 (~€15,000 加入金)","Caja Laboral 預金"]},
        activity_id=act_mondragon_finance, confidence=0.95)
    add_func(mondragon, "vsm_s5_policy_identity",
        mechanism={"means":["10 Cooperative Principles","Arizmendiarrieta の思想体系"],
                   "note":"バスク文化 + キリスト教社会教説 + 協同組合運動の融合"},
        confidence=0.9)

    add_impact(mondragon, "経済", "cooperative_scalability",
        {"description":"労働者所有協同組合が大規模 (7万人) で工業・金融・教育を統合運営できる事例として影響"},
        "positive", "long_term",
        affected_scope={"discipline":"economic democracy, alternative economics"},
        confidence=0.85)
    add_impact(mondragon, "社会", "fagor_failure",
        {"description":"2013 年に主力協同組合 Fagor (家電) が破綻、5,600 人の組合員が失業。連帯基金で補償したが Mondragón モデルの限界も露呈"},
        "negative", "medium_term",
        evaluation_method="historical_analysis",
        valid_from="2013-11-13", confidence=0.95)

    e_mondragon_founding = add_event("founding",
        event_date="1956-01-01", event_date_precision="year",
        description="ULGOR (現 Fagor) を 5 人の弟子が設立",
        participants={"founders":["Luis Usatorre","Jesús Larrañaga","Alfonso Gorroñogoitia",
                                  "José María Ormaetxea","Javier Ortubay"],
                      "mentor":"José María Arizmendiarrieta"},
        location={"city":"Mondragón, Basque Country"},
        vsr_label="variation", confidence=0.95)
    link_eo(e_mondragon_founding, mondragon, "founder")

    e_fagor_crisis = add_event("crisis",
        event_date="2013-11-13", event_date_precision="exact",
        description="Fagor Electrodomésticos が破産申請、Mondragón 史上最大の危機",
        causes={"economic":"欧州金融危機 + 中国製家電の競争"},
        outcomes={"members_displaced":5600,"solidarity_fund_used":"€300M+"},
        vsr_label="struggle", confidence=0.95)
    link_eo(e_fagor_crisis, mondragon, "affected")

    # ============================================================
    # CASE 10: Wikimedia Foundation (2003-)
    # ============================================================
    wmf = add_org("Wikimedia Foundation",
        alternate_names=[{"name":"WMF","lang":"en"},
                         {"name":"ウィキメディア財団","lang":"ja"}],
        description="2003 年設立の米国 501(c)(3) 非営利団体。Wikipedia (2001-) その他のフリーコンテンツプロジェクトを運営。資金は寄付ベース、コンテンツは編集者コミュニティ自治、技術はオープンソース MediaWiki。",
        geo_scope={"hq":"San Francisco, USA","operations":"global","languages":300},
        start_date="2003-06-20", start_date_precision="exact",
        status="active",
        attributes={"founder":"Jimmy Wales",
                    "wikipedia_articles":">60M (across languages)",
                    "monthly_active_editors":"~280,000",
                    "annual_revenue_usd":"~$170M",
                    "governance":"board (~12 members) + Trustees + global community"},
        external_ids={"wikidata":"Q180"})
    inserted.append(("organization", wmf, "Wikimedia"))

    wmf_claim = add_claim("organization", wmf, "governance_model", "present",
        {"model":"foundation+community_self_governance",
         "unique":"財団は技術・法務・募金、コンテンツ判断は edit community が自治"},
        src_wmf_990, 0.95)
    assign_form(wmf, "legal_form", "501c3_us", is_primary=True,
                valid_from="2003-06-20", confidence=0.95, claim_id=wmf_claim)
    assign_form(wmf, "mintzberg_1989", "missionary", confidence=0.85,
                claim_id=add_claim("organization_form_assignment", wmf, "form", "present",
                    {"reasoning":"規範 (NPOV、検証可能性) の標準化が支配的調整メカニズム"},
                    src_wmf_990, 0.85))

    act_wmf_host = add_activity(wmf, "platform_operation", domain="技術",
        description="MediaWiki ソフトウェア + サーバーインフラの運営、月間 ~15B PV",
        scale={"monthly_pageviews":15e9,"servers":"~1000","languages":300},
        orientation="exploitation",
        valid_from="2003-06-20", confidence=0.95)
    act_wmf_fund = add_activity(wmf, "donation_fundraising", domain="金融",
        description="読者からの小口寄付 (年間 ~$170M)、年末 banner キャンペーン",
        outputs={"annual_revenue":"~$170M","donor_count":">8M annually"},
        orientation="exploitation",
        valid_from="2003-06-20", confidence=0.95)

    add_func(wmf, "miller_02_boundary",
        mechanism={"means":["MediaWiki アカウント","コミュニティ判定 (admin/bureaucrat)","ban 制度"],
                   "note":"境界は法人ではなくコミュニティ規範で引かれる"},
        confidence=0.9)
    add_func(wmf, "miller_17_memory",
        mechanism={"means":["記事履歴 (永久保存)","talk page アーカイブ","CC-BY-SA license で再配布可"]},
        confidence=0.95)
    add_func(wmf, "miller_18_decider",
        mechanism={"means":["コンテンツ: コミュニティコンセンサス","技術/法務: 財団","紛争解決: ArbCom"]},
        confidence=0.9)
    add_func(wmf, "miller_03_ingestor",
        mechanism={"means":["寄付 (主)","grant","merchandise"]},
        activity_id=act_wmf_fund, confidence=0.95)
    add_func(wmf, "vsm_s5_policy_identity",
        mechanism={"means":["Five Pillars","Universal Code of Conduct (2021-)","CC-BY-SA"]},
        confidence=0.9)

    add_impact(wmf, "知識", "knowledge_commons",
        {"description":"Wikipedia は世界最大の汎用百科事典、300+ 言語、累計編集 ~6B"},
        "positive", "intergenerational",
        affected_scope={"users":"~2B/month"},
        confidence=0.95)
    add_impact(wmf, "技術", "open_source_governance_template",
        {"description":"巨大ボランティアコミュニティ + 財団のハイブリッド運営の参照モデル"},
        "positive", "long_term", confidence=0.85)

    e_wmf_founding = add_event("founding",
        event_date="2003-06-20", event_date_precision="exact",
        description="Wikimedia Foundation を Florida 州で 501(c)(3) として法人化",
        participants={"founder":"Jimmy Wales"},
        outcomes={"jurisdiction":"Florida → later San Francisco"},
        vsr_label="variation", confidence=0.95)
    link_eo(e_wmf_founding, wmf, "founder")

    # ============================================================
    # CASE 11: 鴻池家 (1656-1899 [近代会社化])
    # ============================================================
    konoike = add_org("鴻池家",
        alternate_names=[{"name":"Kōnoike family","lang":"en"},
                         {"name":"鴻池善右衛門家","lang":"ja"}],
        description="摂津伊丹発祥の江戸期豪商。酒造 (清酒醸造の原型を確立)、海運 (大坂-江戸航路)、両替商、大名貸へ事業を多角化。1656 年に大坂今橋に両替店開業、1899 年に第十三国立銀行 → 鴻池銀行 → 三和銀行 (現 三菱 UFJ) へ近代会社化。",
        geo_scope={"origin":"伊丹","main_hq":"大坂今橋","network":"全国 (大坂・江戸・京都・伊丹)"},
        start_date="1656-01-01", start_date_precision="year",
        end_date="1899-04-01", end_date_precision="exact",
        status="transformed",
        attributes={"founder":"鴻池善右衛門 正成",
                    "core_business":["sake_brewing","shipping","money_changing","daimyo_loans"],
                    "innovations":["清酒の製法","為替送金","大名貸の標準化"],
                    "successor":"鴻池銀行 → 三和銀行 → 三菱 UFJ"},
        external_ids={"wikidata":"Q11531538"})
    inserted.append(("organization", konoike, "鴻池家"))

    konoike_claim = add_claim("organization", konoike, "longevity_pattern", "present",
        {"pattern":"家業の連続変容","cycle":"酒造→海運→金融→近代銀行→現代メガバンクへの吸収"},
        src_konoike_history, 0.85,
        note="連続性は法人レベルではなく家業・人材・資本・暖簾の継承による")
    assign_form(konoike, "east_asian", "ie_household", is_primary=True,
                valid_from="1656-01-01", valid_to="1899-04-01",
                confidence=0.95, claim_id=konoike_claim)
    assign_form(konoike, "east_asian", "noren", confidence=0.9)
    assign_form(konoike, "legal_form", "kk_jp", valid_from="1899-04-01",
                confidence=0.9,
                claim_id=add_claim("organization_form_assignment", konoike, "form", "partial",
                    {"reasoning":"近代化後は鴻池銀行として KK 化、ただし家業レベルでの連続性も保つ"},
                    src_konoike_history, 0.85))

    act_konoike_sake = add_activity(konoike, "sake_brewing", domain="生産",
        description="伊丹で清酒醸造、江戸送りで需要拡大",
        valid_from="1600-01-01", valid_to="1700-01-01",
        orientation="exploitation", confidence=0.85)
    act_konoike_money = add_activity(konoike, "money_changing", domain="金融",
        description="大坂今橋を中心とする両替商、為替送金、大名貸",
        scale={"daimyo_clients":"100+ 大名家"},
        orientation="exploitation",
        valid_from="1656-01-01", valid_to="1899-04-01", confidence=0.9)

    add_func(konoike, "miller_01_reproducer",
        mechanism={"means":["別家制度 (大坂・江戸・京の支店長は奉公人から昇進)","家法による継承"]},
        confidence=0.9)
    add_func(konoike, "miller_17_memory",
        mechanism={"means":["大福帳","家訓 (家中条目)","奉公人台帳"]},
        confidence=0.85)
    add_func(konoike, "miller_03_ingestor",
        mechanism={"means":["酒販売益","為替手数料","大名貸利息","幕府御用金"]},
        activity_id=act_konoike_money, confidence=0.9)
    add_func(konoike, "vsm_s5_policy_identity",
        mechanism={"means":["善右衛門の名跡継承","鴻池家家訓 (1700 年代成立)"],
                   "note":"暖簾と家訓が組織同一性を担保、人格としての法人格は不在"},
        confidence=0.85)

    add_impact(konoike, "経済", "edo_financial_infrastructure",
        {"description":"江戸期の全国為替・大名貸ネットワークの中核を担い、商業資本の蓄積を可能にした"},
        "descriptive", "long_term",
        affected_scope={"region":"日本全土","period":"1656-1899"},
        confidence=0.85)
    add_impact(konoike, "技術", "sake_brewing_innovation",
        {"description":"清酒醸造法の確立、伊丹の銘柄化"},
        "positive", "long_term", confidence=0.85)

    e_konoike_founding = add_event("founding",
        event_date="1656-01-01", event_date_precision="year",
        description="鴻池善右衛門 正成が大坂今橋に両替店開業",
        location={"city":"大坂今橋"},
        vsr_label="variation", confidence=0.85)
    link_eo(e_konoike_founding, konoike, "founder")

    e_konoike_modern = add_event("reorganization",
        event_date="1899-04-01", event_date_precision="exact",
        description="鴻池銀行を株式会社として設立、家業から KK へ",
        outcomes={"new_form":"kk_jp","predecessor_form":"ie_household"},
        vsr_label="retention", confidence=0.95)
    link_eo(e_konoike_modern, konoike, "transformed")

    # ============================================================
    # 関係性 (relations)
    # ============================================================
    # アシャンティ → ムガル: 同時代の異文化的同型 (両方が複合的徴税統治)
    # → 関係を作るには同源性が必要、これは parallel evolution なので relation は付けない

    # Mondragón ← ベネディクト会: missionary structure の系譜的影響
    bene_row = cur.execute("SELECT organization_id FROM organization WHERE canonical_name LIKE 'ベネディクト会%' LIMIT 1").fetchone()
    if bene_row:
        bene_id = bene_row[0]
        cur.execute(
            """INSERT INTO relation (relation_id, source_organization_id, target_organization_id,
                relation_type, valid_from, relation_attributes, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid(), bene_id, mondragon, "mimetic_isomorphism", "1956-01-01",
             json.dumps({"transfer":"修道会の '祈り・労働・規律' の倫理が Arizmendiarrieta のキリスト教社会教説経由で Mondragón の協同組合精神に影響"}, ensure_ascii=False),
             0.5,
             add_claim("relation","pending","type","partial",
                {"reasoning":"Whyte 研究で Arizmendiarrieta の神学的背景が示唆される"},
                src_whyte_mondragon, 0.5)),
        )

    # 三井 ← 鴻池: 同時代の江戸商家コミュニティ、相互参照
    mitsui_row = cur.execute("SELECT organization_id FROM organization WHERE canonical_name LIKE '三井越後屋%' LIMIT 1").fetchone()
    if mitsui_row:
        mitsui_id = mitsui_row[0]
        cur.execute(
            """INSERT INTO relation (relation_id, source_organization_id, target_organization_id,
                relation_type, directionality, valid_from, valid_to,
                relation_attributes, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (uid(), mitsui_id, konoike, "competition", "bidirectional", "1673-01-01", "1899-04-01",
             json.dumps({"market":"両替商市場","field":"江戸-大坂為替","note":"同業ながら互いに大名貸顧客で住み分け"}, ensure_ascii=False),
             0.6,
             add_claim("relation","pending","type","partial",
                {"reasoning":"両家の文書に互いへの言及あり"},
                src_konoike_history, 0.6)),
        )

    # WMF → MakerDAO: コミュニティ自治型のオープンガバナンスとして系譜的近接
    maker_row = cur.execute("SELECT organization_id FROM organization WHERE canonical_name LIKE 'MakerDAO%' LIMIT 1").fetchone()
    if maker_row:
        maker_id = maker_row[0]
        cur.execute(
            """INSERT INTO relation (relation_id, source_organization_id, target_organization_id,
                relation_type, valid_from, relation_attributes, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (uid(), wmf, maker_id, "mimetic_isomorphism", "2017-12-18",
             json.dumps({"transfer":"コミュニティ自治型ガバナンス、寄付/トークンによる資金、透明性原則"}, ensure_ascii=False),
             0.45,
             add_claim("relation","pending","type","partial",
                {"reasoning":"DAO 文献で WMF や OSS が参照されることがあるが直接の継承を主張する文献は薄い"},
                src_wmf_990, 0.45)),
        )

    conn.commit()

    # Verification
    print("\n=== Phase 2 inserted cases ===")
    for et, eid, name in inserted:
        cur.execute("SELECT COUNT(*) FROM activity WHERE organization_id=?", (eid,))
        a = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM function_record WHERE organization_id=?", (eid,))
        f = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM impact_record WHERE organization_id=?", (eid,))
        i = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM organization_form_assignment WHERE organization_id=?", (eid,))
        fa = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM event_organization WHERE organization_id=?", (eid,))
        eo = cur.fetchone()[0]
        print(f"  {name:18s}  forms={fa} acts={a} funcs={f} impacts={i} events={eo}")

    print("\n=== aggregate counts ===")
    cur.execute("SELECT COUNT(*) FROM organization")
    print(f"organization total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM activity")
    print(f"activity total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM function_record")
    print(f"function_record total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM impact_record")
    print(f"impact_record total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM event")
    print(f"event total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM relation")
    print(f"relation total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claim")
    print(f"claim total: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM source")
    print(f"source total: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()
