#!/usr/bin/env python3
"""Phase 4 並列チーム C: 前近代国家・帝国行政 4 ケースの temporal facet 投入

対象組織 (organization_id 既存 verified 2026-05-03):
  - ハンザ同盟 (Hanseatic League)             769ae2b129534516b257581907423f68  (1159-1669)
  - オスマン・ティマール制 (Ottoman Timar)     8e2f00957ae447449ba2ed7fdd208a4f  (1362-1831)
  - インカ帝国 (Tahuantinsuyu)                 3e4d8db1e62f4d858b17cb6ff14b6c81  (1438-1572)
  - ムガル朝マンサブダール制 (Mansabdari)       18094f83a7624dd8a797a467e7148d64  (1571-1858)

facet_type 集合:
  membership / governance / resource_base / territory /
  technology / identity / scale / legitimation_basis

各 facet は claim 経由で出典あり。捏造禁止、不確実な日付・粒度は precision で表現。
各ケース 5-7 facet (合計 ~25 facet)。

主要参考文献:
  - ハンザ:        Dollinger 1964, Hammel-Kiesow 2000
  - ティマール:    İnalcık 1973, Ágoston 2014
  - インカ:        D'Altroy 2014, Rowe 1946
  - マンサブダール: Athar Ali 1985, Habib 1999
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "hansa":     "769ae2b129534516b257581907423f68",
    "timar":     "8e2f00957ae447449ba2ed7fdd208a4f",
    "inca":      "3e4d8db1e62f4d858b17cb6ff14b6c81",
    "mansabdar": "18094f83a7624dd8a797a467e7148d64",
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
                  recorded_by="claude_phase4_premodern_states"):
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
    # SOURCES (実在文献。捏造禁止)
    # =========================================================================

    # ---- ハンザ同盟 ----
    src_dollinger = add_source(
        "secondary_literature",
        "Dollinger, P. (1970, orig. 1964) The German Hansa",
        authors=["Philippe Dollinger"],
        publication_date="1970",
        publisher="Stanford University Press / Macmillan",
        reliability_score=0.9,
        reliability_basis="ハンザ研究の古典的標準書 (仏語原著 1964)。"
                          "Wendish 都市の核形成、Kontor 4 拠点 (London Steelyard, "
                          "Bruges, Bergen, Novgorod Peterhof)、Hansetag (ディエット) "
                          "の機能、最後のディエット 1669 までを包括的に記述。",
        bias_notes="ドイツ史学側からの整理が中心。Novgorod 側の記録は限定的に扱われる傾向。",
        redistribution="attribution_required",
    )
    src_hammel_kiesow = add_source(
        "secondary_literature",
        "Hammel-Kiesow, R. (2000) Die Hanse",
        authors=["Rolf Hammel-Kiesow"],
        publication_date="2000",
        publisher="C.H. Beck",
        reliability_score=0.9,
        reliability_basis="現代ドイツ語圏の代表的概説。Lübeck 中心の都市同盟形成、"
                          "都市数のピーク (14-15c に約 200 都市)、衰退 (16c 以降) を整理。",
        redistribution="attribution_required",
    )

    # ---- オスマン・ティマール制 ----
    src_inalcik_1973 = add_source(
        "secondary_literature",
        "İnalcık, H. (1973) The Ottoman Empire: The Classical Age 1300-1600",
        authors=["Halil İnalcık"],
        publication_date="1973",
        publisher="Weidenfeld & Nicolson",
        reliability_score=0.95,
        reliability_basis="オスマン古典期の標準書。Murad I 期のティマール制成立、"
                          "16c 古典期の sipahi 約 4 万騎、土地台帳 (tahrir defter) 制度、"
                          "中央集権下の軍事封土の機能を体系的に記述。",
        redistribution="attribution_required",
    )
    src_agoston_2014 = add_source(
        "secondary_literature",
        "Ágoston, G. (2014) 'Firearms and Military Adaptation: The Ottomans and the European Military Revolution, 1450-1800', Journal of World History 25",
        authors=["Gábor Ágoston"],
        publication_date="2014",
        publisher="University of Hawaii Press",
        reliability_score=0.9,
        reliability_basis="オスマン軍事史。火器導入 (15c-) と sipahi 騎兵中心体制の"
                          "相対的衰退、17c 以降の Çiftlik 化と財政基盤の変質、"
                          "1831 Mahmud II による正式廃止までの過程を整理。",
        bias_notes="軍事革命論を相対化する立場、ヨーロッパ中心史観への批判を含む。",
        redistribution="attribution_required",
    )

    # ---- インカ帝国 ----
    src_daltroy = add_source(
        "secondary_literature",
        "D'Altroy, T.N. (2014) The Incas, 2nd ed.",
        authors=["Terence N. D'Altroy"],
        publication_date="2014",
        publisher="Wiley-Blackwell",
        reliability_score=0.95,
        reliability_basis="現代インカ研究の標準書。Pachacuti による拡大開始 (1438-)、"
                          "Topa Inka 全盛期 (1471-93)、四分国 (Tahuantinsuyu) 構造、"
                          "mit'a 労役制、khipu 記録、Huayna Capac 死後の内戦 (1527-32)、"
                          "Pizarro 征服 (1532-) と Vilcabamba 残党 (1572 終焉) を網羅。",
        redistribution="attribution_required",
    )
    src_rowe_1946 = add_source(
        "secondary_literature",
        "Rowe, J.H. (1946) 'Inca Culture at the Time of the Spanish Conquest', Handbook of South American Indians, Vol. 2",
        authors=["John H. Rowe"],
        publication_date="1946",
        publisher="Smithsonian Institution / Bureau of American Ethnology",
        reliability_score=0.85,
        reliability_basis="20 世紀後半の古典的整理。Sapa Inca を頂点とする官僚体制、"
                          "decimal 行政区分 (10/100/1000/10000)、ayllu 共同体基盤、"
                          "stone-age 技術 (青銅・銅) の規模と限界を定式化。",
        bias_notes="20c 中葉の構造主義的整理、近年の考古学的再評価で部分的に修正されている。",
        redistribution="attribution_required",
    )

    # ---- ムガル朝マンサブダール制 ----
    src_athar_ali = add_source(
        "secondary_literature",
        "Athar Ali, M. (1985) The Apparatus of Empire: Awards of Ranks, Offices and Titles to the Mughal Nobility 1574-1658",
        authors=["M. Athar Ali"],
        publication_date="1985",
        publisher="Oxford University Press",
        reliability_score=0.95,
        reliability_basis="マンサブダール制研究の標準書。Akbar による創設 (1571 前後)、"
                          "1595 年の zat (個人ランク) / sawar (騎兵ランク) 二重制度確立、"
                          "貴族の出自構成 (イラン人・トゥラン人・ラージプート等) を実証。",
        redistribution="attribution_required",
    )
    src_habib_1999 = add_source(
        "secondary_literature",
        "Habib, I. (1999, orig. 1963) The Agrarian System of Mughal India 1556-1707, 2nd ed.",
        authors=["Irfan Habib"],
        publication_date="1999",
        publisher="Oxford University Press",
        reliability_score=0.95,
        reliability_basis="ムガル農業・財政史の決定版。jagir (給地) 配分制度、"
                          "Aurangzeb 期 (1658-1707) の jagir 不足危機 (be-jagiri)、"
                          "後期 (18c) の地方知事 (nawab) 自立化と帝国崩壊、"
                          "1858 East India Company による正式廃止を整理。",
        bias_notes="マルクス主義的経済史枠組み、上層構造の文化的側面は手薄。",
        redistribution="attribution_required",
    )

    # 補助 (Wikipedia 概観、低 reliability で参照のみ)
    src_wiki_inca = add_source(
        "web",
        "Wikipedia: Inca Empire - administrative divisions, mit'a, conquest",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Inca_Empire"},
        accessed_at="2026-05-03",
        reliability_score=0.55,
        reliability_basis="百科事典の概観。Tahuantinsuyu 4 suyu 区分、Pizarro 1532-11-16 "
                          "Cajamarca 遭遇、Atahualpa 処刑 1533-07-26、Vilcabamba 1572 終焉。",
        redistribution="public_redistributable",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # =========================================================================
    # ハンザ同盟 (1159-1669): membership / governance / territory / scale / resource_base / legitimation_basis
    # =========================================================================

    # 1) 形成期: Wendish 都市群 (Lübeck 中心)
    f = add_facet(
        ORG["hansa"], "membership",
        {
            "basis": "Wendish 都市群 (Lübeck, Hamburg, Wismar, Rostock 等) の商人ギルド連合",
            "eligibility": "Lübeck 法 (Lübisches Recht) を採る北独諸都市の商人",
            "approximate_count": "10-30 都市規模",
            "notes": "1159 Lübeck 再建 (Heinrich der Löwe) を起点に Wendish 都市が"
                     "海外商業のため相互保護同盟を形成。都市同盟 (Städtebund) 化以前は"
                     "商人の Hansa (集団) としての性格が強い。",
        },
        valid_from="1159-01-01", valid_from_precision="year",
        valid_to="1280-12-31",   valid_to_precision="century",
        confidence=0.7, source_id=src_dollinger,
        note="ハンザ同盟の正式成立年は研究者により幅 (1159 Lübeck 再建説 / 1241 Lübeck-Hamburg 条約説 / 14c 都市同盟化説)。",
    )
    facets_inserted.append(("hansa", "membership", "wendish_core", f))

    # 2) 全盛期: 約 200 都市
    f = add_facet(
        ORG["hansa"], "membership",
        {
            "basis": "北海・バルト海沿岸を中心とする都市同盟 (Städtebund)",
            "eligibility": "Hansetag (ディエット) 参加都市、Lübeck 法または同等の市民法を有する",
            "approximate_count": "ピーク時 約 200 都市 (中核 70-80、周辺含む)",
            "regions": ["北独", "低地諸国一部", "バルト海沿岸 (Riga, Reval, Danzig)",
                        "Westfalen", "Saxony"],
            "notes": "14-15c が都市数のピーク域。Hammel-Kiesow (2000) は中核都市約 70、"
                     "周辺 Beihansa を含めると 200 程度と整理。",
        },
        valid_from="1281-01-01", valid_from_precision="century",
        valid_to="1500-12-31",   valid_to_precision="century",
        confidence=0.75, source_id=src_hammel_kiesow,
    )
    facets_inserted.append(("hansa", "membership", "peak_200", f))

    # 3) 衰退期
    f = add_facet(
        ORG["hansa"], "membership",
        {
            "basis": "中核都市の縮減、地域領邦国家の台頭による都市自治の侵食",
            "approximate_count": "16c 後半は実質 30 都市以下、17c には 10 都市未満",
            "notes": "オランダ・イングランド商業の台頭、三十年戦争 (1618-1648) の打撃、"
                     "領邦国家化により参加都市が縮減。1669 最後の Hansetag には "
                     "Lübeck/Hamburg/Bremen 等 9 都市のみ出席。",
        },
        valid_from="1501-01-01", valid_from_precision="century",
        valid_to="1669-09-01",   valid_to_precision="exact",
        confidence=0.8, source_id=src_dollinger,
    )
    facets_inserted.append(("hansa", "membership", "decline", f))

    # 4) territory: Kontor 4 拠点
    f = add_facet(
        ORG["hansa"], "territory",
        {
            "extent_label": "海外 4 大 Kontor (商館) ネットワーク",
            "key_regions": ["London (Steelyard, ~1320s 確立)",
                            "Bruges (Flanders, 14c)",
                            "Bergen (Norway, Tyske Brygge 14c-)",
                            "Novgorod (Peterhof, 13c-1494)"],
            "notes": "ハンザの実体は『領土』ではなく Kontor (在外商館) と提携都市の"
                     "ネットワーク。各 Kontor は商人の自治区として治外法権的特権を持つ。"
                     "Novgorod Peterhof は 1494 Ivan III により閉鎖。",
        },
        valid_from="1300-01-01", valid_from_precision="century",
        valid_to="1600-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_dollinger,
        note="領域国家ではないため facet_type=territory には注釈付きで Kontor 網を記録。",
    )
    facets_inserted.append(("hansa", "territory", "kontor_network", f))

    # 5) governance: Hansetag (ディエット) 体制
    f = add_facet(
        ORG["hansa"], "governance",
        {
            "regime": "Hansetag (都市代表会議) による合議、常設執行機関なし",
            "decision_locus": "Lübeck を de facto 議長都市とする都市代表会議 (Hansetag)、"
                              "決議は出席都市の同意ベース",
            "key_bodies": ["Hansetag (ディエット)", "Lübeck 市参事会",
                           "各 Kontor の Älterleute (長老)"],
            "notes": "中央政府・常設官僚機構を持たない『連合』型統治。"
                     "Hansetag の招集頻度は中世盛期で数年に 1 回、衰退期は不定期。"
                     "最後の Hansetag は 1669 年。",
        },
        valid_from="1356-01-01", valid_from_precision="year",
        valid_to="1669-09-01",   valid_to_precision="exact",
        confidence=0.85, source_id=src_dollinger,
        note="1356 が最初の正式 Hansetag (Lübeck) とされる。",
    )
    facets_inserted.append(("hansa", "governance", "hansetag", f))

    # 6) resource_base
    f = add_facet(
        ORG["hansa"], "resource_base",
        {
            "primary": "長距離海上交易 (バルト海-北海)",
            "key_commodities": ["塩 (Lüneburg)", "ニシン (Skåne)", "穀物 (Prussia/Livonia)",
                                "毛皮 (Novgorod)", "蜜蝋", "毛織物 (Flanders)",
                                "stockfish (Bergen)", "木材・タール"],
            "secondary": ["都市の関税・特権収入"],
            "notes": "バルト海原料 (穀物・木材・毛皮・魚) と西欧製品 (毛織物・塩) の"
                     "中継貿易が中核。コグ船 (Kogge) による大量輸送が技術的基盤。",
        },
        valid_from="1200-01-01", valid_from_precision="century",
        valid_to="1550-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_hammel_kiesow,
    )
    facets_inserted.append(("hansa", "resource_base", "trade_commodities", f))

    # 7) legitimation_basis
    f = add_facet(
        ORG["hansa"], "legitimation_basis",
        {
            "basis": "皇帝・諸侯からの個別特許状 (privileges) と都市法の相互承認",
            "notes": "ハンザは超国家的『主権』を持たず、各都市が皇帝・国王・諸侯から"
                     "獲得した個別特権を集合的に運用する形で正統性を確保。"
                     "Lübeck 法を共通の法的基盤とする。",
        },
        valid_from="1200-01-01", valid_from_precision="century",
        valid_to="1669-09-01",   valid_to_precision="exact",
        confidence=0.75, source_id=src_dollinger,
    )
    facets_inserted.append(("hansa", "legitimation_basis", "privileges", f))

    # =========================================================================
    # オスマン・ティマール制 (1362-1831): governance / scale / resource_base / membership / territory / legitimation_basis
    # =========================================================================

    # 1) 成立期 (Murad I)
    f = add_facet(
        ORG["timar"], "governance",
        {
            "regime": "ティマール制創設期 - 軍事封土の制度化",
            "decision_locus": "スルタン (Murad I-) → beylerbey (州知事) → sancakbeyi → ティマールリオット (sipahi)",
            "key_bodies": ["スルタン直轄宮廷", "州 (eyalet/beylerbeylik)", "県 (sancak)"],
            "notes": "Murad I 期 (1362-1389) にバルカン征服と並行してティマール制が制度化。"
                     "土地から得られる収入を sipahi に給与の代わりに割り当て、"
                     "騎兵動員義務を課す軍事-財政システム。",
        },
        valid_from="1362-01-01", valid_from_precision="year",
        valid_to="1450-12-31",   valid_to_precision="century",
        confidence=0.75, source_id=src_inalcik_1973,
        note="制度の段階的形成のため開始年は厳密ではない。Murad I 即位を起点と暫定。",
    )
    facets_inserted.append(("timar", "governance", "founding", f))

    # 2) 古典期 (16c)
    f = add_facet(
        ORG["timar"], "scale",
        {
            "metric": "sipahi 騎兵数",
            "value_range": "approx. 40,000 sipahi (16c 古典期)",
            "supporting": "tahrir defter (土地台帳) による定期的な収入再配分、"
                          "ティマール (timar) / zeamet (中ランク) / has (大ランク) の三層",
            "notes": "İnalcık (1973) は Süleyman 期 (1520-66) のヨーロッパ・アナトリア両州で"
                     "ティマール sipahi 約 4 万騎、加えてイェニチェリ (常備歩兵) 約 1.2 万を整理。",
        },
        valid_from="1500-01-01", valid_from_precision="century",
        valid_to="1600-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_inalcik_1973,
    )
    facets_inserted.append(("timar", "scale", "classical_peak", f))

    # 3) resource_base: 土地収入による軍事動員
    f = add_facet(
        ORG["timar"], "resource_base",
        {
            "primary": "農業土地収入 (öşür/tithe + raiyyet rüsumu/peasant dues) の prebendal 配分",
            "secondary": ["スルタン直轄領 (havâss-ı hümâyûn)", "戦利品"],
            "notes": "貨幣俸給ではなく土地 fief を sipahi に給与代わりに割り当てる prebendal system。"
                     "tahrir defter で 10-30 年ごとに収入評価を更新し再配分。",
        },
        valid_from="1400-01-01", valid_from_precision="century",
        valid_to="1600-12-31",   valid_to_precision="century",
        confidence=0.85, source_id=src_inalcik_1973,
    )
    facets_inserted.append(("timar", "resource_base", "prebendal", f))

    # 4) 衰退期: Çiftlik 化、火器導入による sipahi 相対化
    f = add_facet(
        ORG["timar"], "governance",
        {
            "regime": "ティマール制の侵食期 - Çiftlik (大私有地) 化と中央財政化",
            "decision_locus": "中央財政 (mukataa 徴税請負) と地方有力者 (ayan) への移行、"
                              "ティマール sipahi の動員力低下",
            "notes": "17c 以降、火器歩兵 (tüfekçi/イェニチェリ) の比重増大により"
                     "ティマール騎兵の戦術的価値が低下。同時に多くのティマールが"
                     "私有大農場 (Çiftlik) に転化、徴税は iltizam (請負制) へ。"
                     "Ágoston (2014) は軍事革命論との接続で整理。",
        },
        valid_from="1601-01-01", valid_from_precision="century",
        valid_to="1830-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_agoston_2014,
    )
    facets_inserted.append(("timar", "governance", "ciftlik_erosion", f))

    # 5) 廃止: Mahmud II 改革
    f = add_facet(
        ORG["timar"], "governance",
        {
            "regime": "正式廃止 - Mahmud II の中央集権改革",
            "decision_locus": "スルタン Mahmud II 直轄、近代的常備軍 (Asakir-i Mansure) への置換",
            "notes": "1826 イェニチェリ廃止 (Vaka-i Hayriye) に続き、1831 にティマール制が"
                     "正式に廃止 (法令・実態とも)。土地収入は中央財政に編入。",
        },
        valid_from="1831-01-01", valid_from_precision="year",
        valid_to="1831-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_agoston_2014,
        note="制度終焉年。1831 廃止後の組織は存在しないため期間は短い記録的 facet。",
    )
    facets_inserted.append(("timar", "governance", "abolition_1831", f))

    # 6) legitimation_basis
    f = add_facet(
        ORG["timar"], "legitimation_basis",
        {
            "basis": "スルタン主権 (kanun + şeriat) - 全土地は名目上スルタン所有 (miri arazi)",
            "notes": "ティマール保有は所有権ではなく『収入分与』(prebend) として正当化される。"
                     "保有者は世襲ではなく原則一代限り、戦功・忠誠で再配分。"
                     "kanun (世俗法) と şeriat (宗教法) の二重正統性。",
        },
        valid_from="1362-01-01", valid_from_precision="year",
        valid_to="1831-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_inalcik_1973,
    )
    facets_inserted.append(("timar", "legitimation_basis", "sultanic", f))

    # =========================================================================
    # インカ帝国 (1438-1572): governance / territory / scale / resource_base / technology / legitimation_basis
    # =========================================================================

    # 1) Pachacuti 拡大開始
    f = add_facet(
        ORG["inca"], "territory",
        {
            "extent_label": "Cuzco 周辺の地方政体から拡大開始",
            "key_regions": ["Cuzco 盆地", "中央アンデス南部"],
            "notes": "Pachacuti (Cusi Yupanqui) が 1438 年頃 Chanca を撃破して即位、"
                     "Cuzco 周辺から拡大開始。それ以前はクスコ盆地の小政体。",
        },
        valid_from="1438-01-01", valid_from_precision="year",
        valid_to="1471-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_daltroy,
    )
    facets_inserted.append(("inca", "territory", "pachacuti_start", f))

    # 2) Topa Inka 全盛期: Tahuantinsuyu 完成
    f = add_facet(
        ORG["inca"], "territory",
        {
            "extent_label": "Tahuantinsuyu (四分国) 完成期 - 南北約 4,000 km",
            "key_regions": ["Chinchaysuyu (北西)", "Antisuyu (北東)",
                            "Cuntisuyu (南西)", "Collasuyu (南東)"],
            "approximate_extent_km": "南北約 4,000 km、現在のエクアドル南部から"
                                     "チリ中部 (Maule 川) まで",
            "notes": "Topa Inka Yupanqui (1471-93) と Huayna Capac (1493-1527) 期に"
                     "最大領域。D'Altroy (2014) は人口約 1,000-1,200 万と推定。",
        },
        valid_from="1471-01-01", valid_from_precision="year",
        valid_to="1527-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_daltroy,
    )
    facets_inserted.append(("inca", "territory", "tahuantinsuyu_peak", f))

    # 3) governance: decimal 行政体制
    f = add_facet(
        ORG["inca"], "governance",
        {
            "regime": "Sapa Inca 神権王 + decimal 行政階層",
            "decision_locus": "Sapa Inca (絶対君主) → Apu (suyu 知事) → curaca (地方首長) "
                              "の階層、decimal system (10/100/1,000/10,000 戸単位) で動員",
            "key_bodies": ["Sapa Inca", "Apukuna (4 suyu の知事)", "Curacas",
                           "khipukamayuq (khipu 記録官)"],
            "notes": "Rowe (1946) の古典的整理。書字なく khipu (結縄) と口頭伝承で"
                     "行政情報を管理。各 ayllu (親族共同体) を decimal 単位に編成。",
        },
        valid_from="1438-01-01", valid_from_precision="year",
        valid_to="1532-11-15",   valid_to_precision="exact",
        confidence=0.75, source_id=src_rowe_1946,
    )
    facets_inserted.append(("inca", "governance", "decimal_admin", f))

    # 4) resource_base: mit'a 労役制
    f = add_facet(
        ORG["inca"], "resource_base",
        {
            "primary": "mit'a (周期的労役制) による国家動員労働",
            "secondary": ["国家保有の terrace 農地 (state lands)",
                          "Inka/Sun の土地三分制 (community/Inka/Sun)",
                          "qollqa (国家倉庫) 備蓄"],
            "notes": "現金・市場経済を持たず、再分配経済。各 ayllu に労役義務 (mit'a) を課し、"
                     "農作業・建設 (道路・要塞)・軍役・鉱山労働を動員。"
                     "qollqa (倉庫) 網に余剰を貯蔵し再分配。",
        },
        valid_from="1438-01-01", valid_from_precision="year",
        valid_to="1532-11-15",   valid_to_precision="exact",
        confidence=0.85, source_id=src_daltroy,
    )
    facets_inserted.append(("inca", "resource_base", "mita_redistribution", f))

    # 5) technology
    f = add_facet(
        ORG["inca"], "technology",
        {
            "primary": "石造建築 (cyclopean masonry) + 青銅・銅冶金 + khipu 記録 + qhapaq ñan (王道)",
            "notes": "鉄器・車輪・畜力運搬・書字を持たないが、石造精密建築 (Sacsayhuamán, "
                     "Machu Picchu)、約 4 万 km の道路網 (qhapaq ñan)、khipu による"
                     "数値・行政記録、青銅器の高度な利用が技術基盤。"
                     "Rowe (1946) は 'Stone Age empire' と表現。",
        },
        valid_from="1438-01-01", valid_from_precision="year",
        valid_to="1532-11-15",   valid_to_precision="exact",
        confidence=0.85, source_id=src_rowe_1946,
        note="khipu の解読は現在も部分的、行政情報以外の用途は議論中。",
    )
    facets_inserted.append(("inca", "technology", "stone_age_empire", f))

    # 6) 内戦期 (1527-1532)
    f = add_facet(
        ORG["inca"], "governance",
        {
            "regime": "継承内戦 - Huascar vs Atahualpa",
            "decision_locus": "Cuzco の Huascar 派 vs Quito の Atahualpa 派の二分裂",
            "notes": "Huayna Capac の天然痘死 (1527 頃) 後、嫡子 Huascar (Cuzco) と"
                     "庶子 Atahualpa (Quito) の継承戦争。1532 春 Atahualpa 勝利、"
                     "Huascar 処刑。征服直前に統治構造が分裂状態。",
        },
        valid_from="1527-01-01", valid_from_precision="year",
        valid_to="1532-11-15",   valid_to_precision="exact",
        confidence=0.8, source_id=src_daltroy,
    )
    facets_inserted.append(("inca", "governance", "civil_war", f))

    # 7) 征服・残党 (Vilcabamba)
    f = add_facet(
        ORG["inca"], "territory",
        {
            "extent_label": "Pizarro 征服 → Vilcabamba 残党国家",
            "key_regions": ["Vilcabamba (peruvian Andes 東斜面、現 Cuzco 県北西部)"],
            "notes": "1532-11-16 Cajamarca で Pizarro が Atahualpa 捕縛、1533-07-26 処刑、"
                     "1533-11 Cuzco 占領。Manco Inca が 1537 年に Vilcabamba に逃亡し"
                     "残党国家を樹立。1572 Tupac Amaru I 処刑で完全終焉。",
        },
        valid_from="1532-11-16", valid_from_precision="exact",
        valid_to="1572-09-24",   valid_to_precision="exact",
        confidence=0.85, source_id=src_wiki_inca,
        note="征服日と Tupac Amaru I 処刑日 (1572-09-24) は確立した史実。",
    )
    facets_inserted.append(("inca", "territory", "conquest_vilcabamba", f))

    # =========================================================================
    # ムガル朝マンサブダール制 (1571-1858): governance / membership / scale / resource_base / legitimation_basis
    # =========================================================================

    # 1) Akbar 創設期
    f = add_facet(
        ORG["mansabdar"], "governance",
        {
            "regime": "マンサブダール制創設期 - 単一ランク制 (zat のみ)",
            "decision_locus": "皇帝 Akbar 直轄、貴族層 (umara) を mansab (序列) で組織化",
            "key_bodies": ["皇帝", "diwan (財務)", "bakhshi (軍事)", "mansabdar 各個"],
            "notes": "Akbar が 1571 年頃 (一説 1574-77 詔勅) に mansabdari を導入。"
                     "全帝国官僚・貴族・軍司令官を 10-10,000 の数値ランクで階層化。",
        },
        valid_from="1571-01-01", valid_from_precision="year",
        valid_to="1594-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_athar_ali,
        note="制度導入の正確な年次は史料により幅。Akbar 期 1570s が定説。",
    )
    facets_inserted.append(("mansabdar", "governance", "founding_akbar", f))

    # 2) zat/sawar 二重制確立
    f = add_facet(
        ORG["mansabdar"], "governance",
        {
            "regime": "zat (個人ランク) / sawar (騎兵動員ランク) 二重制 - 古典期",
            "decision_locus": "皇帝による mansab 個別下賜、二重ランクで地位と軍事義務を分離",
            "key_bodies": ["皇帝", "mir bakhshi (軍事監督)", "diwan-i ala (財務総督)"],
            "notes": "1595 年頃の改革で zat (個人地位) と sawar (実動員騎兵数) の"
                     "二重ランク制が確立。これにより貴族の見栄ランクと実軍事力を分離管理。"
                     "Athar Ali (1985) はこれをマンサブダール制の構造的核と位置づけ。",
        },
        valid_from="1595-01-01", valid_from_precision="year",
        valid_to="1657-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_athar_ali,
    )
    facets_inserted.append(("mansabdar", "governance", "zat_sawar_classical", f))

    # 3) scale: 古典期マンサブダール総数と上層構造
    f = add_facet(
        ORG["mansabdar"], "scale",
        {
            "metric": "mansabdar 総数",
            "value_range": "Akbar 末期 (1605) 約 1,800、Aurangzeb 期 (1690s) 約 14,500",
            "elite_count": "1,000 zat 以上の上級 mansabdar は古典期 100-200 人程度",
            "notes": "Athar Ali (1985) のデータ。Akbar 期から Aurangzeb 期にかけて"
                     "ランク保有者が約 8 倍に膨張、これが jagir 不足危機の構造的背景。"
                     "上層 (1000+ zat) の出自構成: イラン人約 28%、トゥラン人約 23%、"
                     "ラージプート約 15%、インド系ムスリム他。",
        },
        valid_from="1595-01-01", valid_from_precision="year",
        valid_to="1707-03-03",   valid_to_precision="exact",
        confidence=0.8, source_id=src_athar_ali,
    )
    facets_inserted.append(("mansabdar", "scale", "classical_count", f))

    # 4) resource_base: jagir 制
    f = add_facet(
        ORG["mansabdar"], "resource_base",
        {
            "primary": "jagir (給地) - 土地税収を mansabdar に割り当て",
            "secondary": ["khalisa (皇帝直轄領) からの中央財政"],
            "notes": "mansabdar は俸給ではなく特定地域の jagir (土地税収徴収権) を"
                     "割り当てられ、そこから自軍 (騎兵 sawar) の維持費と私的所得を確保。"
                     "jagir は原則一代限り・転封制で世襲を防ぐ設計。"
                     "オスマン・ティマール制と類似だがより流動的。",
        },
        valid_from="1571-01-01", valid_from_precision="year",
        valid_to="1707-03-03",   valid_to_precision="exact",
        confidence=0.85, source_id=src_habib_1999,
    )
    facets_inserted.append(("mansabdar", "resource_base", "jagir_classical", f))

    # 5) Aurangzeb 期 jagir 不足危機
    f = add_facet(
        ORG["mansabdar"], "governance",
        {
            "regime": "be-jagiri (jagir 不足) 危機 - 制度の構造的限界",
            "decision_locus": "皇帝 Aurangzeb 期、デカン征服による jagir 需要急増と供給不足",
            "notes": "Aurangzeb のデカン遠征 (1681-1707) で新規 mansabdar が増加する一方、"
                     "デカンは荒廃で実収入が公称ランク (jama) を大きく下回り、"
                     "jagir 待ちの mansabdar が増加 (be-jagiri)。"
                     "Habib (1999) が 'agrarian crisis' として帝国崩壊の構造要因と分析。",
        },
        valid_from="1681-01-01", valid_from_precision="year",
        valid_to="1707-03-03",   valid_to_precision="exact",
        confidence=0.8, source_id=src_habib_1999,
    )
    facets_inserted.append(("mansabdar", "governance", "be_jagiri_crisis", f))

    # 6) 後期帝国崩壊期: 地方ナワーブ自立化
    f = add_facet(
        ORG["mansabdar"], "governance",
        {
            "regime": "後期帝国崩壊期 - mansab 制の名目化、地方 nawab 自立化",
            "decision_locus": "Bengal/Awadh/Hyderabad 等の subadar が世襲化し独立的、"
                              "デリーの皇帝はマンサブを下賜するが実権なし",
            "notes": "1707 Aurangzeb 死後、Bengal Nawab (Murshid Quli Khan 1717-)、"
                     "Awadh Nawab (Saadat Ali Khan 1722-)、Hyderabad Nizam "
                     "(Asaf Jah I 1724-) 等が事実上の世襲君主化。"
                     "1739 Nadir Shah のデリー略奪、1761 第三次パーニーパットの戦いを経て"
                     "マラーター・東インド会社が実権を分有。",
        },
        valid_from="1707-03-04", valid_from_precision="exact",
        valid_to="1803-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_habib_1999,
    )
    facets_inserted.append(("mansabdar", "governance", "nawab_devolution", f))

    # 7) 完全廃止: 1858 East India Company による正式終焉
    f = add_facet(
        ORG["mansabdar"], "governance",
        {
            "regime": "完全廃止 - 英領インド成立",
            "decision_locus": "East India Company → British Crown (1858 Government of India Act)",
            "notes": "1857 セポイの反乱 (Indian Rebellion) で Bahadur Shah II が反乱側に"
                     "担がれ敗北、1858 流刑 (Rangoon)、ムガル朝公式終焉。"
                     "Government of India Act (1858) で Crown が直接統治、"
                     "mansabdari 制度は完全に消滅。",
        },
        valid_from="1858-08-02", valid_from_precision="exact",
        valid_to="1858-12-31",   valid_to_precision="year",
        confidence=0.9, source_id=src_habib_1999,
    )
    facets_inserted.append(("mansabdar", "governance", "abolition_1858", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ
    # =========================================================================
    print("=" * 70)
    print(f"投入 facet レコード数: {len(facets_inserted)}")
    print("=" * 70)
    print()

    # ケース別件数
    print("ケース別 facet 件数")
    print("-" * 70)
    for key, oid in ORG.items():
        n = cur.execute(
            "SELECT COUNT(*) FROM organization_temporal_facet WHERE organization_id=?",
            (oid,),
        ).fetchone()[0]
        name = cur.execute(
            "SELECT canonical_name FROM organization WHERE organization_id=?",
            (oid,),
        ).fetchone()[0]
        print(f"  {name}: {n} facets")
    print()

    # Q1. 1500 年時点のハンザ全 facet スナップショット
    print("Q1. 1500-01-01 時点のハンザ同盟スナップショット")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, facet_value, confidence, valid_from, valid_to
        FROM organization_temporal_facet
        WHERE organization_id = ?
          AND (valid_from IS NULL OR valid_from <= '1500-01-01')
          AND (valid_to   IS NULL OR valid_to   >  '1500-01-01')
        ORDER BY facet_type
        """,
        (ORG["hansa"],),
    ).fetchall()
    for ft, fv, conf, vf, vt in rows:
        v = json.loads(fv)
        summary = (v.get("regime") or v.get("basis") or v.get("primary")
                   or v.get("extent_label") or v.get("metric") or "—")
        print(f"  [{ft}] {vf} → {vt or 'open'} | conf={conf} | {summary[:60]}")
    print()

    # Q2. インカ帝国の territory 推移
    print("Q2. インカ帝国の territory 変遷")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'territory'
        ORDER BY valid_from
        """,
        (ORG["inca"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('extent_label')}")
    print()

    # Q3. マンサブダール制の governance 変遷
    print("Q3. マンサブダール制の governance 変遷")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'governance'
        ORDER BY valid_from
        """,
        (ORG["mansabdar"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('regime')}")
    print()

    # Q4. facet_type 分布 (投入 4 ケース)
    print("Q4. 4 ケースの facet_type 分布")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, COUNT(*) FROM organization_temporal_facet
        WHERE organization_id IN (?,?,?,?)
        GROUP BY facet_type ORDER BY 2 DESC
        """,
        tuple(ORG.values()),
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")
    print()

    # Q5. claim 整合性チェック
    print("Q5. claim 整合性 (4 ケース facet 全件に claim_id が紐付いているか)")
    print("-" * 70)
    n_total = cur.execute(
        "SELECT COUNT(*) FROM organization_temporal_facet "
        "WHERE organization_id IN (?,?,?,?)",
        tuple(ORG.values()),
    ).fetchone()[0]
    n_with_claim = cur.execute(
        "SELECT COUNT(*) FROM organization_temporal_facet f "
        "JOIN claim c ON c.claim_id = f.claim_id "
        "WHERE f.organization_id IN (?,?,?,?)",
        tuple(ORG.values()),
    ).fetchone()[0]
    print(f"  total facets: {n_total}, with valid claim: {n_with_claim}")

    conn.close()


if __name__ == "__main__":
    main()
