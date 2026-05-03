#!/usr/bin/env python3
"""並列タスク #U: 東アジア固有形態の追加注釈 (5 ケース)

codex3 で 14 形態が列挙されたが、宗族・郷党・商幫・門中・郷約・会合衆・アメーバ
等は具体ケースが未注釈だった。本スクリプトはこの空白を埋める。

追加ケース:
  1. 山西商人ネットワーク (商幫, c.1500-1900)
     — 票号より広い同郷商人連合。Ming-Qing の 10 大商幫筆頭。鴻池家との並列
       (parallel commercial network)。
  2. 安東権氏門中 (Andong Kwon Munjung, c.10c-現存)
     — 朝鮮半島最古級の父系リネージ。族譜・祭祀・墓地共有の典型例。中国宗族
       との比較ノード (DB に zongzu の個別組織は無いため form_assignment で代替)。
  3. ベトナム郷約 (hương ước, 1464-19c)
     — Lê 朝 Hồng Đức 法典 (1464) で公式化された村落自治規約。「王の法は村の
       規に屈す」の格言で知られる。ハンザ自治都市と類比。
  4. 堺会合衆 (Sakai Egoshu, c.1530-1582)
     — 室町後期-安土期の自治商業都市。10 町を統括する豪商評議会。1582 年
       秀吉により解体。ハンザ同盟と並列 (autonomous merchant city)。
  5. 京セラ / 稲盛アメーバ経営 (Kyocera, 1959-)
     — 大組織を小集団 (アメーバ) に分割し各々を独立採算化。2010 年 JAL 再建
       (会社更生法 → 2 年 7 ヶ月で再上場) で大規模適用。Mondragón との
       mimetic 比較 (協同組合の小集団自律性 ↔ 株式会社内の小集団自律性)。

参考文献は WebSearch で実在性確認済 (Wikipedia、学術論文、Springer/Stanford 等)。
直接の一次史料は確認していないため、reliability は二次文献は 0.7-0.9、
Wikipedia 系は 0.5-0.6 に抑え、interpretation_note に「未確認/解釈」を明記する。

東アジア固有形態 (taxonomy=east_asian) として 4 つの新 form を追加:
  - shang_bang (商幫, 同郷商人連合)
  - huong_uoc (郷約, ベトナム村落規約)
  - egoshu (会合衆, 日本中世自治都市の評議会)
  - ameba_keiei (アメーバ経営, 小集団独立採算制)
門中 (munjung) は既存 form を使用。

既存ケースとの relation:
  - 山西商人 → 鴻池家: knowledge_transfer (parallel commercial network、
    実証的継承ではなく類比、confidence 低)
  - 山西商人 → 票号 (form 含意): knowledge_transfer (商幫は票号の上位母体)
  - 堺会合衆 → ハンザ同盟: mimetic (parallel 自治商業共同体、独立発生、
    比較研究上の対照)
  - 京セラ → Mondragón: mimetic (アメーバ ↔ 協同組合の小集団自律性、
    起源は独立、比較研究上の対照)
  - 安東権氏門中: 中国宗族と並列概念 (DB に宗族個別組織なし、relation 作らず)
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

    # ===== helpers =====
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

    def add_claim(et, eid, fp, vk, val, src, conf, by="claude_task_U", note=None):
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

    def ensure_form(taxonomy, code, label, definition=None, criteria=None,
                    valid_from=None, valid_to=None, notes=None):
        """既存 form があればその id を返す。無ければ新規作成。"""
        row = cur.execute(
            "SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
            (taxonomy, code)).fetchone()
        if row:
            return row[0]
        fid = uid()
        cur.execute(
            "INSERT INTO organization_form (form_id, taxonomy_name, form_code, label, "
            "definition, criteria, valid_period_from, valid_period_to, notes) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (fid, taxonomy, code, label, definition,
             json.dumps(criteria, ensure_ascii=False) if criteria else None,
             valid_from, valid_to, notes))
        return fid

    def assign_form(oid, tax, code, **kw):
        row = cur.execute("SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
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
            (eid, etype, kw.get("event_date"), kw.get("event_date_precision", "unknown"),
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
            "INSERT OR IGNORE INTO event_organization (event_organization_id, event_id, organization_id, role) VALUES (?,?,?,?)",
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

    def find_org(name_like):
        row = cur.execute(
            "SELECT organization_id FROM organization WHERE canonical_name LIKE ? LIMIT 1",
            (name_like,)).fetchone()
        return row[0] if row else None

    inserted = []

    # ============================================================
    # ステップ 0: 新 form を east_asian taxonomy に追加
    # ============================================================
    ensure_form("east_asian", "shang_bang", "商幫 (中国同郷商人連合)",
                definition="明清期に発達した、出身地 (省・府) を共有する商人ネットワーク。"
                           "票号などの個別商号を含む上位母体として機能。山西商幫・徽州商幫など。",
                criteria={"membership_basis": ["native_place", "kinship", "guild_norms"]},
                valid_from="1500-01-01", valid_to="1911-12-31",
                notes="Faure, Pomeranz らの近世中国経済史研究で扱われる")
    ensure_form("east_asian", "huong_uoc", "郷約 (ベトナム村落規約)",
                definition="ベトナム村落の自治規約。1464 年 Lê 朝 Hồng Đức 法典で公式化。"
                           "「王の法は村の規に屈す」の格言で知られる村落自治の基盤。",
                criteria={"scope": "village", "form": "written_covenant"},
                valid_from="1464-01-01", valid_to="1900-01-01",
                notes="Phan Đại Doãn, 桃木至朗らの研究")
    ensure_form("east_asian", "egoshu", "会合衆 (日本中世自治都市の評議会)",
                definition="室町後期から安土期にかけて自治都市を運営した豪商・有力町人の評議組織。"
                           "堺・博多・平野・桑名・大湊・宇治山田などに見られる。",
                criteria={"era": "muromachi_to_azuchi", "members": "wealthy_merchants"},
                valid_from="1450-01-01", valid_to="1620-01-01",
                notes="豊田武・脇田晴子・中村吉治・小葉田淳らの中世商業都市研究")
    ensure_form("east_asian", "ameba_keiei", "アメーバ経営 (Inamori Amoeba Management)",
                definition="稲盛和夫が京セラで開発した経営手法。組織を 5-50 人程度の "
                           "小集団 (アメーバ) に分割し、各々が独立採算 (時間当り採算) で "
                           "運営する。情報共有・全員参加・現場リーダー育成が特徴。",
                criteria={"unit_size": "5-50", "accounting": "time_based_per_unit",
                          "philosophy": "全員参加"},
                valid_from="1965-01-01",
                notes="JAL 再建 (2010-2012) で大規模適用。Corporate Rebels, "
                      "eurotechnology.com 等が西洋管理学に紹介")

    # ============================================================
    # ===== sources =====
    # ============================================================
    src_morck_yang = add_source("secondary_literature",
        "Morck, R. & Yang, F. (2010) The Shanxi Banks (NBER Working Paper 15884)",
        authors=["Randall Morck", "Fan Yang"], publication_date="2010-04-01",
        publisher="National Bureau of Economic Research",
        locator={"url": "https://www.nber.org/system/files/working_papers/w15884/w15884.pdf"},
        accessed_at="2026-05-02", reliability_score=0.85,
        reliability_basis="査読プレプリント、票号と山西商幫の経済組織分析",
        redistribution="public_redistributable")

    src_shanxi_wp = add_source("secondary_literature",
        "Wikipedia: Shanxi merchants",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Shanxi_merchants"},
        accessed_at="2026-05-02", reliability_score=0.55,
        reliability_basis="二次情報源、『十大商幫』記述等の出典確認は別途必要",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_pomeranz = add_source("secondary_literature",
        "Pomeranz, K. (2000) The Great Divergence",
        authors=["Kenneth Pomeranz"], publication_date="2000-01-01",
        publisher="Princeton University Press",
        reliability_score=0.85,
        reliability_basis="清代経済史の代表的研究、商幫・宗族・票号への言及あり",
        redistribution="restricted")

    src_faure = add_source("secondary_literature",
        "Faure, D. (2007) China and Capitalism: A History of Business Enterprise in Modern China",
        authors=["David Faure"], publication_date="2007-01-01",
        publisher="Hong Kong University Press",
        reliability_score=0.85,
        reliability_basis="近代中国の宗族・商幫・会館・票号の制度史的研究",
        redistribution="restricted")

    src_jokbo_paper = add_source("secondary_literature",
        "Korean Genealogy (Jokbo): Histories and Changes",
        publisher="The Review of Korean Studies",
        locator={"url": "https://accesson.kr/rks/assets/pdf/7619/journal-10-4-0.pdf"},
        accessed_at="2026-05-02", reliability_score=0.75,
        reliability_basis="韓国学の査読誌、族譜・門中の制度史",
        redistribution="attribution_required")

    src_lim_munjung = add_source("secondary_literature",
        "Lim, J. 'The Structure and Functions of Munjung in Korea' (J-STAGE)",
        authors=["Jaegyu Lim"],
        publisher="Japan Sociological Society / J-STAGE",
        locator={"url": "https://www.jstage.jst.go.jp/article/jrs/5/1/5_45/_article"},
        accessed_at="2026-05-02", reliability_score=0.8,
        reliability_basis="査読論文、門中の小門中-大門中構造の分析",
        redistribution="attribution_required")

    src_andong_kwon_wp = add_source("secondary_literature",
        "Wikidata / Wikipedia (ko/ja): Andong Kwon clan",
        publisher="Wikidata / Wikipedia",
        locator={"wikidata": "Q6821897"},
        accessed_at="2026-05-02", reliability_score=0.5,
        reliability_basis="氏族起源の伝説的部分を含む、二次情報源",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_huong_uoc_law = add_source("secondary_literature",
        "Vietnam Law Magazine: Huong uoc and the village rituals",
        publisher="Vietnam Law Magazine",
        locator={"url": "https://vietnamlawmagazine.vn/huong-uoc-and-the-village-rituals-4163.html"},
        accessed_at="2026-05-02", reliability_score=0.6,
        reliability_basis="法制誌の解説記事、Hồng Đức 法典 (1464) への言及あり",
        redistribution="attribution_required")

    src_phan_dai_doan = add_source("secondary_literature",
        "Phan Đại Doãn, Vietnamese Village Studies (referenced in scholarship)",
        authors=["Phan Đại Doãn"],
        reliability_score=0.7,
        reliability_basis="ベトナム郷約・村落研究の代表的研究者。原典未確認、二次引用",
        redistribution="restricted")

    src_jjarchaeology = add_source("secondary_literature",
        "Japanese medieval trading towns: Sakai and Tosaminato (Journal of Japanese Archaeology)",
        publication_date="2016-01-01",
        publisher="Journal of Japanese Archaeology",
        locator={"url": "https://www.jjarchaeology.jp/contents/pdf/vol003/3-2_089-116.pdf"},
        accessed_at="2026-05-02", reliability_score=0.8,
        reliability_basis="査読学術誌、堺・十三湊の中世考古学的研究")

    src_sakai_wp = add_source("secondary_literature",
        "Wikipedia: Sakai / Egoshu",
        publisher="Wikipedia / Japanese Wiki Corpus",
        locator={"urls": ["https://en.wikipedia.org/wiki/Sakai",
                          "https://www.japanesewiki.com/history/Egoshu.html"]},
        accessed_at="2026-05-02", reliability_score=0.55,
        reliability_basis="二次情報源、原典 (会合衆名簿等) への言及はあるが直接確認していない",
        license="CC-BY-SA-4.0", redistribution="attribution_required")

    src_toyoda = add_source("secondary_literature",
        "豊田武『日本中世商業発達史の研究』 (referenced)",
        authors=["豊田武"],
        publication_date="1952-01-01",
        reliability_score=0.8,
        reliability_basis="日本中世商業史の古典的研究。原典未確認、二次引用レベル",
        redistribution="restricted")

    src_inamori_jal = add_source("secondary_literature",
        "Reviving Japan Airlines (2010): Transplanting Kyocera Philosophy and Amoeba Management",
        publisher="Kyocera / Inamori Archive",
        locator={"url": "https://global.kyocera.com/inamori/archive/episode/episode-18.html"},
        accessed_at="2026-05-02", reliability_score=0.6,
        reliability_basis="京セラ公式アーカイブ、自社視点の整理。客観性は割引",
        redistribution="attribution_required")

    src_inamori_book = add_source("secondary_literature",
        "稲盛和夫『アメーバ経営』 (2006)",
        authors=["稲盛和夫"], publication_date="2006-01-01",
        publisher="日本経済新聞出版",
        reliability_score=0.75,
        reliability_basis="創業者自身による経営手法の体系化。一次自記述として価値、客観評価は別途必要",
        redistribution="restricted")

    src_corp_rebels = add_source("web",
        "Corporate Rebels: Scaling Up with Amoeba Management",
        publisher="Corporate Rebels",
        locator={"url": "https://www.corporate-rebels.com/blog/amoeba-management"},
        accessed_at="2026-05-02", reliability_score=0.5,
        reliability_basis="経営ブログ、欧米でのアメーバ経営紹介。学術的根拠は限定的",
        redistribution="attribution_required")

    src_eurotech = add_source("web",
        "Inamori rebuilds JAL using Amoeba Management (eurotechnology.com)",
        publisher="eurotechnology.com",
        locator={"url": "https://www.eurotechnology.com/2012/11/29/kazuo-inamori-founder-of-kyocera-ddi-kddi-turnround-of-japan-airlines/"},
        accessed_at="2026-05-02", reliability_score=0.5,
        reliability_basis="業界ブログ、二次情報源",
        redistribution="attribution_required")

    # ============================================================
    # CASE U-1: 山西商人ネットワーク (商幫)
    # ============================================================
    shanxi = add_org(
        "山西商人ネットワーク (Shanxi Merchants / Jin Shang)",
        alternate_names=[
            {"name": "Shanxi merchants", "lang": "en"},
            {"name": "Jin shang", "lang": "en"},
            {"name": "晉商 / 山西商幫", "lang": "zh"},
            {"name": "山西商幫", "lang": "ja"},
        ],
        description="明清期 (16-20 世紀初頭) に栄えた、山西省出身者を結ぶ広域商人ネットワーク。"
                    "塩・茶・絹・金融 (票号) を扱い、十大商幫の筆頭とされる。同郷性 (native-place)・"
                    "宗族・会館を結合の基礎とし、個別商号 (票号・商号) を超えた上位母体として機能。"
                    "辛亥革命前後 (1911-) に衰退し、近代銀行に置き換わる。",
        geo_scope={"origin": "Shanxi province", "operations": ["北京", "天津", "張家口", "蒙古", "ロシア", "中央アジア"]},
        start_date="1500-01-01", start_date_precision="century",
        end_date="1920-01-01", end_date_precision="century",
        status="extinct",
        attributes={
            "rank_in_ten_merchant_groups": 1,
            "core_industries": ["salt", "tea", "remittance/finance", "silk"],
            "membership_basis": ["native_place", "kinship", "huiguan_membership"],
            "longevity_years_approx": 400,
        },
        external_ids={"wikidata": "Q1146891"})
    inserted.append(("organization", shanxi, "山西商人"))

    shanxi_claim = add_claim("organization", shanxi, "start_date", "partial",
        {"period": "Ming mid-period to Qing", "context": "明中期に他商幫と並び『十大商幫』の筆頭として顕在化。明確な創立年は無い"},
        src_morck_yang, 0.7,
        note="ネットワークとしての商幫に正確な開始日は存在しない。明中期 (16c) を概略の起点とする慣行に従う")

    assign_form(shanxi, "east_asian", "shang_bang", is_primary=True,
                valid_from="1500-01-01", valid_to="1920-01-01",
                confidence=0.85, claim_id=shanxi_claim)
    assign_form(shanxi, "east_asian", "huiguan",
                confidence=0.8,
                claim_id=add_claim("organization_form_assignment", shanxi, "form", "present",
                    {"reasoning": "山西商人は各地で会館 (山西会館・山陝会館) を建立、商幫と会館は不可分"},
                    src_faure, 0.85))
    assign_form(shanxi, "east_asian", "piaohao",
                valid_from="1820-01-01", valid_to="1920-01-01",
                confidence=0.85,
                claim_id=add_claim("organization_form_assignment", shanxi, "form", "partial",
                    {"reasoning": "票号は山西商幫の一部分野 (送金・為替) であり、商幫全体ではない"},
                    src_morck_yang, 0.85,
                    note="商幫 ⊃ 票号 という包含関係"))

    act_shanxi_salt = add_act(shanxi, "long_distance_trade", domain="交換",
        description="塩 (官許塩商)・茶 (蒙古・ロシア向け)・絹の長距離交易。明初の開中法により北辺塞防のための塩運送を獲得",
        outputs={"goods": ["salt", "tea", "silk"], "routes": ["晋蒙茶路 (晋蒙茶葉之路)"]},
        orientation="exploitation",
        valid_from="1500-01-01", valid_to="1900-01-01", confidence=0.85)

    act_shanxi_finance = add_act(shanxi, "remittance_finance", domain="金融",
        description="19 世紀に票号 (山西票号) を派生させ、清朝官府の送金・地方財政の決済を担う",
        outputs={"innovation": "支店間送金ネットワーク"},
        scale={"piaohao_count_peak_approx": 30},
        orientation="exploration",
        valid_from="1820-01-01", valid_to="1920-01-01", confidence=0.85)

    add_func(shanxi, "miller_13_channel_and_net",
        mechanism={"means": ["同郷者間の信用紹介", "会館間の通信", "故郷との文書通信"]},
        confidence=0.85)
    add_func(shanxi, "miller_02_boundary",
        mechanism={"means": ["山西出身であること", "宗族・地縁の身元保証", "排除 (除名) 制裁"]},
        confidence=0.85)
    add_func(shanxi, "miller_17_memory",
        mechanism={"means": ["票号の帳簿システム", "商号の家訓・店規", "族譜"]},
        confidence=0.8)
    add_func(shanxi, "vsm_s2_coordination",
        mechanism={"means": ["会館の会則", "業界慣行 (商埠 ・牙行)", "同郷者間の評判"]},
        confidence=0.8)

    add_imp(shanxi, "経済", "premodern_finance_network",
        {"description": "20 世紀以前の中国における広域信用・送金ネットワークの基幹"},
        "positive", "long_term",
        evaluation_method="historical_interpretation", confidence=0.85)
    add_imp(shanxi, "経済", "decline_with_modern_banking",
        {"description": "辛亥革命後 (1911-) に近代銀行・国家銀行制度に置換され衰退"},
        "negative", "long_term",
        evaluation_method="historical_interpretation", confidence=0.85)

    e_shanxi_decline = add_event("dissolution",
        event_date="1920-01-01", event_date_precision="century",
        description="辛亥革命・近代銀行・軍閥混戦により山西票号と商幫が事実上解体",
        dissolution_cause="obsolescence",
        causes={"political": "辛亥革命 1911", "institutional": "近代銀行・中央銀行制度",
                "war": "軍閥混戦・日中戦争"},
        vsr_label="selection", confidence=0.85)
    link_eo(e_shanxi_decline, shanxi, "dissolved")

    # ============================================================
    # CASE U-2: 安東権氏門中
    # ============================================================
    andong_kwon = add_org(
        "安東権氏門中 (Andong Kwon Munjung)",
        alternate_names=[
            {"name": "Andong Kwon clan", "lang": "en"},
            {"name": "안동 권씨", "lang": "ko"},
            {"name": "安東權氏", "lang": "ko"},
        ],
        description="高麗初期 (10c) に新羅金氏から分かれた、慶尚北道安東を本貫とする父系リネージ組織。"
                    "始祖は太祖王建から「権」の姓を賜ったとされる権幸 (旧名 金幸)。族譜・祠堂・墓地・"
                    "祭祀を共有し、現代韓国まで継承される代表的な大門中の一つ。"
                    "Lim (J-STAGE) の小門中-大門中の同心円構造の典型例。",
        geo_scope={"origin": "Andong, North Gyeongsang", "spread": ["Korean peninsula", "diaspora"]},
        start_date="0930-01-01", start_date_precision="century",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "founder_legendary": "권행 (Kwon Haeng) — 旧名 金幸",
            "longevity_years_approx": "1100+",
            "structure": "small_munjung within large_munjung (同心円)",
            "core_practices": ["族譜 (jokbo)", "祭祀 (charye)", "祠堂", "門中財産"],
        },
        external_ids={"wikidata": "Q6821897"})
    inserted.append(("organization", andong_kwon, "安東権氏門中"))

    ak_claim = add_claim("organization", andong_kwon, "founding_legend", "partial",
        {"date_range": "circa 930", "context": "始祖伝承は高麗太祖期、史料的に確実な範囲は遅れる"},
        src_andong_kwon_wp, 0.5,
        note="始祖伝承部分を含む。族譜による系譜記述自体は近世以降に整備された")

    assign_form(andong_kwon, "east_asian", "munjung", is_primary=True,
                valid_from="0930-01-01",
                confidence=0.9, claim_id=ak_claim)

    add_act(andong_kwon, "ancestral_ritual", domain="儀礼",
        description="始祖・中始祖・高祖父までの祭祀 (時祭・忌祭・茶礼)。門中所有の祠堂・墓地で実施",
        orientation="exploitation", confidence=0.9)
    add_act(andong_kwon, "genealogical_record_keeping", domain="記憶",
        description="族譜 (jokbo) の編纂・改訂。父系男子を網羅的に記録",
        outputs={"document": "안동권씨족보"},
        orientation="exploitation", confidence=0.9)
    add_act(andong_kwon, "communal_property_management", domain="経済",
        description="位土 (祭祀のための共有耕地)・墓位田・門中財産の運営",
        orientation="exploitation", confidence=0.8)

    add_func(andong_kwon, "miller_01_reproducer",
        mechanism={"means": ["父系出生による自動成員化", "族譜への登録", "養子制度"]},
        confidence=0.9)
    add_func(andong_kwon, "miller_17_memory",
        mechanism={"means": ["族譜 (jokbo)", "祠堂の位牌", "墓誌・行状"]},
        confidence=0.95)
    add_func(andong_kwon, "miller_02_boundary",
        mechanism={"means": ["父系血縁", "本貫 (安東)", "族譜への登録の有無"]},
        confidence=0.9)
    add_func(andong_kwon, "vsm_s5_policy_identity",
        mechanism={"means": ["始祖伝承", "家訓・宗約", "儒教的孝の倫理"]},
        confidence=0.85)

    add_imp(andong_kwon, "文化", "lineage_continuity",
        {"description": "1000 年以上にわたる父系継承の連続性 — 韓国の血縁ネットワーク文化の典型"},
        "descriptive", "intergenerational",
        evaluation_method="historical_interpretation", confidence=0.85,
        affected_scope={"region": "korea"})
    add_imp(andong_kwon, "経済", "communal_landholding",
        {"description": "門中財産 (位土・墓位田) による共有不動産管理 — 近代私有制との緊張"},
        "descriptive", "long_term", confidence=0.7)

    # ============================================================
    # CASE U-3: ベトナム郷約 (hương ước)
    # ============================================================
    huong_uoc = add_org(
        "ベトナム郷約 (hương ước)",
        alternate_names=[
            {"name": "hương ước", "lang": "vi"},
            {"name": "village covenant", "lang": "en"},
            {"name": "鄉約", "lang": "vi-han"},
        ],
        description="ベトナム村落の自治規約。1464 年 Lê 朝 Hồng Đức 法典 (Hồng Đức thiện chính thư) で"
                    "公式化されたが、慣習としては既に存在。各村ごとに独自の規約を制定し、祭礼・農業暦・"
                    "公田管理・婚姻・葬送・刑罰などを規定。「王の法は村の規に屈す (Phép vua thua lệ làng)」"
                    "の格言で知られる村落自治の基盤。Nguyễn 朝 (1802-1945) を経て植民地期に変容、現代まで断続。",
        geo_scope={"region": "Vietnam (especially Red River Delta)", "scale": "village"},
        start_date="1464-01-01", start_date_precision="year",
        end_date="1945-01-01", end_date_precision="century",
        status="transformed",
        attributes={
            "formalization_year": 1464,
            "source_code": "Hồng Đức thiện chính thư",
            "scope": "village-level autonomy",
            "domains": ["agriculture", "ritual", "marriage", "funerals", "petty_justice", "公田 (công điền)"],
        },
        external_ids=None)
    inserted.append(("organization", huong_uoc, "ベトナム郷約"))

    hu_claim = add_claim("organization", huong_uoc, "formalization", "present",
        {"date": "1464", "context": "Lê Thánh Tông (Hồng Đức 帝) の法典編纂で郷約が公的承認"},
        src_huong_uoc_law, 0.7,
        note="慣習自体はそれ以前から存在。1464 年は公式化の年であり創始ではない")

    assign_form(huong_uoc, "east_asian", "huong_uoc", is_primary=True,
                valid_from="1464-01-01", valid_to="1945-01-01",
                confidence=0.85, claim_id=hu_claim)

    add_act(huong_uoc, "village_self_governance", domain="統治",
        description="村落内の祭礼・農業・婚姻・葬送・小規模紛争を村自身の規約で処理",
        orientation="exploitation",
        valid_from="1464-01-01", valid_to="1945-01-01", confidence=0.85)
    add_act(huong_uoc, "ritual_management", domain="儀礼",
        description="đình (村社) での祭礼・成丁式・選挙の運営",
        orientation="exploitation", confidence=0.85)

    add_func(huong_uoc, "vsm_s5_policy_identity",
        mechanism={"means": ["成文化された郷約 (lệ làng)", "đình に保管される規約文書",
                             "格言『王の法は村の規に屈す』"]},
        confidence=0.85)
    add_func(huong_uoc, "miller_02_boundary",
        mechanism={"means": ["村籍 (公田の分配対象)", "外来者 (ngụ cư) と土着者 (chính cư) の区別"]},
        confidence=0.85)
    add_func(huong_uoc, "vsm_s2_coordination",
        mechanism={"means": ["長老会 (Hội đồng kỳ mục)", "里長 (lý trưởng)",
                             "公田分配サイクル"]},
        confidence=0.8)
    add_func(huong_uoc, "miller_17_memory",
        mechanism={"means": ["郷約文書", "村社碑文", "đình の記録"]},
        confidence=0.75)

    add_imp(huong_uoc, "政治", "village_autonomy",
        {"description": "前近代ベトナムにおける村落の準主権 — 国家権力の浸透を制約した制度的緩衝"},
        "descriptive", "long_term",
        evaluation_method="historical_interpretation", confidence=0.85)
    add_imp(huong_uoc, "経済", "communal_field_redistribution",
        {"description": "公田 (công điền) の周期的再分配 — 私有地化への抵抗装置として機能"},
        "positive", "long_term", confidence=0.75,
        affected_scope={"region": "Red River Delta"})

    e_huong_formalization = add_event("founding",
        event_date="1464-01-01", event_date_precision="year",
        description="Lê Thánh Tông (Hồng Đức 帝) が Hồng Đức thiện chính thư で郷約を公式制度として承認",
        causes={"political": "中央集権化と村落慣習の調整",
                "ideology": "儒教的礼治の浸透"},
        outcomes={"institution": "郷約の文書化義務",
                  "principle": "村落自治の法的基盤"},
        location={"country": "大越 (Đại Việt)"},
        vsr_label="retention", confidence=0.7)
    link_eo(e_huong_formalization, huong_uoc, "transformed")

    # ============================================================
    # CASE U-4: 堺会合衆
    # ============================================================
    sakai = add_org(
        "堺会合衆 (Sakai Egoshu)",
        alternate_names=[
            {"name": "Sakai egoshu", "lang": "en"},
            {"name": "堺の会合衆", "lang": "ja"},
            {"name": "Kaigōshu", "lang": "en"},
        ],
        description="室町後期-安土期 (c.1530-1582) に堺の自治を担った 10 人前後の豪商評議会。"
                    "10 町に分かれた市街を統括し、堀と木戸で囲まれた濠を防衛、明・琉球・南蛮との貿易、"
                    "鉄砲・刀剣・塩・畳表の生産・流通を管理。Notoya・Beniya・今井宗久・千利休 (の係累) "
                    "等が成員。1568 年信長による矢銭要求、1582 年秀吉による解体で自治終焉。"
                    "ヨーロッパ中世自由都市と類比可能とされる稀有な日本の事例。",
        geo_scope={"city": "Sakai (摂泉国境)", "trade_partners": ["Ming China", "Ryukyu", "Portuguese", "Spanish"]},
        start_date="1530-01-01", start_date_precision="decade",
        end_date="1582-01-01", end_date_precision="year",
        status="extinct",
        attributes={
            "council_size_approx": 10,
            "districts": 10,
            "population_peak_approx": 40000,
            "key_industries": ["鉄砲鋳造", "刀剣", "塩", "畳表", "南蛮貿易"],
            "comparable_to": "European medieval free cities (Hansa, Italian communes)",
        },
        external_ids={"wikidata": "Q1066427"})
    inserted.append(("organization", sakai, "堺会合衆"))

    sakai_claim = add_claim("organization", sakai, "active_period", "partial",
        {"period_approx": "1530s-1582", "context": "1530 年代に自治体制が固まる、1582 年秀吉により解体"},
        src_sakai_wp, 0.65,
        note="自治の正確な始期は史料により幅がある。一次史料は会合衆名簿等が断片的")

    assign_form(sakai, "east_asian", "egoshu", is_primary=True,
                valid_from="1530-01-01", valid_to="1582-01-01",
                confidence=0.85, claim_id=sakai_claim)
    # 中世商業都市としての側面 (medieval_guild は近い概念だが厳密一致ではない)
    assign_form(sakai, "historical_era", "medieval_guild",
                confidence=0.5,
                claim_id=add_claim("organization_form_assignment", sakai, "form", "partial",
                    {"reasoning": "ヨーロッパ medieval_guild との類比は研究文献で頻繁に行われるが、"
                                  "厳密には『都市自治体 + 商人評議会』であって職能別ギルドとは異なる"},
                    src_jjarchaeology, 0.5,
                    note="taxonomies の便宜的マッピング、本質は egoshu 形態"))

    add_act(sakai, "long_distance_trade", domain="交換",
        description="勘合貿易・南蛮貿易・琉球貿易。鉄砲・絹・薬種・砂糖を扱う",
        outputs={"goods": ["firearms", "silk", "medicines", "sugar"]},
        orientation="exploitation",
        valid_from="1530-01-01", valid_to="1582-01-01", confidence=0.85)
    add_act(sakai, "weapons_manufacturing", domain="生産",
        description="鉄砲鋳造の最大拠点の一つ。種子島伝来 (1543) 後、堺鉄砲が戦国大名間で需要拡大",
        orientation="exploration",
        valid_from="1543-01-01", valid_to="1582-01-01", confidence=0.85)
    add_act(sakai, "city_defense_governance", domain="統治",
        description="堀・木戸・櫓による物理的防衛、会合衆による行政・徴税・紛争調停",
        orientation="exploitation",
        valid_from="1530-01-01", valid_to="1582-01-01", confidence=0.8)

    add_func(sakai, "miller_18_decider",
        mechanism={"means": ["会合衆の合議", "10 町ごとの代表者"]},
        confidence=0.85)
    add_func(sakai, "miller_02_boundary",
        mechanism={"means": ["濠 (堀)", "木戸 (夜閉)", "町人身分"]},
        confidence=0.85)
    add_func(sakai, "vsm_s2_coordination",
        mechanism={"means": ["10 町間の調整", "町年寄を介した日常運営"]},
        confidence=0.8)
    add_func(sakai, "miller_03_ingestor",
        mechanism={"means": ["関税相当の入市料", "商工業者からの賦課金", "矢銭 (戦時拠出)"]},
        confidence=0.7)

    add_imp(sakai, "経済", "premodern_autonomous_commercial_city",
        {"description": "日本史上稀な、欧州自由都市と比較可能な水準の自治都市。中世末の商業繁栄の象徴"},
        "positive", "long_term",
        evaluation_method="historical_interpretation", confidence=0.8)
    add_imp(sakai, "技術", "firearms_diffusion",
        {"description": "種子島伝来後、堺・国友・根来と並ぶ鉄砲量産拠点として戦国期軍事革命を支えた"},
        "descriptive", "long_term", confidence=0.85)

    e_sakai_dissol = add_event("dissolution",
        event_date="1582-01-01", event_date_precision="year",
        description="本能寺の変後、秀吉が堺を直轄化。商人を大坂に移転させ会合衆自治を解体",
        dissolution_cause="political_purge",
        causes={"political": "豊臣政権の中央集権化",
                "economic": "大坂への商業集約戦略"},
        outcomes={"successor_city": "大坂"},
        vsr_label="selection", confidence=0.85)
    link_eo(e_sakai_dissol, sakai, "dissolved")

    # ============================================================
    # CASE U-5: 京セラ (アメーバ経営)
    # ============================================================
    kyocera = add_org(
        "京セラ (Kyocera Corporation)",
        alternate_names=[
            {"name": "Kyocera Corporation", "lang": "en"},
            {"name": "京都セラミック", "lang": "ja"},
            {"name": "Kyoto Ceramic", "lang": "en"},
        ],
        description="1959 年に稲盛和夫が京都で創業した電子部品 (ファインセラミック)・通信機器メーカー。"
                    "稲盛が開発した「アメーバ経営」(組織を 5-50 人の独立採算小集団に分割) で知られる。"
                    "1984 年に第二電電 (DDI、後の KDDI) を創業。2010 年に稲盛が無報酬で JAL 会長に就任、"
                    "アメーバ経営を移植して 2 年 7 ヶ月で再上場 (世界航空業の最短再生記録)。",
        geo_scope={"hq": "Kyoto", "operations": "global"},
        start_date="1959-04-01", start_date_precision="exact",
        end_date=None, end_date_precision=None,
        status="active",
        attributes={
            "founder": "稲盛和夫 (Kazuo Inamori, 1932-2022)",
            "founding_capital": "3 million yen (8 founders)",
            "core_innovations": ["アメーバ経営", "時間当り採算", "京セラフィロソフィ"],
            "spinoff": "DDI (1984) → KDDI",
            "applied_to_jal": True,
            "longevity_years": "65+",
        },
        external_ids={"wikidata": "Q336675"})
    inserted.append(("organization", kyocera, "京セラ"))

    kyocera_claim = add_claim("organization", kyocera, "founding", "present",
        {"date": "1959-04-01", "founder": "稲盛和夫", "context": "京都セラミック株式会社として登記"},
        src_inamori_jal, 0.75)

    assign_form(kyocera, "east_asian", "ameba_keiei", is_primary=True,
                valid_from="1965-01-01",
                confidence=0.9, claim_id=kyocera_claim)
    assign_form(kyocera, "legal_form", "kk_jp",
                valid_from="1959-04-01",
                confidence=0.95)
    assign_form(kyocera, "historical_era", "u_form",
                confidence=0.5,
                claim_id=add_claim("organization_form_assignment", kyocera, "form", "partial",
                    {"reasoning": "事業部制 (multi-divisional) に近いが、アメーバ経営による更に細分化された"
                                  "独立採算は M-form/U-form 二分法に収まらない"},
                    src_inamori_book, 0.5,
                    note="Chandler 流の M-form/U-form ではなく、より下位レベルでの独立採算"))

    add_act(kyocera, "manufacturing_fineceramic", domain="生産",
        description="ファインセラミック・電子デバイス・半導体パッケージ等の製造",
        orientation="exploration",
        valid_from="1959-04-01", confidence=0.95)
    add_act(kyocera, "amoeba_management_practice", domain="統治",
        description="組織を 5-50 人のアメーバ (独立採算単位) に分割。各アメーバは時間当り採算で評価",
        outputs={"output_metric": "時間当り採算 (jikan_atari_saisan)"},
        orientation="exploration",
        valid_from="1965-01-01", confidence=0.85)

    add_func(kyocera, "vsm_s1_operations",
        mechanism={"means": ["小集団 (アメーバ) ごとの完結した PDCA",
                             "アメーバリーダーの独立採算責任"]},
        confidence=0.85)
    add_func(kyocera, "miller_18_decider",
        mechanism={"means": ["アメーバ単位の採算会議",
                             "経営方針はトップダウンだが現場意思決定は分権"]},
        confidence=0.8)
    add_func(kyocera, "miller_12_internal_transducer",
        mechanism={"means": ["時間当り採算表 (日次/月次)", "全員参加の経営会議"],
                   "note": "情報共有による全員参加経営"},
        confidence=0.8)
    add_func(kyocera, "vsm_s5_policy_identity",
        mechanism={"means": ["京セラフィロソフィ (78 ヶ条)", "稲盛経営学",
                             "『心を高める、経営を伸ばす』"]},
        confidence=0.85)
    add_func(kyocera, "miller_01_reproducer",
        mechanism={"means": ["アメーバの分裂・分社", "DDI (1984) のスピンオフ",
                             "JAL への手法移植 (2010)"]},
        confidence=0.85)

    add_imp(kyocera, "経済", "amoeba_management_diffusion",
        {"description": "アメーバ経営手法は 1000 社以上 (京セラコミュニケーションシステム経由) に導入"},
        "positive", "long_term",
        evaluation_method="industry_reports", confidence=0.55,
        affected_scope={"region": "Japan + Asia"})
    add_imp(kyocera, "経済", "jal_turnaround",
        {"description": "JAL は 2010 年 1 月会社更生法申請 (負債 2.3 兆円、戦後最大規模) → 稲盛会長就任 → "
                        "1 年で営業利益 1884 億円 → 2012 年 9 月再上場 (2 年 7 ヶ月)"},
        "positive", "medium_term",
        evaluation_method="financial_records", confidence=0.85,
        valid_from="2010-01-19", valid_to="2012-09-19",
        affected_scope={"target": "JAL", "industry": "civil_aviation"})

    e_kyocera_founding = add_event("founding",
        event_date="1959-04-01", event_date_precision="exact",
        description="京都市内の倉庫を借りて京都セラミック株式会社を 8 名で設立",
        causes={"individual": "稲盛和夫の松風工業からの独立",
                "industry": "電子部品需要の拡大"},
        location={"city": "Kyoto"},
        vsr_label="variation", confidence=0.9)
    link_eo(e_kyocera_founding, kyocera, "founder")

    e_jal_appointment = add_event("governance_change",
        event_date="2010-02-01", event_date_precision="year",
        description="稲盛和夫が政府要請を受け JAL 会長に無報酬で就任、アメーバ経営を移植",
        causes={"political": "民主党政権・企業再生支援機構の要請",
                "individual": "稲盛の社会的責任観"},
        outcomes={"strategy": "アメーバ経営 + 京セラフィロソフィの全社移植"},
        vsr_label="variation", confidence=0.85)
    link_eo(e_jal_appointment, kyocera, "actor")

    e_jal_relisting = add_event("ipo",
        event_date="2012-09-19", event_date_precision="exact",
        description="JAL が東京証券取引所一部に再上場 (2 年 7 ヶ月)、世界航空業の最短再生記録",
        outcomes={"financial": "再上場時時価総額 6500 億円規模",
                  "method": "アメーバ経営の有効性検証"},
        vsr_label="retention", confidence=0.9)
    link_eo(e_jal_relisting, kyocera, "actor")

    # ============================================================
    # 既存ケースとの relation
    # ============================================================
    # 山西商人 → 鴻池家: 並列商業ネットワーク (parallel commercial network)
    # 直接の継承は無いが、東アジアにおける同郷+宗族+信用ネットワーク型商業組織として比較対象
    konoike = find_org("%鴻池家%")
    if konoike:
        rel_claim = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "両者は独立に発生した東アジア型商業ネットワーク。直接の知識移転史料は無いが、"
                          "(1) 同郷/宗族を成員資格基盤とする (2) 為替・送金を扱う (3) 国家公権力との癒着 "
                          "(山西は塩・官府送金、鴻池は大名貸) という構造的並列性が研究文献で指摘される"},
            src_pomeranz, 0.5,
            note="比較研究上の対照であり、直接的な制度的影響は確認されていない")
        add_relation(shanxi, konoike, "knowledge_transfer",
            directionality="undirected",
            valid_from="1670-01-01", valid_to="1900-01-01",
            relation_attributes={"transfer_type": "structural_parallel",
                                 "shared_features": ["native_place_basis", "money_exchange",
                                                     "state_finance", "long_lived_household_continuity"]},
            confidence=0.45,
            strength=0.3, strength_basis="比較研究上の構造的並列、直接継承証拠なし",
            claim_id=rel_claim)

    # 堺会合衆 → ハンザ同盟: 並列自治商業共同体 (mimetic ではないが比較対象)
    # 厳密には mimetic_isomorphism は事後的継承でしか使わないが、研究文献での対比という限定的意味で
    # knowledge_transfer (parallel) を使う
    hansa = find_org("%ハンザ同盟%")
    if hansa:
        rel_claim2 = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "両者は独立発生した中世末期の自治商業共同体。研究文献では『日本のハンザ』"
                          "『東洋のヴェネツィア』として頻繁に対比される。共通点: (1) 商人評議会による統治 "
                          "(2) 物理的境界 (堀・濠・kontor) (3) 国家への準独立 (4) 国家統合により消滅"},
            src_jjarchaeology, 0.55,
            note="研究文献における比較対象、直接の歴史的接触ではない")
        add_relation(sakai, hansa, "knowledge_transfer",
            directionality="undirected",
            valid_from="1530-01-01", valid_to="1582-01-01",
            relation_attributes={"transfer_type": "structural_parallel",
                                 "shared_features": ["merchant_council_governance", "fortified_perimeter",
                                                     "quasi_sovereign", "absorbed_by_emergent_state"]},
            confidence=0.4,
            strength=0.25, strength_basis="比較研究上の対比、独立発生",
            claim_id=rel_claim2)

    # 京セラ → Mondragón: mimetic 比較 (協同組合の小集団自律性 ↔ アメーバの小集団自律性)
    mondragon = find_org("%Mondragón%")
    if mondragon:
        rel_claim3 = add_claim("relation", "pending", "type", "partial",
            {"reasoning": "両者は組織理論的に類似するが起源は独立。共通点: (1) 5-50 人規模の自律的小集団"
                          " (2) 全員参加・現場主導 (3) 創業者個人 (Arizmendiarrieta vs 稲盛) のフィロソフィに依拠 "
                          "(4) 大組織化しても小集団自律性を維持。相違: 株式会社 vs 協同組合の所有形態"},
            src_inamori_book, 0.4,
            note="比較組織論の対照、直接の知識移転は確認されていない")
        add_relation(kyocera, mondragon, "mimetic_isomorphism",
            directionality="undirected",
            valid_from="1965-01-01",
            relation_attributes={"transfer_type": "structural_parallel",
                                 "shared_features": ["small_unit_autonomy", "founder_philosophy",
                                                     "scale_with_decentralization"],
                                 "differences": ["corporate vs cooperative ownership"]},
            confidence=0.35,
            strength=0.25, strength_basis="比較組織論レベル、直接継承証拠なし",
            claim_id=rel_claim3)

    # 京セラ → JAL アメーバ移植 — JAL 個別ノードは未作成のため、event のみで記録済み
    # 山西商人と票号 form の包含関係は form_assignment で表現済み (above)

    conn.commit()

    # ============================================================
    # Verification
    # ============================================================
    case_ids = (shanxi, andong_kwon, huong_uoc, sakai, kyocera)
    print("\n=== Task #U: 5 East Asian cases verification ===")
    cur.execute(
        "SELECT COUNT(*) FROM organization WHERE organization_id IN (?,?,?,?,?)", case_ids)
    print(f"organizations created: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM organization_form_assignment WHERE organization_id IN (?,?,?,?,?)",
        case_ids)
    print(f"form assignments: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM activity WHERE organization_id IN (?,?,?,?,?)", case_ids)
    print(f"activities: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM function_record WHERE organization_id IN (?,?,?,?,?)", case_ids)
    print(f"functions: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM impact_record WHERE organization_id IN (?,?,?,?,?)", case_ids)
    print(f"impacts: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM relation WHERE source_organization_id IN (?,?,?,?,?) "
        "OR target_organization_id IN (?,?,?,?,?)",
        case_ids + case_ids)
    print(f"relations involving these orgs: {cur.fetchone()[0]}")
    cur.execute(
        "SELECT COUNT(*) FROM organization_form WHERE taxonomy_name='east_asian'")
    print(f"east_asian forms (total now): {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM organization")
    print(f"organizations (total now): {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claim")
    print(f"claims (total now): {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM source")
    print(f"sources (total now): {cur.fetchone()[0]}")

    print("\n=== Inserted East Asian cases (Task #U) ===")
    for entity_type, eid, name in inserted:
        print(f"  {entity_type:14s}  {eid[:12]}...  {name}")

    print("\n=== New east_asian forms ===")
    for code in ("shang_bang", "huong_uoc", "egoshu", "ameba_keiei"):
        row = cur.execute(
            "SELECT form_id, label FROM organization_form WHERE taxonomy_name='east_asian' AND form_code=?",
            (code,)).fetchone()
        if row:
            print(f"  east_asian/{code}  -> {row[1]}")

    conn.close()


if __name__ == "__main__":
    main()
