#!/usr/bin/env python3
"""Phase 4 並列チーム B: 中世宗教・教育系 8 ケースの organization_temporal_facet 投入

担当 (organization_id 既存 verified 2026-05-03):
  - バイト・アル=ヒクマ (House of Wisdom)   f0a66f1db27646bf8fc3f26ddbba123c (786-1258)
  - 比叡山延暦寺 (Tendai School)              9d844aafb5a0473a9673a26c04c69552 (788-active)
  - Cluny 修道会                               dfb63f4c58a146ba99c30686d317401a (910-1790)
  - 安東権氏門中 (Andong Kwon Munjung)        bbfeb4dcfd044936bd322660e3c0e154 (930-active)
  - アル・アズハル (Al-Azhar)                  c52e89e33eff49bfa067ff8e6f3921f7 (972-active)
  - ボローニャ大学                            8784a09b16554b9bac6572b47fe33aa2 (1088-active)
  - シトー会 (Cistercians)                     d9c2571497d84171ad42eb73e6c6799c (1098-active)
  - ナクシュバンディー教団                    2121dceb79754ea382104354c0e9439e (1380-active)

facet_type 集合 (schema CHECK):
  membership / governance / resource_base / territory /
  technology / identity / scale / legitimation_basis

設計方針:
  - 各ケースで 4-6 facet を投入し、重要な変容ポイントを記録
  - claim 経由で出典付き、捏造禁止
  - 不確実な日付・粒度は precision で表現、低 confidence は note で明記
  - 中世の正確な日付は不明なものが多いため、precision=year/decade/century を多用
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "bayt_al_hikma": "f0a66f1db27646bf8fc3f26ddbba123c",
    "hieizan":       "9d844aafb5a0473a9673a26c04c69552",
    "cluny":         "dfb63f4c58a146ba99c30686d317401a",
    "kwon_munjung":  "bbfeb4dcfd044936bd322660e3c0e154",
    "al_azhar":      "c52e89e33eff49bfa067ff8e6f3921f7",
    "bologna":       "8784a09b16554b9bac6572b47fe33aa2",
    "cistercians":   "d9c2571497d84171ad42eb73e6c6799c",
    "naqshbandi":    "2121dceb79754ea382104354c0e9439e",
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
                  recorded_by="claude_phase4_medieval_religious"):
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
    # SOURCES (実在文献優先)
    # =========================================================================
    src_gutas = add_source(
        "secondary_literature",
        "Gutas, D. (1998) Greek Thought, Arabic Culture: The Graeco-Arabic "
        "Translation Movement in Baghdad and Early ʿAbbāsid Society",
        authors=["Dimitri Gutas"],
        publication_date="1998",
        publisher="Routledge",
        reliability_score=0.95,
        reliability_basis="バイト・アル=ヒクマとアッバース朝翻訳運動の標準的批判研究。"
                          "宮廷図書館・翻訳所としての性格と神話化された'House of Wisdom'像との"
                          "区別を厳密に提示。",
        bias_notes="従来の神話的記述を批判的に修正する立場、'機関'としての制度性を控えめに評価。",
        redistribution="attribution_required",
    )
    src_hikma_wiki = add_source(
        "web",
        "Wikipedia: House of Wisdom (Bayt al-Ḥikma) - Abbasid era to Mongol "
        "destruction (1258)",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/House_of_Wisdom"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="百科事典の概観。Hārūn al-Rashīd 期の図書館設立、"
                          "al-Maʾmūn (813-833) 期の最盛、1258 モンゴル軍 (Hulagu) による"
                          "バグダード破壊までの整理。",
        bias_notes="神話化された記述と Gutas の批判的見解が混在。",
        redistribution="public_redistributable",
    )

    src_groner = add_source(
        "secondary_literature",
        "Groner, P. (1984) Saichō: The Establishment of the Japanese Tendai School",
        authors=["Paul Groner"],
        publication_date="1984",
        publisher="University of Hawaii Press",
        reliability_score=0.95,
        reliability_basis="最澄 (Saichō) と日本天台宗成立の標準研究書。"
                          "788 比叡山創建、806 天台宗公認、大乗戒壇設立 (822) を扱う。",
        redistribution="attribution_required",
    )
    src_stone = add_source(
        "secondary_literature",
        "Stone, J.I. (1999) Original Enlightenment and the Transformation of "
        "Medieval Japanese Buddhism",
        authors=["Jacqueline I. Stone"],
        publication_date="1999",
        publisher="University of Hawaii Press",
        reliability_score=0.9,
        reliability_basis="中世天台本覚思想の研究。鎌倉新仏教 (法然・親鸞・道元・日蓮) が"
                          "比叡山で学んだ系譜を歴史的に位置づける。",
        redistribution="attribution_required",
    )
    src_hieizan_wiki = add_source(
        "web",
        "Wikipedia: Enryaku-ji / Mount Hiei - founding, Nobunaga's burning "
        "(1571), Edo restoration, modern era",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Enryaku-ji"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="比叡山延暦寺の歴史概要。1571 信長焼討、徳川期復興、"
                          "明治神仏分離、現代の整理。",
        redistribution="public_redistributable",
    )

    src_iognaprat = add_source(
        "secondary_literature",
        "Iogna-Prat, D. (2002) Order and Exclusion: Cluny and Christendom Face "
        "Heresy, Judaism, and Islam (1000-1150)",
        authors=["Dominique Iogna-Prat"],
        publication_date="2002",
        publisher="Cornell University Press",
        reliability_score=0.95,
        reliability_basis="クリュニー修道会の社会史的標準研究。910 創建以降、"
                          "11-12c の Cluniac Reform、約 1000 院に及ぶネットワーク、"
                          "12c 以降の凋落を扱う。",
        bias_notes="クリュニーの宗教社会学的影響を強調する立場。",
        redistribution="attribution_required",
    )
    src_cluny_wiki = add_source(
        "web",
        "Wikipedia: Cluny Abbey / Order of Cluny - foundation 910, Cluniac "
        "Reforms, dissolution by French Revolution 1790",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Cluny_Abbey"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="クリュニー会の創建 (910) ・ 11c ピーク・1790 仏革命解体の"
                          "概観。Abbot Hugh of Semur (1049-1109) 期の最盛を記述。",
        redistribution="public_redistributable",
    )

    src_kwon_jokbo = add_source(
        "primary_text",
        "安東權氏成化譜 (1476) - 韓国最古現存の族譜 (Andong Kwon clan genealogy)",
        publication_date="1476",
        reliability_score=0.85,
        reliability_basis="1476 年刊行、韓国最古現存の族譜として知られる安東權氏成化譜。"
                          "高麗末期から朝鮮初期にかけての門中組織化を示す一次史料。",
        bias_notes="父系血縁集団の正統化を目的とする家門記録、女性・庶子の系譜は"
                   "後の時代に整備された規範に従って簡略化される傾向。",
        redistribution="public_redistributable",
    )
    src_deuchler = add_source(
        "secondary_literature",
        "Deuchler, M. (1992) The Confucian Transformation of Korea: A Study of "
        "Society and Ideology",
        authors=["Martina Deuchler"],
        publication_date="1992",
        publisher="Harvard University Asia Center",
        reliability_score=0.95,
        reliability_basis="朝鮮王朝期の門中・宗族制度の形成を扱う標準研究。"
                          "高麗から朝鮮への父系化・儒教化と門中の制度的確立を詳述。",
        redistribution="attribution_required",
    )

    src_dodge = add_source(
        "secondary_literature",
        "Dodge, B. (1961) Al-Azhar: A Millennium of Muslim Learning",
        authors=["Bayard Dodge"],
        publication_date="1961",
        publisher="Middle East Institute",
        reliability_score=0.85,
        reliability_basis="アル・アズハルの千年史を扱う英文標準書。"
                          "972 ファーティマ朝シーア派モスク創建、1171 アイユーブ朝による"
                          "スンニ転換、近代までの整理。",
        bias_notes="1961 出版、近年の研究で更新された部分あり。",
        redistribution="attribution_required",
    )
    src_azhar_wiki = add_source(
        "web",
        "Wikipedia: Al-Azhar University - Fatimid foundation, Sunni transition, "
        "Ottoman era, 1961 Nasser reforms",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Al-Azhar_University"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="アズハルの 972 創建から 1961 ナーセルによる近代国営大学化までの整理。",
        redistribution="public_redistributable",
    )

    src_verger = add_source(
        "secondary_literature",
        "Verger, J. (1999) Les universités au Moyen Age",
        authors=["Jacques Verger"],
        publication_date="1999",
        publisher="Presses Universitaires de France",
        reliability_score=0.95,
        reliability_basis="中世大学史のフランス語標準書。ボローニャの universitas "
                          "(学生組合) 形成、法学中心、12-13c の制度確立を詳述。",
        redistribution="attribution_required",
    )
    src_brizzi = add_source(
        "secondary_literature",
        "Brizzi, G.P. (ed.) Storia dell'Università di Bologna",
        authors=["Gian Paolo Brizzi"],
        publisher="CLUEB / Bononia University Press",
        reliability_score=0.9,
        reliability_basis="ボローニャ大学公式編纂史シリーズ。"
                          "1088 創立 (慣例的年次)、universitas scholarium、"
                          "近代化と現代 EU 大学への変容。",
        redistribution="attribution_required",
    )
    src_bologna_wiki = add_source(
        "web",
        "Wikipedia: University of Bologna - foundation 1088, universitas, "
        "modern reforms",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/University_of_Bologna"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="1088 創立年次は慣例的 (1888 Carducci の四旬節祭にて確定)、"
                          "近代国家による国営化、現代の Bologna Process 主導の整理。",
        redistribution="public_redistributable",
    )

    src_berman = add_source(
        "secondary_literature",
        "Berman, C.H. (2000) The Cistercian Evolution: The Invention of a "
        "Religious Order in Twelfth-Century Europe",
        authors=["Constance Hoffman Berman"],
        publication_date="2000",
        publisher="University of Pennsylvania Press",
        reliability_score=0.9,
        reliability_basis="シトー会研究の修正主義的標準書。1098 創立は伝統的だが、"
                          "12c 中葉以降の急拡大と組織化が実態的な 'Order' 形成と論じる。"
                          "12c 末に約 700 院に達する。",
        bias_notes="従来の Bernard of Clairvaux 中心史観を相対化する立場。",
        redistribution="attribution_required",
    )
    src_cistercian_wiki = add_source(
        "web",
        "Wikipedia: Cistercians - foundation 1098, expansion, Reformation, "
        "modern OCSO/OCist split",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Cistercians"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="1098 Cîteaux 創立、Charter of Charity (1119)、"
                          "1664 Trappist 改革、1892 OCSO 独立、現代 OCist/OCSO 分岐の整理。",
        redistribution="public_redistributable",
    )

    src_algar = add_source(
        "secondary_literature",
        "Algar, H. (2007) Naqshbandiyya in: Encyclopaedia of Islam, Second Edition",
        authors=["Hamid Algar"],
        publication_date="2007",
        publisher="Brill",
        reliability_score=0.95,
        reliability_basis="ナクシュバンディー教団の標準的事典項目。"
                          "Bahā' al-Dīn Naqshband (1318-1389) 創始 (中央アジア・ブハラ)、"
                          "Mujaddidi 分派 (Sirhindī, d.1624)、Khālidī 分派、現代展開を扱う。",
        redistribution="attribution_required",
    )
    src_naqshbandi_wiki = add_source(
        "web",
        "Wikipedia: Naqshbandi - founding 1380s, Ottoman expansion, "
        "Mujaddidi/Khalidi sub-orders, modern global diffusion",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Naqshbandi"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="ナクシュバンディー教団のスーフィー道団としての歴史概観。"
                          "中央アジア起源、オスマン期拡大、インド進出 (Mujaddidi 16-17c)、"
                          "現代世界拡散の整理。",
        redistribution="public_redistributable",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # ---------- バイト・アル=ヒクマ -----------------------------------------
    f = add_facet(
        ORG["bayt_al_hikma"], "identity",
        {
            "dominant_identity": "アッバース朝宮廷図書館 (Khizānat al-Ḥikma)",
            "brand_or_name": "Khizānat al-Ḥikma / Bayt al-Ḥikma",
            "notes": "Hārūn al-Rashīd (r.786-809) 期にバグダードに設立された宮廷図書館。"
                     "Gutas (1998) は神話化された'研究機関'像を批判し、本来は"
                     "ササン朝写本伝統を引き継ぐ宮廷蔵書として位置づける。",
        },
        valid_from="0786-01-01", valid_from_precision="decade",
        valid_to="0813-12-31",   valid_to_precision="year",
        confidence=0.65, source_id=src_gutas,
        note="設立年次は確定的でない。786 (al-Rashīd 即位) を採用。",
    )
    facets_inserted.append(("bayt_al_hikma", "identity", "court_library", f))

    f = add_facet(
        ORG["bayt_al_hikma"], "identity",
        {
            "dominant_identity": "翻訳運動の中核機関 (al-Maʾmūn 期)",
            "brand_or_name": "Bayt al-Ḥikma (House of Wisdom)",
            "notes": "al-Maʾmūn (r.813-833) 期に Greek-Arabic 翻訳運動が最盛、"
                     "Ḥunayn ibn Isḥāq らの翻訳学者が活動。ただし制度的'機関'としての"
                     "明示的境界は史料上不明瞭 (Gutas)。",
        },
        valid_from="0813-01-01", valid_from_precision="year",
        valid_to="0861-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_gutas,
        note="al-Mutawakkil (r.847-861) 期以降、宮廷の知的活動の中心が移行。",
    )
    facets_inserted.append(("bayt_al_hikma", "identity", "translation_peak", f))

    f = add_facet(
        ORG["bayt_al_hikma"], "scale",
        {
            "phase": "peak (al-Maʾmūn era)",
            "metric": "translation_output",
            "value_range": "数百冊規模の Greek/Syriac/Pahlavi → Arabic 翻訳",
            "notes": "Gutas (1998) はアッバース朝翻訳運動の規模を、ギリシア科学・哲学・"
                     "医学のほぼ全領域に及ぶと整理。Bayt al-Ḥikma 単独の'蔵書数'は"
                     "史料に明示なし。",
        },
        valid_from="0813-01-01", valid_from_precision="year",
        valid_to="0861-12-31",   valid_to_precision="year",
        confidence=0.6, source_id=src_gutas,
        note="蔵書数の数値は伝説的記述と区別が困難。翻訳事業の規模で代用。",
    )
    facets_inserted.append(("bayt_al_hikma", "scale", "translation_volume", f))

    f = add_facet(
        ORG["bayt_al_hikma"], "governance",
        {
            "regime": "アッバース朝宮廷直属、カリフ庇護下",
            "decision_locus": "カリフおよび宮廷官僚 (vizier、Banū Mūsā 等の学者一族)",
            "notes": "独立法人格はなく、カリフ宮廷の一部局として運営。"
                     "翻訳学者は宮廷の俸給または個人パトロンによる委託で活動。",
        },
        valid_from="0786-01-01", valid_from_precision="decade",
        valid_to="1258-02-13",   valid_to_precision="exact",
        confidence=0.65, source_id=src_gutas,
    )
    facets_inserted.append(("bayt_al_hikma", "governance", "caliphal", f))

    f = add_facet(
        ORG["bayt_al_hikma"], "identity",
        {
            "dominant_identity": "縮小・残存期 (post-translation movement)",
            "brand_or_name": "Bayt al-Ḥikma (機能的縮小)",
            "notes": "9c 末以降、翻訳運動の最盛は過ぎ、宮廷図書館としての"
                     "象徴的機能に縮小。1055 セルジューク朝のバグダード入城以降、"
                     "アッバース朝政治力の衰退と並行。",
        },
        valid_from="0861-01-01", valid_from_precision="year",
        valid_to="1258-02-13",   valid_to_precision="exact",
        confidence=0.55, source_id=src_hikma_wiki,
        note="9c-13c の継続性については史料的根拠が薄い。'残存していた'説は通俗的。",
    )
    facets_inserted.append(("bayt_al_hikma", "identity", "decline", f))

    f = add_facet(
        ORG["bayt_al_hikma"], "scale",
        {
            "phase": "destruction by Mongols (1258)",
            "metric": "extinction_event",
            "value_range": "complete destruction",
            "notes": "1258-02-13 Hulagu Khan 率いるモンゴル軍によるバグダード陥落で、"
                     "図書館・写本群が Tigris に投棄された伝承 (実際の規模は議論あり)。"
                     "アッバース朝カリフ制の終焉と同時。",
        },
        valid_from="1258-02-13", valid_from_precision="exact",
        valid_to="1258-02-13",   valid_to_precision="exact",
        confidence=0.7, source_id=src_hikma_wiki,
    )
    facets_inserted.append(("bayt_al_hikma", "scale", "mongol_destruction", f))

    # ---------- 比叡山延暦寺 -----------------------------------------------
    f = add_facet(
        ORG["hieizan"], "identity",
        {
            "dominant_identity": "天台法華宗 (最澄創建期)",
            "brand_or_name": "比叡山寺 → 延暦寺 (823 勅額)",
            "notes": "788 最澄が比叡山に一乗止観院を草創、805 入唐求法、"
                     "806 天台宗公認、822 大乗戒壇設立 (最澄没後 7 日)、"
                     "823 嵯峨天皇より延暦寺の勅額。",
        },
        valid_from="0788-01-01", valid_from_precision="year",
        valid_to="1175-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_groner,
    )
    facets_inserted.append(("hieizan", "identity", "saicho_founding", f))

    f = add_facet(
        ORG["hieizan"], "identity",
        {
            "dominant_identity": "鎌倉新仏教の母胎 (顕密体制の中核)",
            "brand_or_name": "延暦寺 (山門)",
            "notes": "12-13c に法然・親鸞・栄西・道元・日蓮らが比叡山で修学後に"
                     "新宗派を開く。本覚思想の発展期 (Stone 1999)。"
                     "山門 (延暦寺) と寺門 (園城寺) の分裂 (10c) も並行。",
        },
        valid_from="1175-01-01", valid_from_precision="century",
        valid_to="1571-09-29",   valid_to_precision="exact",
        confidence=0.8, source_id=src_stone,
    )
    facets_inserted.append(("hieizan", "identity", "kamakura_matrix", f))

    f = add_facet(
        ORG["hieizan"], "scale",
        {
            "phase": "medieval peak",
            "metric": "temple_complex",
            "value_range": "3000+ 子院・坊舎 (伝承)、僧兵数千",
            "notes": "中世盛期 (12-15c) の延暦寺は山中に 3000 余の堂塔伽藍を擁したと"
                     "伝えられ、僧兵は'山法師'として畏怖された。"
                     "数値は中世史料の伝承的記述、実数は不確定。",
        },
        valid_from="1175-01-01", valid_from_precision="century",
        valid_to="1571-09-29",   valid_to_precision="exact",
        confidence=0.6, source_id=src_hieizan_wiki,
        note="3000 院の数値は伝承的、実数推定は困難。",
    )
    facets_inserted.append(("hieizan", "scale", "medieval_peak", f))

    f = add_facet(
        ORG["hieizan"], "scale",
        {
            "phase": "Nobunaga's burning (1571)",
            "metric": "extinction_event",
            "value_range": "near-total destruction (堂塔焼失、僧侶虐殺)",
            "notes": "1571-09-30 (元亀2年9月12日) 織田信長の比叡山焼討で根本中堂以下"
                     "ほぼ全山焼失、数千人が殺害された。一時的に組織は壊滅。",
        },
        valid_from="1571-09-30", valid_from_precision="exact",
        valid_to="1571-09-30",   valid_to_precision="exact",
        confidence=0.85, source_id=src_hieizan_wiki,
    )
    facets_inserted.append(("hieizan", "scale", "nobunaga_burning", f))

    f = add_facet(
        ORG["hieizan"], "governance",
        {
            "regime": "江戸幕府公認・天海再興期 (徳川家庇護)",
            "decision_locus": "天台座主 + 江戸幕府寺社奉行の管理",
            "notes": "1584 豊臣秀吉により再興許可、1607 天海が東塔再建着手、"
                     "1642 慈眼大師天海による寛永期の本格復興。"
                     "徳川家光以降、東叡山寛永寺 (1625) と並ぶ天台総本山として再構築。",
        },
        valid_from="1584-01-01", valid_from_precision="year",
        valid_to="1868-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_hieizan_wiki,
    )
    facets_inserted.append(("hieizan", "governance", "edo_restoration", f))

    f = add_facet(
        ORG["hieizan"], "identity",
        {
            "dominant_identity": "現代日本天台宗の総本山 (宗教法人)",
            "brand_or_name": "天台宗総本山 比叡山延暦寺",
            "notes": "1868 神仏分離令、1872 修験道廃止令を経て近代化。"
                     "1951 宗教法人法下で宗教法人化。1994 ユネスコ世界遺産"
                     "(古都京都の文化財) 登録。",
        },
        valid_from="1868-04-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_hieizan_wiki,
    )
    facets_inserted.append(("hieizan", "identity", "modern", f))

    # ---------- Cluny 修道会 -----------------------------------------------
    f = add_facet(
        ORG["cluny"], "governance",
        {
            "regime": "創建期 - Burgundy 公爵 William I 寄進、ローマ教皇直属",
            "decision_locus": "Cluny 修道院長 (Berno 初代、910-927)",
            "notes": "910 Aquitaine 公 William I の寄進により創建。"
                     "ローマ聖座直属で世俗領主・地元司教からの独立を確保 (libertas)。",
        },
        valid_from="0910-09-11", valid_from_precision="year",
        valid_to="1049-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_iognaprat,
    )
    facets_inserted.append(("cluny", "governance", "founding", f))

    f = add_facet(
        ORG["cluny"], "scale",
        {
            "phase": "Cluniac Reform peak (Hugh of Semur era)",
            "metric": "monastic_houses",
            "value_range": "approx. 1000-2000 dependent priories at peak",
            "notes": "Abbot Hugh of Semur (1049-1109) と Peter the Venerable (1122-1156) "
                     "の時代に Cluniac ネットワーク最盛、欧州全域に約 1000-2000 の"
                     "従属修道院 (priorate) を擁した。Iogna-Prat (2002) 概観。",
        },
        valid_from="1049-01-01", valid_from_precision="year",
        valid_to="1156-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_iognaprat,
        note="数値は研究者により幅、ピーク値は 1100 院前後とする推定が多い。",
    )
    facets_inserted.append(("cluny", "scale", "peak", f))

    f = add_facet(
        ORG["cluny"], "governance",
        {
            "regime": "Cluniac Order (中央集権連邦)",
            "decision_locus": "Cluny 修道院長を頂点とするピラミッド型連邦、"
                              "全 priory が Cluny abbot に直属",
            "key_bodies": ["Abbot of Cluny", "General Chapter (1132 制度化)"],
            "notes": "従来のベネディクト各院自治モデルに対し、Cluny を頂点とする"
                     "中央集権ネットワークを構築。1132 General Chapter 制度化。"
                     "中世における初期'orderly federation'の実例。",
        },
        valid_from="1049-01-01", valid_from_precision="year",
        valid_to="1500-12-31",   valid_to_precision="century",
        confidence=0.8, source_id=src_iognaprat,
    )
    facets_inserted.append(("cluny", "governance", "centralized_federation", f))

    f = add_facet(
        ORG["cluny"], "scale",
        {
            "phase": "decline (12c onwards)",
            "metric": "relative_influence",
            "value_range": "シトー会・托鉢修道会の台頭でシェア低下",
            "notes": "12c 半ば以降、シトー会 (1098-)、フランシスコ・ドミニコ会"
                     "(13c 初頭) の台頭でクリュニー型の影響力が相対的に低下。"
                     "建築・財政の規模に比した宗教的革新の停滞も指摘される。",
        },
        valid_from="1156-01-01", valid_from_precision="year",
        valid_to="1789-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_iognaprat,
    )
    facets_inserted.append(("cluny", "scale", "decline", f))

    f = add_facet(
        ORG["cluny"], "scale",
        {
            "phase": "dissolution by French Revolution (1790)",
            "metric": "extinction_event",
            "value_range": "complete dissolution as religious order",
            "notes": "1789-11 国民議会の教会財産国有化決議、1790-02 修道誓願禁止令により"
                     "Cluny 修道会は解散。1798 母院 Cluny 修道院も売却され、"
                     "19c に大半の建物が解体された。",
        },
        valid_from="1790-02-13", valid_from_precision="exact",
        valid_to="1790-02-13",   valid_to_precision="exact",
        confidence=0.9, source_id=src_cluny_wiki,
    )
    facets_inserted.append(("cluny", "scale", "dissolution", f))

    f = add_facet(
        ORG["cluny"], "resource_base",
        {
            "primary": "領地寄進 (donations of land by lay nobility)",
            "secondary": ["intercessory prayers の対価としての寄進",
                          "domain agriculture", "tithes"],
            "notes": "貴族からの土地寄進 (in exchange for prayers for the dead) が"
                     "主要収入源。10-12c に膨大な所領を集積。"
                     "14c 以降は財政逼迫が顕著。",
        },
        valid_from="0910-09-11", valid_from_precision="year",
        valid_to="1789-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_iognaprat,
    )
    facets_inserted.append(("cluny", "resource_base", "land_donations", f))

    # ---------- 安東権氏門中 ------------------------------------------------
    f = add_facet(
        ORG["kwon_munjung"], "membership",
        {
            "basis": "父系血縁 (始祖 權幸 - 高麗太祖期、930s)",
            "eligibility": "權幸の男系子孫、嫡庶を初期は緩やかに含む",
            "notes": "高麗太祖王建を助けた權幸 (始祖) を起点とする父系血縁集団。"
                     "高麗末期までは族譜は未整備、口伝・墓誌等で系譜が伝承。",
        },
        valid_from="0930-01-01", valid_from_precision="decade",
        valid_to="1392-07-16",   valid_to_precision="year",
        confidence=0.6, source_id=src_kwon_jokbo,
        note="高麗期の門中組織化は限定的、Deuchler (1992) は朝鮮初期の確立を強調。",
    )
    facets_inserted.append(("kwon_munjung", "membership", "koryo_proto", f))

    f = add_facet(
        ORG["kwon_munjung"], "governance",
        {
            "regime": "朝鮮王朝期の門中 (宗中) 制度確立",
            "decision_locus": "宗孫 (宗家家督) + 門会 (門中会議)、書院・祠堂を中心",
            "key_bodies": ["宗家 (Jongga)", "門会", "祭享委員会"],
            "notes": "朝鮮王朝の儒教化により、嫡長子相続・父系制が制度化。"
                     "1476 安東權氏成化譜 (韓国最古現存族譜) 刊行で門中組織が"
                     "可視化。Deuchler (1992) は 15-16c を門中確立期と位置づける。",
        },
        valid_from="1392-07-17", valid_from_precision="year",
        valid_to="1910-08-29",   valid_to_precision="exact",
        confidence=0.85, source_id=src_deuchler,
    )
    facets_inserted.append(("kwon_munjung", "governance", "joseon", f))

    f = add_facet(
        ORG["kwon_munjung"], "identity",
        {
            "dominant_identity": "両班 (yangban) 名門としての門中アイデンティティ",
            "brand_or_name": "安東權氏 (Andong Kwon)",
            "notes": "朝鮮王朝期に複数の文科及第者・宰相を輩出する両班名門として確立。"
                     "本貫制 (本貫=安東) と族譜による集団アイデンティティの強化。",
        },
        valid_from="1476-01-01", valid_from_precision="year",
        valid_to="1910-08-29",   valid_to_precision="exact",
        confidence=0.85, source_id=src_deuchler,
    )
    facets_inserted.append(("kwon_munjung", "identity", "yangban", f))

    f = add_facet(
        ORG["kwon_munjung"], "governance",
        {
            "regime": "日帝期の門中 (制度的解体・私的存続)",
            "decision_locus": "宗孫 + 残存宗親会、公的制度から退却",
            "notes": "1910 韓国併合後、朝鮮戸籍令 (1922) 等により伝統的家族制度が"
                     "改変、創氏改名 (1939) など同化政策で門中の公的可視性が低下。"
                     "ただし族譜編纂・祭祀は私的に継続。",
        },
        valid_from="1910-08-29", valid_from_precision="exact",
        valid_to="1945-08-15",   valid_to_precision="exact",
        confidence=0.7, source_id=src_deuchler,
        note="Deuchler は植民地期の門中変容を扱うが詳細は二次研究に依存。",
    )
    facets_inserted.append(("kwon_munjung", "governance", "japanese_colonial", f))

    f = add_facet(
        ORG["kwon_munjung"], "identity",
        {
            "dominant_identity": "現代韓国の門中 (宗親会・文化的アイデンティティ)",
            "brand_or_name": "安東權氏宗親会 (Andong Kwon Jongchin-hoe)",
            "notes": "韓国独立後、宗親会 (clan association) として再編。"
                     "2008 戸主制廃止 (民法改正) で法的家父長制は終焉、"
                     "現代では文化的・社会的アイデンティティ集団として存続。"
                     "族譜は継続的に更新 (近年は電子化も)。",
        },
        valid_from="1945-08-15", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_deuchler,
    )
    facets_inserted.append(("kwon_munjung", "identity", "modern", f))

    # ---------- アル・アズハル ----------------------------------------------
    f = add_facet(
        ORG["al_azhar"], "legitimation_basis",
        {
            "basis": "ファーティマ朝シーア派 (Ismāʿīlī) 学院",
            "notes": "972 ファーティマ朝カリフ al-Muʿizz が新都カイロにジャーミィ (mosque) "
                     "を建立、後に Ismāʿīlī シーア派の教義教育機関 (madrasa) として発展。"
                     "988 al-ʿAzīz により正式に dār al-ʿilm として組織化。",
        },
        valid_from="0972-01-01", valid_from_precision="year",
        valid_to="1171-09-12",   valid_to_precision="year",
        confidence=0.85, source_id=src_dodge,
    )
    facets_inserted.append(("al_azhar", "legitimation_basis", "fatimid_shia", f))

    f = add_facet(
        ORG["al_azhar"], "legitimation_basis",
        {
            "basis": "スンニ派 (アイユーブ朝以降、シャーフィイー学派中心)",
            "notes": "1171 サラディン (Salāḥ al-Dīn) によるファーティマ朝終焉と同時に"
                     "アズハルでのシーア派教義教育を停止、約 100 年の閉鎖期間を経て"
                     "13c 後半にスンニ派 madrasa として復興。"
                     "後にスンニ 4 学派 (シャーフィイー、ハナフィー、マーリキー、ハンバル) "
                     "全てを教育する総合機関に。",
        },
        valid_from="1171-09-13", valid_from_precision="year",
        valid_to="1517-01-22",   valid_to_precision="year",
        confidence=0.85, source_id=src_dodge,
    )
    facets_inserted.append(("al_azhar", "legitimation_basis", "ayyubid_sunni", f))

    f = add_facet(
        ORG["al_azhar"], "governance",
        {
            "regime": "オスマン期 (シャイフ・アル=アズハル制度確立)",
            "decision_locus": "シャイフ・アル=アズハル (Shaykh al-Azhar) を頂点、"
                              "オスマン総督 (vālī) の保護下で運営",
            "notes": "1517 オスマン朝マムルーク朝征服後、アズハルはオスマン帝国の"
                     "イスラーム学術中心として継続。17c に Shaykh al-Azhar の"
                     "職位が制度化、現在まで継続する最高権威。",
        },
        valid_from="1517-01-22", valid_from_precision="year",
        valid_to="1961-06-04",   valid_to_precision="exact",
        confidence=0.85, source_id=src_dodge,
    )
    facets_inserted.append(("al_azhar", "governance", "ottoman", f))

    f = add_facet(
        ORG["al_azhar"], "governance",
        {
            "regime": "近代国営大学化 (Nasser 改革)",
            "decision_locus": "エジプト政府 (Ministry of Awqāf 経由)、"
                              "Shaykh al-Azhar は政府任命",
            "key_bodies": ["Supreme Council of al-Azhar",
                           "Islamic Research Academy"],
            "notes": "1961 ナーセル政権下の Law 103 によりアズハルが近代国営大学化、"
                     "従来の宗教学に加え医学・工学・農学等の世俗科目を導入。"
                     "Shaykh al-Azhar は事実上政府指名となる。",
        },
        valid_from="1961-06-05", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.9, source_id=src_azhar_wiki,
    )
    facets_inserted.append(("al_azhar", "governance", "nasser_state", f))

    f = add_facet(
        ORG["al_azhar"], "identity",
        {
            "dominant_identity": "スンニ・イスラーム世界の最高権威機関",
            "brand_or_name": "Al-Azhar al-Sharīf",
            "notes": "アイユーブ朝以降、スンニ・イスラーム学術の権威機関として"
                     "中東・北アフリカ・東南アジア等から学生を集める世界最古級の"
                     "大学 (継続稼働期間としてはボローニャと並ぶ)。",
        },
        valid_from="1300-01-01", valid_from_precision="century",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_dodge,
    )
    facets_inserted.append(("al_azhar", "identity", "sunni_authority", f))

    # ---------- ボローニャ大学 ----------------------------------------------
    f = add_facet(
        ORG["bologna"], "governance",
        {
            "regime": "universitas scholarium (学生組合) - 中世自治型",
            "decision_locus": "学生 (universitas) による rector 選出、"
                              "教師の雇用・規則制定権",
            "key_bodies": ["universitas citramontanorum (アルプス以南学生組合)",
                           "universitas ultramontanorum (アルプス以北学生組合)",
                           "rector"],
            "notes": "中世のボローニャは'学生大学'モデル (パリの教師大学型と対比)。"
                     "学生が組合を組み、教師を雇用。1158 Authentica Habita "
                     "(Frederick I) で学生の法的保護が確立。",
        },
        valid_from="1088-01-01", valid_from_precision="year",
        valid_to="1500-12-31",   valid_to_precision="century",
        confidence=0.8, source_id=src_verger,
        note="1088 創立年は 1888 Carducci の祝祭で確定された慣例的年次、"
             "実際の制度形成は 12c 中葉以降。",
    )
    facets_inserted.append(("bologna", "governance", "medieval_universitas", f))

    f = add_facet(
        ORG["bologna"], "identity",
        {
            "dominant_identity": "ローマ法 (Corpus Iuris Civilis) 研究の中心",
            "brand_or_name": "Bologna 法学派 (Glossators)",
            "notes": "Irnerius (c.1050-c.1125) を祖とする Glossators 学派が"
                     "ユスティニアヌス法典の体系的注釈を行い、欧州のローマ法復興の"
                     "中心地となる。Decretum Gratiani (c.1140) で教会法も並立。",
        },
        valid_from="1088-01-01", valid_from_precision="year",
        valid_to="1400-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_verger,
    )
    facets_inserted.append(("bologna", "identity", "roman_law", f))

    f = add_facet(
        ORG["bologna"], "governance",
        {
            "regime": "教皇庁・地元コムーネの管理下 (近世)",
            "decision_locus": "教皇国家 (1506-1797) 統治下、Bologna senate と"
                              "教皇 legate による共同管理",
            "notes": "1506 教皇 Julius II による Bologna 併合以降、教皇国家の"
                     "管轄下に。学生組合の自治権は弱体化、教師の権限が増大。"
                     "16c に植物園 (1568)・解剖学劇場 (1637) 等近代学問装置を導入。",
        },
        valid_from="1506-01-01", valid_from_precision="year",
        valid_to="1797-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_brizzi,
    )
    facets_inserted.append(("bologna", "governance", "papal_state", f))

    f = add_facet(
        ORG["bologna"], "governance",
        {
            "regime": "近代イタリア国民国家化",
            "decision_locus": "イタリア教育省 (Ministero della Pubblica Istruzione)、"
                              "Casati Law (1859) 適用",
            "notes": "1859 Casati Law によりサルデーニャ王国の大学制度に編入、"
                     "1861 イタリア統一後は国立大学として国民国家インフラに統合。"
                     "1888 創立 800 年祭 (Carducci) でブランド再構築。",
        },
        valid_from="1859-11-13", valid_from_precision="year",
        valid_to="1999-06-19",   valid_to_precision="exact",
        confidence=0.85, source_id=src_brizzi,
    )
    facets_inserted.append(("bologna", "governance", "italian_state", f))

    f = add_facet(
        ORG["bologna"], "identity",
        {
            "dominant_identity": "EU 高等教育圏の中核 (Bologna Process 主導大学)",
            "brand_or_name": "Alma Mater Studiorum - Università di Bologna",
            "notes": "1999-06-19 Bologna Declaration により欧州高等教育圏 (EHEA) 構築の"
                     "起点となる。3-2-3 サイクル等の国際標準を主導。"
                     "現在 EU 内最大級の総合大学。",
        },
        valid_from="1999-06-19", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.9, source_id=src_bologna_wiki,
    )
    facets_inserted.append(("bologna", "identity", "eu_hub", f))

    # ---------- シトー会 ---------------------------------------------------
    f = add_facet(
        ORG["cistercians"], "identity",
        {
            "dominant_identity": "Cluny 派の世俗化への反動として創設",
            "brand_or_name": "Ordo Cisterciensis (Cîteaux 修道院)",
            "notes": "1098 Robert of Molesme が Cîteaux に新修道院を創設。"
                     "Cluny 派の華美な典礼・領地経営への反動として、原始ベネディクト規則"
                     "への回帰、労働 (manual labor)・簡素・荒野立地を理念化。",
        },
        valid_from="1098-03-21", valid_from_precision="exact",
        valid_to="1150-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_berman,
    )
    facets_inserted.append(("cistercians", "identity", "anti_cluny", f))

    f = add_facet(
        ORG["cistercians"], "scale",
        {
            "phase": "12c expansion peak",
            "metric": "monastic_houses",
            "value_range": "approx. 700+ houses by end of 12c",
            "notes": "Bernard of Clairvaux (1090-1153) のカリスマと Carta Caritatis "
                     "(1119) の制度化により急拡大。12c 末に約 700 院、"
                     "13c 末に約 750 院に達する。Berman (2000) は実質的'Order'形成は"
                     "12c 中葉以降と論じる。",
        },
        valid_from="1119-01-01", valid_from_precision="year",
        valid_to="1300-12-31",   valid_to_precision="century",
        confidence=0.8, source_id=src_berman,
    )
    facets_inserted.append(("cistercians", "scale", "12c_peak", f))

    f = add_facet(
        ORG["cistercians"], "governance",
        {
            "regime": "Carta Caritatis モデル - 'filiation' 連邦",
            "decision_locus": "General Chapter (年次総会) + 母院 (mother house) "
                              "による娘院 (daughter house) の visitation",
            "key_bodies": ["General Chapter (年次)", "Abbot of Cîteaux",
                           "filiation tree of mother-daughter houses"],
            "notes": "Cluny の中央集権ピラミッドと異なり、各院 abbot が"
                     "母院 abbot から visitation を受ける'filiation'モデル。"
                     "年次 General Chapter で全院 abbot が議決。",
        },
        valid_from="1119-01-01", valid_from_precision="year",
        valid_to="1517-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_berman,
    )
    facets_inserted.append(("cistercians", "governance", "filiation", f))

    f = add_facet(
        ORG["cistercians"], "scale",
        {
            "phase": "Reformation impact",
            "metric": "monastic_houses",
            "value_range": "プロテスタント諸国の数百院解散、欧州残存数大幅減",
            "notes": "16c プロテスタント宗教改革でドイツ・北欧・英国の"
                     "多数のシトー院が解散。1789-1815 仏革命・ナポレオン期で"
                     "フランス・オーストリア等の残存院も縮小。",
        },
        valid_from="1517-10-31", valid_from_precision="year",
        valid_to="1815-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_cistercian_wiki,
    )
    facets_inserted.append(("cistercians", "scale", "reformation_decline", f))

    f = add_facet(
        ORG["cistercians"], "identity",
        {
            "dominant_identity": "OCSO (Trappist) と OCist の二分岐",
            "brand_or_name": "OCSO (Order of Cistercians of the Strict Observance) / "
                             "OCist (Order of Cistercians)",
            "notes": "1664 La Trappe 修道院での Rancé 改革を起点とする厳格派が"
                     "1892 教皇 Leo XIII により独立 (OCSO=Trappists)。"
                     "緩和派 (OCist) と並立、共に Cîteaux を始祖とするが別法人。",
        },
        valid_from="1892-10-17", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_cistercian_wiki,
    )
    facets_inserted.append(("cistercians", "identity", "ocso_ocist_split", f))

    f = add_facet(
        ORG["cistercians"], "resource_base",
        {
            "primary": "labora (manual agricultural labor) と grange 経営",
            "secondary": ["sheep husbandry (英国)", "metallurgy (Champagne)",
                          "wine (Burgundy)"],
            "notes": "シトー会は荒野立地と労働の理念から、未開地開拓・牧羊・"
                     "鉄鋼業・ワイン醸造等の technological innovator として知られる。"
                     "中世農業革命の主要担い手。",
        },
        valid_from="1098-03-21", valid_from_precision="exact",
        valid_to="1500-12-31",   valid_to_precision="century",
        confidence=0.8, source_id=src_berman,
    )
    facets_inserted.append(("cistercians", "resource_base", "labor_grange", f))

    # ---------- ナクシュバンディー教団 -------------------------------------
    f = add_facet(
        ORG["naqshbandi"], "identity",
        {
            "dominant_identity": "中央アジア起源スーフィー道団 (Khwājagān 系)",
            "brand_or_name": "Ṭarīqa Naqshbandiyya",
            "notes": "Bahā' al-Dīn Naqshband (1318-1389, ブハラ近郊) を初代マスターとする"
                     "スーフィー道団。Khwājagān (中央アジア・スーフィー学派) の伝統を継承、"
                     "silent dhikr (無声祈念) を特徴とする。",
        },
        valid_from="1380-01-01", valid_from_precision="decade",
        valid_to="1500-12-31",   valid_to_precision="century",
        confidence=0.8, source_id=src_algar,
        note="1380 を活動開始の便宜的年次として採用 (Naqshband 60代頃)。",
    )
    facets_inserted.append(("naqshbandi", "identity", "central_asian_origin", f))

    f = add_facet(
        ORG["naqshbandi"], "territory",
        {
            "extent_label": "オスマン帝国・中央アジアへの拡大",
            "key_regions": ["Transoxiana", "Khorasan", "Anatolia",
                            "Balkans", "Crimea"],
            "notes": "16c にオスマン領内へ拡大、特にイスタンブール・アナトリア・"
                     "バルカンに浸透。Aḥrārī 系統 (ʿUbaydullāh Aḥrār, d.1490) が"
                     "拡大の中核。",
        },
        valid_from="1500-01-01", valid_from_precision="century",
        valid_to="1750-12-31",   valid_to_precision="century",
        confidence=0.75, source_id=src_algar,
    )
    facets_inserted.append(("naqshbandi", "territory", "ottoman_expansion", f))

    f = add_facet(
        ORG["naqshbandi"], "identity",
        {
            "dominant_identity": "Mujaddidi 分派 (インド進出、シャリーア重視改革)",
            "brand_or_name": "Naqshbandiyya-Mujaddidiyya",
            "notes": "Aḥmad Sirhindī (Mujaddid alf-i thānī, 1564-1624) による"
                     "改革分派、ムガル朝インドで影響力拡大。"
                     "シャリーア (イスラーム法) との厳密な整合とイスラーム正統主義を強調。",
        },
        valid_from="1600-01-01", valid_from_precision="century",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_algar,
    )
    facets_inserted.append(("naqshbandi", "identity", "mujaddidi", f))

    f = add_facet(
        ORG["naqshbandi"], "identity",
        {
            "dominant_identity": "Khālidī 分派 (近代オスマン・クルド地域)",
            "brand_or_name": "Naqshbandiyya-Khālidiyya",
            "notes": "Mawlānā Khālid al-Baghdādī (1779-1827) によるクルド地域での"
                     "革新分派。19c オスマン帝国の改革に対する反応として広範に拡大、"
                     "Caucasus・Indonesia 等にも到達。",
        },
        valid_from="1811-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_algar,
    )
    facets_inserted.append(("naqshbandi", "identity", "khalidi", f))

    f = add_facet(
        ORG["naqshbandi"], "territory",
        {
            "extent_label": "現代世界拡散 (西欧・北米・東南アジア)",
            "key_regions": ["Turkey", "Daghestan/Chechnya", "Pakistan",
                            "Indonesia", "Western Europe", "North America"],
            "notes": "20c 以降、特に Khālidī 系統が北コーカサス (反ソ運動の宗教的基盤)、"
                     "東南アジア (Haqqāniyya 等)、ディアスポラを通じた西欧・北米への"
                     "拡散。現代スーフィズムの主要グローバル道団の一つ。",
        },
        valid_from="1900-01-01", valid_from_precision="century",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_naqshbandi_wiki,
    )
    facets_inserted.append(("naqshbandi", "territory", "modern_global", f))

    f = add_facet(
        ORG["naqshbandi"], "governance",
        {
            "regime": "シャイフ-ムリード継承 (silsila ベース)",
            "decision_locus": "各 silsila (継承系統) の Shaykh が独立に弟子集団を運営、"
                              "中央権威なし",
            "notes": "他のスーフィー道団同様、中央集権的組織はもたず、"
                     "silsila (霊的系譜) を通じた Shaykh-murīd 関係でネットワーク化。"
                     "Mujaddidi、Khālidī 等の主要分派は別個の silsila を構成。",
        },
        valid_from="1380-01-01", valid_from_precision="decade",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_algar,
    )
    facets_inserted.append(("naqshbandi", "governance", "silsila", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ
    # =========================================================================
    print("=" * 70)
    print(f"Phase 4 Team B - 投入 facet レコード数: {len(facets_inserted)}")
    print("=" * 70)
    print()

    print("Q1. 担当 8 ケースの facet 件数")
    print("-" * 70)
    for key, oid in ORG.items():
        rows = cur.execute(
            """
            SELECT o.canonical_name, COUNT(*) AS n,
                   GROUP_CONCAT(DISTINCT f.facet_type)
            FROM organization_temporal_facet f
            JOIN organization o ON o.organization_id = f.organization_id
            WHERE f.organization_id = ?
            GROUP BY o.canonical_name
            """,
            (oid,),
        ).fetchall()
        for name, n, types in rows:
            print(f"  [{key}] {name}: {n} facets ({types})")
    print()

    print("Q2. 1100 年時点の Cluny 全 facet スナップショット")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, facet_value, confidence, valid_from, valid_to
        FROM organization_temporal_facet
        WHERE organization_id = ?
          AND (valid_from IS NULL OR valid_from <= '1100-01-01')
          AND (valid_to   IS NULL OR valid_to   >  '1100-01-01')
        ORDER BY facet_type
        """,
        (ORG["cluny"],),
    ).fetchall()
    for ft, fv, conf, vf, vt in rows:
        v = json.loads(fv)
        summary = (v.get("phase") or v.get("regime") or v.get("primary")
                   or v.get("dominant_identity") or v.get("metric") or "—")
        print(f"  [{ft}] {vf} → {vt or 'open'} | conf={conf} | {summary}")
    print()

    print("Q3. アル・アズハルの legitimation_basis 推移")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'legitimation_basis'
        ORDER BY valid_from
        """,
        (ORG["al_azhar"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('basis')}")
    print()

    print("Q4. facet_type 分布 (本投入分のみ - 担当 8 ケース)")
    print("-" * 70)
    placeholders = ",".join("?" for _ in ORG)
    rows = cur.execute(
        f"""
        SELECT facet_type, COUNT(*) FROM organization_temporal_facet
        WHERE organization_id IN ({placeholders})
        GROUP BY facet_type ORDER BY 2 DESC
        """,
        list(ORG.values()),
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")
    print()

    print("Q5. DB 全体の facet 件数 (Phase 4 Team B 投入後)")
    print("-" * 70)
    total = cur.execute(
        "SELECT COUNT(*) FROM organization_temporal_facet"
    ).fetchone()[0]
    print(f"  organization_temporal_facet 総件数: {total}")
    org_total = cur.execute(
        "SELECT COUNT(DISTINCT organization_id) FROM organization_temporal_facet"
    ).fetchone()[0]
    print(f"  facet 保有組織数: {org_total}")

    conn.close()


if __name__ == "__main__":
    main()
