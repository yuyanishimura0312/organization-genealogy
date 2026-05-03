#!/usr/bin/env python3
"""Phase 4 並列チーム A: 古代 5 ケースの organization_temporal_facet 投入

目的:
  古代組織の長期的内部変容を facet スライスとして時系列で記録する。
  16_temporal_facets.py の VOC / 三井 / ベネディクト / MakerDAO / Asante と
  同じパターンで、source → claim → facet を chain で生成する。

対象組織 (organization_id 既存 verified 2026-05-03):
  - ウルク Eanna 神殿            8c8b06b7684e40c1b23b7eb499f9db82  (BC3500頃-BC2900頃)
  - エジプト第18王朝の宰相        1f56433ad1364d2ab2a1852839edc9c0  (BC1550頃-BC1077頃)
  - ローマ軍団 (post-Marian)     5abc3447a8704648b866e138f9a954b9  (BC107-AD476)
  - ローマの collegia            1895e59a9e3842d3b671c4fd4955b9ba  (BC500頃-AD476)
  - スパルタ agoge               302b99a2c8304d8fa8286fcc2c7b34f8  (BC700頃-AD200頃)

facet_type 集合 (CHECK 制約と一致):
  membership / governance / resource_base / territory /
  technology / identity / scale / legitimation_basis

設計方針:
  - 古代史は日付精度が低い → valid_from_precision='century' / 'period' 多用
  - BC 日付は ISO 8601 拡張表記 (-NNNN-MM-DD) を採用
  - 不確実な点は confidence を 0.5-0.65 に下げ、note に明記
  - 各 source は実在文献 (Adams 1981, van den Boorn 1988, Goldsworthy/Keppie,
    van Nijf 1997, Kennell 1995 等)。Wikipedia は補助的に reliability 0.5-0.6
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "uruk_eanna":      "8c8b06b7684e40c1b23b7eb499f9db82",
    "egypt_vizier":    "1f56433ad1364d2ab2a1852839edc9c0",
    "roman_legion":    "5abc3447a8704648b866e138f9a954b9",
    "roman_collegia":  "1895e59a9e3842d3b671c4fd4955b9ba",
    "spartan_agoge":   "302b99a2c8304d8fa8286fcc2c7b34f8",
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

    # ---- helpers (16_temporal_facets.py と同シグネチャ) ----
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
                  recorded_by="claude_phase4_ancient_facet"):
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
    # ---------- Uruk Eanna ----------
    src_adams_1981 = add_source(
        "secondary_literature",
        "Adams, R. McC. (1981) Heartland of Cities: Surveys of Ancient "
        "Settlement and Land Use on the Central Floodplain of the Euphrates",
        authors=["Robert McC. Adams"],
        publication_date="1981",
        publisher="University of Chicago Press",
        reliability_score=0.9,
        reliability_basis="メソポタミア都市考古学・神殿経済の標準書。Uruk 期 "
                          "(c.4000-3100 BC) の都市化・神殿中心経済を扱う代表的研究。",
        redistribution="attribution_required",
    )
    src_liverani_2014 = add_source(
        "secondary_literature",
        "Liverani, M. (2014) The Ancient Near East: History, Society and Economy",
        authors=["Mario Liverani"],
        publication_date="2014",
        publisher="Routledge",
        reliability_score=0.9,
        reliability_basis="古代近東史の標準教科書。Uruk Eanna 神殿の経済機能、"
                          "Inanna 崇拝、ED 期の en/ensi 統治への移行を整理。",
                bias_notes="マルクス主義経済史の影響。",
        redistribution="attribution_required",
    )
    src_uruk_wiki = add_source(
        "web",
        "Wikipedia: Eanna - temple complex of Inanna at Uruk",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Eanna"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="Eanna 神殿層位 (Uruk IV-III) と Inanna 崇拝の概略記述。"
                          "原テキスト発見 (proto-cuneiform) 等の事実は確立。",
        redistribution="public_redistributable",
    )

    # ---------- Egyptian vizier ----------
    src_van_den_boorn = add_source(
        "secondary_literature",
        "van den Boorn, G.P.F. (1988) The Duties of the Vizier: Civil "
        "Administration in the Early New Kingdom",
        authors=["G.P.F. van den Boorn"],
        publication_date="1988",
        publisher="Kegan Paul International",
        reliability_score=0.95,
        reliability_basis="新王国宰相職 (djati) 研究の決定版。Rekhmire 墓の "
                          "'Duties of the Vizier' テキスト分析、Thutmose III 期の"
                          "南北二宰相制度確立を詳述。",
        redistribution="attribution_required",
    )
    src_grandet_amarna = add_source(
        "secondary_literature",
        "Grandet, P. (2008) 'Ramesses III' in The Egyptian World, ed. T. Wilkinson",
        authors=["Pierre Grandet"],
        publication_date="2008",
        publisher="Routledge",
        reliability_score=0.85,
        reliability_basis="第19-20王朝期の宰相職。Ramesses III 期の To と Hori、"
                          "末期王朝への政治的弱体化を扱う。",
        redistribution="attribution_required",
    )
    src_vizier_wiki = add_source(
        "web",
        "Wikipedia: Vizier (Ancient Egypt) - djati (tjaty) office",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Vizier_(Ancient_Egypt)"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="宰相職の概要、二宰相制 (Upper/Lower Egypt)、Rekhmire の墓の説明。",
        redistribution="public_redistributable",
    )

    # ---------- Roman legion ----------
    src_keppie_1984 = add_source(
        "secondary_literature",
        "Keppie, L. (1984) The Making of the Roman Army: From Republic to Empire",
        authors=["Lawrence Keppie"],
        publication_date="1984",
        publisher="Batsford / Routledge",
        reliability_score=0.95,
        reliability_basis="ローマ軍団史の標準書。Marian reforms (107 BC) 以降の"
                          "プロフェッショナル化、Augustan 改革による常備 28 (後 25-33) "
                          "軍団体制を詳述。",
        redistribution="attribution_required",
    )
    src_goldsworthy = add_source(
        "secondary_literature",
        "Goldsworthy, A. (2003) The Complete Roman Army",
        authors=["Adrian Goldsworthy"],
        publication_date="2003",
        publisher="Thames & Hudson",
        reliability_score=0.9,
        reliability_basis="ローマ軍団の編成・装備・社会の総合書。3c 危機、Diocletian/"
                          "Constantine 改革 (comitatenses / limitanei) を含む。",
        redistribution="attribution_required",
    )
    src_legion_wiki = add_source(
        "web",
        "Wikipedia: Roman legion - history, structure, post-Marian to late Empire",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Roman_legion"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="軍団数の年代別推移 (Augustus 28、Severan 33 等) の整理。",
        redistribution="public_redistributable",
    )

    # ---------- Roman collegia ----------
    src_van_nijf_1997 = add_source(
        "secondary_literature",
        "van Nijf, O. (1997) The Civic World of Professional Associations in "
        "the Roman East",
        authors=["Onno van Nijf"],
        publication_date="1997",
        publisher="J.C. Gieben",
        reliability_score=0.95,
        reliability_basis="ローマ collegia 研究の標準書。職業組合・葬祭組合の社会的"
                          "機能、ローマ東部の都市生活への統合を分析。",
        redistribution="attribution_required",
    )
    src_perry_2006 = add_source(
        "secondary_literature",
        "Perry, J.S. (2006) The Roman Collegia: The Modern Evolution of an "
        "Ancient Concept",
        authors=["Jonathan Scott Perry"],
        publication_date="2006",
        publisher="Brill",
        reliability_score=0.85,
        reliability_basis="collegia 制度史。Lex Iulia (BC59?) による規制、Trajan・"
                          "Hadrian 期の認可制、3c 以降の corpora 強制化を扱う。",
        redistribution="attribution_required",
    )
    src_collegia_wiki = add_source(
        "web",
        "Wikipedia: Collegium (ancient Rome) - professional and religious associations",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Collegium_(ancient_Rome)"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="collegia 一般紹介。Numa Pompilius 伝承的起源、Lex Iulia、"
                          "後期帝政の corpora 義務化の概要。",
        redistribution="public_redistributable",
    )

    # ---------- Spartan agoge ----------
    src_kennell_1995 = add_source(
        "secondary_literature",
        "Kennell, N.M. (1995) The Gymnasium of Virtue: Education and Culture "
        "in Ancient Sparta",
        authors=["Nigel M. Kennell"],
        publication_date="1995",
        publisher="University of North Carolina Press",
        reliability_score=0.95,
        reliability_basis="agoge 研究の決定版。古典期 agoge の実態と、ヘレニズム期"
                          "Cleomenes III 改革 (227 BC)、ローマ期 'agoge' 復興・"
                          "観光化を区別する重要研究。",
        redistribution="attribution_required",
    )
    src_cartledge_2002 = add_source(
        "secondary_literature",
        "Cartledge, P. (2002) Sparta and Lakonia: A Regional History 1300-362 BC, 2nd ed.",
        authors=["Paul Cartledge"],
        publication_date="2002",
        publisher="Routledge",
        reliability_score=0.9,
        reliability_basis="スパルタ社会史。Lycurgan 制度の古典期確立、agoge の "
                          "Spartiate (homoioi) 育成機能を扱う。",
        redistribution="attribution_required",
    )
    src_agoge_wiki = add_source(
        "web",
        "Wikipedia: Agoge - Spartan education system",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Agoge"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="agoge の段階区分、ローマ期復興の概要記述。",
        redistribution="public_redistributable",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # =========================================================================
    # 1) Uruk Eanna 神殿 (BC3500頃-BC2900頃)
    # =========================================================================
    # governance: 神官統治 (en) → ED 期 ensi 並立
    f = add_facet(
        ORG["uruk_eanna"], "governance",
        {
            "regime": "Late Uruk 期 神殿中心統治 (en/EN priest-ruler)",
            "decision_locus": "Eanna 神殿の en (神官王) を頂点とする神殿経済官僚",
            "key_bodies": ["Eanna 神官団", "書記 (proto-cuneiform 段階)"],
            "notes": "Uruk IV-III 期 (c.3500-3100 BC) の Eanna 神殿は政治・経済・"
                     "宗教の中核。en は世俗的支配者と神官を兼ねる。Adams (1981) の"
                     "都市化モデルと整合。",
        },
        valid_from="-3500-01-01", valid_from_precision="century",
        valid_to="-3100-12-31",   valid_to_precision="century",
        confidence=0.65, source_id=src_adams_1981,
        note="日付境界は考古層位 (Uruk IV-III) ベース、絶対年代は研究者により幅。",
    )
    facets_inserted.append(("uruk_eanna", "governance", "en_priest_ruler", f))

    f = add_facet(
        ORG["uruk_eanna"], "governance",
        {
            "regime": "Early Dynastic (ED) 期 神殿 + 世俗統治者 (lugal/ensi) 並立",
            "decision_locus": "ensi/lugal が世俗権を獲得、Eanna は宗教経済機能に縮小",
            "notes": "ED I-III 期 (c.2900-2350 BC) には世俗的王権 (lugal) が分化、"
                     "Eanna は依然として主要神殿だが政治的中心性は相対化。"
                     "Liverani (2014) 第 4-5 章。",
        },
        valid_from="-2900-01-01", valid_from_precision="century",
        valid_to="-2350-12-31",   valid_to_precision="century",
        confidence=0.6, source_id=src_liverani_2014,
        note="Eanna 神殿『組織』としての終端は曖昧。本 facet は ED 期の機能変化を記録。",
    )
    facets_inserted.append(("uruk_eanna", "governance", "ed_lugal", f))

    # resource_base: 神殿経済 (穀物 / 家畜 / 労働力)
    f = add_facet(
        ORG["uruk_eanna"], "resource_base",
        {
            "primary": "redistributive temple economy (grain, livestock, labour)",
            "secondary": ["長距離交易 (Anatolia/Iran 経由の金属・石材)"],
            "notes": "神殿が穀物備蓄・家畜・労働力動員の中心。proto-cuneiform 文書"
                     "(c.3300 BC) は穀物・家畜・人員の管理記録が大半。",
        },
        valid_from="-3500-01-01", valid_from_precision="century",
        valid_to="-2900-12-31",   valid_to_precision="century",
        confidence=0.7, source_id=src_adams_1981,
    )
    facets_inserted.append(("uruk_eanna", "resource_base", "temple_redistribution", f))

    # technology: proto-cuneiform 書記制
    f = add_facet(
        ORG["uruk_eanna"], "technology",
        {
            "primary": "proto-cuneiform tablets (administrative)",
            "notes": "Uruk IV 期 (c.3300 BC) に proto-cuneiform が出現。Eanna 神殿"
                     "経済管理が文字発生の主要動因とされる (Schmandt-Besserat / Nissen)。",
        },
        valid_from="-3300-01-01", valid_from_precision="century",
        valid_to="-2900-12-31",   valid_to_precision="century",
        confidence=0.75, source_id=src_liverani_2014,
    )
    facets_inserted.append(("uruk_eanna", "technology", "proto_cuneiform", f))

    # legitimation_basis: Inanna 崇拝
    f = add_facet(
        ORG["uruk_eanna"], "legitimation_basis",
        {
            "basis": "Inanna (Ishtar) cult - 都市神信仰による神聖王権",
            "notes": "Eanna は Inanna の主神殿。en の権威は Inanna の地上代理という"
                     "宗教的正当性に基づく。後の Sumerian King List も Uruk 王権を"
                     "Inanna と結びつける。",
        },
        valid_from="-3500-01-01", valid_from_precision="century",
        valid_to="-2350-12-31",   valid_to_precision="century",
        confidence=0.7, source_id=src_uruk_wiki,
    )
    facets_inserted.append(("uruk_eanna", "legitimation_basis", "inanna_cult", f))

    # =========================================================================
    # 2) エジプト第18王朝の宰相 djati (BC1550-BC1077, 第18-20王朝)
    # =========================================================================
    # governance: 王朝初期単一宰相 → Thutmose III 期に南北二宰相制
    f = add_facet(
        ORG["egypt_vizier"], "governance",
        {
            "regime": "第18王朝初期: 単一宰相 (djati) - 王に直属する最高行政官",
            "decision_locus": "djati 一人がエジプト全土の行政・司法・財務を統括、"
                              "ファラオに直接報告",
            "notes": "Ahmose I-Hatshepsut 期 (c.1550-1458 BC) は単一宰相制。"
                     "Hatshepsut 治世末期に Useramen など著名な djati。",
        },
        valid_from="-1550-01-01", valid_from_precision="decade",
        valid_to="-1458-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_van_den_boorn,
    )
    facets_inserted.append(("egypt_vizier", "governance", "single_vizier", f))

    f = add_facet(
        ORG["egypt_vizier"], "governance",
        {
            "regime": "Thutmose III 期以降: 南北二宰相制 (Upper / Lower Egypt)",
            "decision_locus": "上エジプト宰相 (Thebes 拠点) と下エジプト宰相 "
                              "(Memphis/Heliopolis 拠点) の二分。Rekhmire は上宰相。",
            "key_bodies": ["上エジプト宰相府", "下エジプト宰相府", "ファラオ宮廷"],
            "notes": "Thutmose III (c.1458 BC 単独統治開始) 期に二宰相制が確立。"
                     "Rekhmire 墓 (TT100) の 'Duties of the Vizier' テキストが"
                     "職務範囲を詳述。van den Boorn (1988) の中心テーマ。",
        },
        valid_from="-1458-01-01", valid_from_precision="decade",
        valid_to="-1295-12-31",   valid_to_precision="decade",
        confidence=0.8, source_id=src_van_den_boorn,
    )
    facets_inserted.append(("egypt_vizier", "governance", "dual_vizier", f))

    f = add_facet(
        ORG["egypt_vizier"], "governance",
        {
            "regime": "第19-20王朝: 二宰相制継続 + 軍人系宰相の台頭",
            "decision_locus": "二宰相制を踏襲しつつ、Ramesside 期は軍人/王族出身の"
                              "宰相が増加。Khaemwaset (王子) 等の例。",
            "notes": "Ramesses II-III 期は宰相職が王族・軍人エリートに開かれる。"
                     "末期は神官 (Amun 大司祭) との権力競合が始まる。",
        },
        valid_from="-1295-01-01", valid_from_precision="decade",
        valid_to="-1077-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_grandet_amarna,
    )
    facets_inserted.append(("egypt_vizier", "governance", "ramesside", f))

    # membership: 宰相の選抜基盤
    f = add_facet(
        ORG["egypt_vizier"], "membership",
        {
            "basis": "選抜任用 (王による任命)",
            "eligibility": "高位行政官・神官の出身、稀に王族。世襲ではないが"
                           "事実上の名門出身が多い。",
            "notes": "Useramen-Rekhmire は叔甥継承の例で、宰相職が一族で循環する"
                     "ケースも存在。van den Boorn (1988) は理念上の能力主義と"
                     "実際の門閥傾向の両方を指摘。",
        },
        valid_from="-1550-01-01", valid_from_precision="decade",
        valid_to="-1077-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_vizier_wiki,
    )
    facets_inserted.append(("egypt_vizier", "membership", "appointed_elite", f))

    # legitimation_basis: ファラオの代理人・Maat の守護者
    f = add_facet(
        ORG["egypt_vizier"], "legitimation_basis",
        {
            "basis": "ファラオの個人的代理 (王権の延長) + Maat (秩序・正義) の守護",
            "notes": "'Duties of the Vizier' は Maat に従う公正な裁定を djati の"
                     "中核機能として強調。宰相の権威はファラオ個人への忠誠と"
                     "宇宙的秩序維持の両面に依拠。",
        },
        valid_from="-1550-01-01", valid_from_precision="decade",
        valid_to="-1077-12-31",   valid_to_precision="decade",
        confidence=0.75, source_id=src_van_den_boorn,
    )
    facets_inserted.append(("egypt_vizier", "legitimation_basis", "pharaoh_maat", f))

    # =========================================================================
    # 3) ローマ軍団 (post-Marian) BC107 - AD476
    # =========================================================================
    # membership: Marian reforms 後の志願兵制
    f = add_facet(
        ORG["roman_legion"], "membership",
        {
            "basis": "志願制プロフェッショナル軍 (post-Marian)",
            "eligibility": "ローマ市民 (capite censi 含む)、土地所有要件撤廃。"
                           "16-25 年の長期服務、退役後 land grant",
            "notes": "BC107 Marius の改革で財産資格を撤廃、無産市民の入隊を可能に。"
                     "兵士は将軍個人に忠誠、内戦の構造的要因に。Keppie (1984) 第 3-4 章。",
        },
        valid_from="-0107-01-01", valid_from_precision="year",
        valid_to="-0030-12-31",   valid_to_precision="decade",
        confidence=0.85, source_id=src_keppie_1984,
    )
    facets_inserted.append(("roman_legion", "membership", "marian_volunteer", f))

    f = add_facet(
        ORG["roman_legion"], "membership",
        {
            "basis": "Augustan 常備軍 - 国家給与制 + 退役後 praemia",
            "eligibility": "ローマ市民 (auxilia は非市民)、20 年現役 + 5 年予備、"
                           "Aerarium Militare (AD6 設立) からの退役金",
            "notes": "Augustus が 28 個常備軍団を確立、給与・退役金を国家財政化。"
                     "兵士の将軍個人への忠誠依存を制度的に弱める。Keppie 第 5 章。",
        },
        valid_from="-0030-01-01", valid_from_precision="decade",
        valid_to="0235-12-31",    valid_to_precision="year",
        confidence=0.85, source_id=src_keppie_1984,
    )
    facets_inserted.append(("roman_legion", "membership", "augustan_standing", f))

    f = add_facet(
        ORG["roman_legion"], "membership",
        {
            "basis": "後期帝政: comitatenses (機動軍) と limitanei (国境守備) の分化、"
                     "barbarian foederati 大量編入",
            "eligibility": "市民権が AD212 に拡大 (Constitutio Antoniniana) し、"
                           "民族・出自要件は希薄化。3c 以降ゲルマン系兵士が主力に。",
            "notes": "Diocletian/Constantine の改革で軍団は小型化 (1000 人級) し、"
                     "comitatenses と limitanei に二分。5c には正規軍と foederati の"
                     "境界が曖昧化。Goldsworthy (2003) 第 8-9 章。",
        },
        valid_from="0284-01-01", valid_from_precision="year",
        valid_to="0476-09-04",   valid_to_precision="exact",
        confidence=0.8, source_id=src_goldsworthy,
    )
    facets_inserted.append(("roman_legion", "membership", "late_empire", f))

    # scale: 軍団数の推移
    f = add_facet(
        ORG["roman_legion"], "scale",
        {
            "metric": "active_legions",
            "value": 28,
            "manpower_per_legion": "approx. 5000-5500 (legionaries) + auxilia",
            "notes": "Augustus 治世 (AD14) 時点で 28 個軍団。Varus 災害 (AD9) 後の"
                     "再編成を経た数値。Keppie (1984) Appendix。",
        },
        valid_from="-0030-01-01", valid_from_precision="decade",
        valid_to="0192-12-31",    valid_to_precision="year",
        confidence=0.85, source_id=src_keppie_1984,
    )
    facets_inserted.append(("roman_legion", "scale", "early_empire_28", f))

    f = add_facet(
        ORG["roman_legion"], "scale",
        {
            "metric": "active_legions",
            "value": 33,
            "notes": "Septimius Severus (在位 193-211) が新軍団を編成し計 33 個に。"
                     "後 Severan 期は 33-35 個で推移。Goldsworthy (2003)。",
        },
        valid_from="0193-01-01", valid_from_precision="year",
        valid_to="0284-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_goldsworthy,
    )
    facets_inserted.append(("roman_legion", "scale", "severan_33", f))

    f = add_facet(
        ORG["roman_legion"], "scale",
        {
            "metric": "active_legions",
            "value_range": "approx. 60-70 (smaller, ~1000 men each)",
            "notes": "Diocletian/Constantine 改革で軍団数は 60-70 に増加するが、"
                     "1 軍団あたりの人員は約 1000 人へ縮小。総兵力は概ね同程度。"
                     "Notitia Dignitatum (c.AD400) の記録に基づく推定。",
        },
        valid_from="0284-01-01", valid_from_precision="year",
        valid_to="0476-09-04",   valid_to_precision="exact",
        confidence=0.7, source_id=src_legion_wiki,
        note="後期帝政の正確な軍団数は Notitia Dignitatum の解釈に依存し、"
             "研究者により幅。",
    )
    facets_inserted.append(("roman_legion", "scale", "late_60_smaller", f))

    # =========================================================================
    # 4) ローマの collegia (BC500頃-AD476)
    # =========================================================================
    # legitimation_basis: 王政期伝承的起源 → 共和政期慣行
    f = add_facet(
        ORG["roman_collegia"], "legitimation_basis",
        {
            "basis": "Numa Pompilius 伝承的起源、宗教 cultus 中心の自由結社",
            "notes": "古典伝承 (Plutarch Numa 17) は Numa が職人 collegia を"
                     "創設したと伝える。実際の起源は王政末期-共和政初期と推定。"
                     "宗教祭祀を口実とする結社が法的庇護を得る慣行。",
        },
        valid_from="-0500-01-01", valid_from_precision="century",
        valid_to="-0064-12-31",   valid_to_precision="year",
        confidence=0.55, source_id=src_collegia_wiki,
        note="伝承的起源、考古学的に確認困難。précise BC500 は概念的。",
    )
    facets_inserted.append(("roman_collegia", "legitimation_basis", "numan_origin", f))

    # governance: 共和政末期の政治化と弾圧 → 帝政期認可制
    f = add_facet(
        ORG["roman_collegia"], "governance",
        {
            "regime": "共和政末期: 政治化、Lex Iulia (BC59 or BC56) による禁止/規制",
            "decision_locus": "各 collegium は magistri / quaestores による自治、"
                              "ただし国家による解散命令対象に",
            "notes": "Clodius の collegia 動員 (BC58) を契機に、Caesar/Augustus が"
                     "collegia を強く規制。Lex Iulia de collegiis で"
                     "未認可結社を禁止 (年代は BC64・BC59・BC56 諸説)。",
        },
        valid_from="-0064-01-01", valid_from_precision="decade",
        valid_to="0014-12-31",    valid_to_precision="year",
        confidence=0.65, source_id=src_perry_2006,
    )
    facets_inserted.append(("roman_collegia", "governance", "republican_crisis", f))

    f = add_facet(
        ORG["roman_collegia"], "governance",
        {
            "regime": "帝政前期: 元老院認可制 (collegia licita) - 葬祭・職業組合中心",
            "decision_locus": "各 collegium 内部は magistri 合議、外部では元老院/"
                              "皇帝の認可を要件とする",
            "key_bodies": ["magistri", "quaestores", "patroni (有力者の庇護)"],
            "notes": "Augustus 以降、認可された collegia (主に collegia tenuiorum 葬祭組合・"
                     "職業組合) のみ合法。Trajan-Pliny 書簡 (10.33-34) は Bithynia の"
                     "消防 collegium 認可拒否で有名。van Nijf (1997) は東方都市での"
                     "市民生活統合機能を重視。",
        },
        valid_from="0015-01-01", valid_from_precision="year",
        valid_to="0249-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_van_nijf_1997,
    )
    facets_inserted.append(("roman_collegia", "governance", "imperial_licensed", f))

    f = add_facet(
        ORG["roman_collegia"], "governance",
        {
            "regime": "後期帝政: corpora 強制化 - 世襲的国家義務集団へ",
            "decision_locus": "国家が職業 corpora への加入と世襲を強制。"
                              "自治結社性を喪失し国家行政の延長に",
            "notes": "3c 危機以降、Diocletian/Constantine が pistores (パン職人)・"
                     "navicularii (海運業者) など重要職業 corpora の加入・世襲を"
                     "義務化。collegia は事実上 ギルド的国家機構へ転換。"
                     "Perry (2006) 第 4 章。",
        },
        valid_from="0250-01-01", valid_from_precision="decade",
        valid_to="0476-09-04",   valid_to_precision="exact",
        confidence=0.8, source_id=src_perry_2006,
    )
    facets_inserted.append(("roman_collegia", "governance", "late_compulsory", f))

    # membership: 自由参加 → 世襲強制
    f = add_facet(
        ORG["roman_collegia"], "membership",
        {
            "basis": "自発的加入 (職業・宗教・葬祭の共同体)",
            "eligibility": "解放奴隷・自由人混在、女性会員も存在。低身分者中心の "
                           "collegia tenuiorum が多数",
            "notes": "帝政前期の碑文証拠は解放奴隷比率の高さを示す。van Nijf (1997) "
                     "は collegia が低身分者の社会的可視性獲得装置だったと論じる。",
        },
        valid_from="-0064-01-01", valid_from_precision="decade",
        valid_to="0249-12-31",    valid_to_precision="year",
        confidence=0.8, source_id=src_van_nijf_1997,
    )
    facets_inserted.append(("roman_collegia", "membership", "voluntary_freedmen", f))

    f = add_facet(
        ORG["roman_collegia"], "membership",
        {
            "basis": "強制的・世襲的 (国家割当)",
            "eligibility": "対象職業者は離脱不可、子も継承義務。逃亡は刑罰対象",
            "notes": "Codex Theodosianus (5c) には pistores・navicularii・collegiati の"
                     "世襲強制規定が頻出。自由結社から国家統制機構への転換を示す。",
        },
        valid_from="0250-01-01", valid_from_precision="decade",
        valid_to="0476-09-04",   valid_to_precision="exact",
        confidence=0.8, source_id=src_perry_2006,
    )
    facets_inserted.append(("roman_collegia", "membership", "compulsory_hereditary", f))

    # =========================================================================
    # 5) スパルタ agoge (BC700頃-AD200頃)
    # =========================================================================
    # membership: 古典期 Spartiate 限定
    f = add_facet(
        ORG["spartan_agoge"], "membership",
        {
            "basis": "Spartiate (homoioi) 男子のみ - 7 歳から 30 歳まで強制",
            "eligibility": "Spartan 市民 (Spartiate) の嫡男のみ、希に mothakes "
                           "(劣格者) が許可。perioikoi/helot は除外",
            "notes": "古典期 (c.700-371 BC) の agoge は Spartiate 男子の市民教育。"
                     "Lycurgus 伝承的立法に帰属。Cartledge (2002) 第 7 章。",
        },
        valid_from="-0700-01-01", valid_from_precision="century",
        valid_to="-0371-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_cartledge_2002,
        note="agoge の起源年代は不明、BC7c 頃の Lycurgan 制度確立に置く慣例的見方。",
    )
    facets_inserted.append(("spartan_agoge", "membership", "classical_spartiate", f))

    f = add_facet(
        ORG["spartan_agoge"], "membership",
        {
            "basis": "縮減期: Spartiate 数の急減により事実上機能停止",
            "eligibility": "Leuctra (BC371) 後の oliganthropia (人口減) で参加者激減",
            "notes": "BC371 Leuctra 敗戦後、Spartiate 数が急減 (5c 8000 → 4c 1000 程度)、"
                     "agoge は事実上崩壊。Cartledge (2002) 第 12 章。",
        },
        valid_from="-0371-01-01", valid_from_precision="decade",
        valid_to="-0227-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_cartledge_2002,
    )
    facets_inserted.append(("spartan_agoge", "membership", "post_leuctra_decline", f))

    f = add_facet(
        ORG["spartan_agoge"], "membership",
        {
            "basis": "Cleomenes III 改革による再建 (BC227)",
            "eligibility": "市民資格を拡大 (perioikoi/外国人 4000 人を Spartiate 化)、"
                           "agoge 再開",
            "notes": "Cleomenes III (在位 235-222 BC) が BC227 に Lycurgan 制度の"
                     "再興を宣言、agoge を再建。Sellasia 敗戦 (BC222) で短命に終わる。"
                     "Kennell (1995) 第 2 章。",
        },
        valid_from="-0227-01-01", valid_from_precision="year",
        valid_to="-0146-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_kennell_1995,
    )
    facets_inserted.append(("spartan_agoge", "membership", "cleomenean_revival", f))

    f = add_facet(
        ORG["spartan_agoge"], "membership",
        {
            "basis": "ローマ期 'agoge' - 観光化された儀礼的再演",
            "eligibility": "スパルタ少年 (citizenship 規模はローマ統治下で再定義)、"
                           "ローマ人観光客向けの公開儀式 (diamastigosis 鞭打ち祭) を含む",
            "notes": "Kennell (1995) の中心主張: ローマ期の 'agoge' は古典期の直接連続"
                     "ではなく、ヘレニズム末-ローマ期に再構築された ritualized 制度。"
                     "diamastigosis (Artemis Orthia 祭の鞭打ち) はローマ期に観光名物化。",
        },
        valid_from="-0146-01-01", valid_from_precision="year",
        valid_to="0200-12-31",    valid_to_precision="century",
        confidence=0.75, source_id=src_kennell_1995,
        note="Kennell の主張は agoge 連続性論への決定的修正。終端 AD200 頃は"
             "Pausanias 記述・3c 衰退の目安。",
    )
    facets_inserted.append(("spartan_agoge", "membership", "roman_revival_ritualized", f))

    # identity: 軍事訓練 → 観光・儀礼
    f = add_facet(
        ORG["spartan_agoge"], "identity",
        {
            "dominant_identity": "軍事教育・市民育成 (Spartiate hoplite 養成)",
            "notes": "古典期 agoge は重装歩兵 (hoplite phalanx) と Spartan 市民"
                     "アイデンティティ (homoioi) の同時生産装置。",
        },
        valid_from="-0700-01-01", valid_from_precision="century",
        valid_to="-0371-12-31",   valid_to_precision="decade",
        confidence=0.75, source_id=src_cartledge_2002,
    )
    facets_inserted.append(("spartan_agoge", "identity", "classical_military", f))

    f = add_facet(
        ORG["spartan_agoge"], "identity",
        {
            "dominant_identity": "古代スパルタ伝統の儀礼的再演 (heritage performance)",
            "brand_or_name": "agoge (ローマ期復興版)",
            "notes": "ローマ期はスパルタの古典的栄光を再演する文化観光・儀礼装置。"
                     "diamastigosis や ephebic contests が中心。Kennell (1995) は"
                     "これを 'invention of tradition' に近い現象と位置づける。",
        },
        valid_from="-0146-01-01", valid_from_precision="year",
        valid_to="0200-12-31",    valid_to_precision="century",
        confidence=0.7, source_id=src_agoge_wiki,
    )
    facets_inserted.append(("spartan_agoge", "identity", "roman_heritage", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ
    # =========================================================================
    print("=" * 70)
    print("--- 投入結果 ---")
    print(f"投入 facet レコード総数: {len(facets_inserted)}")
    print("=" * 70)
    print()

    print("組織別 facet 件数")
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
        print(f"  {name}: {n}")
    print()

    print("facet_type 別件数 (本投入分)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT f.facet_type, COUNT(*) AS n
        FROM organization_temporal_facet f
        WHERE f.organization_id IN (?,?,?,?,?)
        GROUP BY f.facet_type
        ORDER BY n DESC
        """,
        tuple(ORG.values()),
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")
    print()

    print("ローマ軍団: scale (軍団数) 推移")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value, confidence
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'scale'
        ORDER BY valid_from
        """,
        (ORG["roman_legion"],),
    ).fetchall()
    for vf, vt, fv, conf in rows:
        v = json.loads(fv)
        val = v.get("value") or v.get("value_range") or "—"
        print(f"  {vf} → {vt or 'open'} | conf={conf} | legions={val}")
    print()

    print("agoge: membership 4 段階")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'membership'
        ORDER BY valid_from
        """,
        (ORG["spartan_agoge"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('basis')}")
    print()

    conn.close()


if __name__ == "__main__":
    main()
