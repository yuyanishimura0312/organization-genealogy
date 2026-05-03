#!/usr/bin/env python3
"""Phase 4 先取りタスク #P: organization_temporal_facet 投入

目的:
  organization の静的属性 (start_date / end_date / status) では捉えられない
  長期的内部変容を facet スライスとして時系列で記録する。codex2 の
  OrganizationTemporalFacet を 5 ケースで初期投入し、temporal facet 設計の
  実用性を検証する。

対象組織 (organization_id 既存 verified 2026-05-02):
  - VOC                   9e99525267034e16af5863b9db8e63e6  (1602-1799)
  - 三井 (越後屋→グループ) bd370be2e24d4a54b92d914a111a81e6  (1673- )
  - ベネディクト会         2cf732ca2e44458b8d793880b59a1b5d  (529- )
  - MakerDAO              464be7e725f045afa3f2bd0750c04dbe  (2017- )
  - アシャンティ王国       fc9810d3d6e24955bfa3b97bb0c64641  (1670-1957)

facet_type 集合 (schema_sqlite_v05_temporal_facet.sql の CHECK と一致):
  membership / governance / resource_base / territory /
  technology / identity / scale / legitimation_basis

各 facet は claim 経由で出典あり。捏造禁止、不確実な日付・粒度は precision で表現。

設計方針:
  - 同一 organization × facet_type について複数スライスを許容
    (期間が連続的に分割されるケースもあれば、重なるケースもある)。
  - facet_value は JSON。型は facet_type に依存する柔軟スキーマ:
      governance      : {regime, decision_locus, key_bodies?, notes?}
      resource_base   : {primary, secondary?, financing?, notes?}
      territory       : {extent_label, key_regions?, area_km2_estimate?, notes?}
      identity        : {dominant_identity, brand_or_name?, notes?}
      scale           : {workforce?, ships?, capital?, tvl_usd?, area?, members?, notes?}
      technology      : {primary, notes?}
      membership      : {basis, eligibility?, notes?}
      legitimation_basis: {basis, notes?}
  - 確証性が低いものは confidence を下げ、note に明記。

検証クエリ (実行例) は最後に CLI で実行する。
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "voc":         "9e99525267034e16af5863b9db8e63e6",
    "mitsui":      "bd370be2e24d4a54b92d914a111a81e6",
    "benedictine": "2cf732ca2e44458b8d793880b59a1b5d",
    "makerdao":    "464be7e725f045afa3f2bd0750c04dbe",
    "asante":      "fc9810d3d6e24955bfa3b97bb0c64641",
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
                  recorded_by="claude_phase4_temporal_facet"):
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
        """facet を 1 件挿入。claim を facet 用に作り直して紐付ける。"""
        facet_id = uid()
        # facet ごとに claim を作る (entity_type='organization_temporal_facet')
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
    # SOURCES (実在文献。WebSearch を経た既知資料に揃える。捏造禁止)
    # =========================================================================
    src_voc_wiki = add_source(
        "web",
        "Wikipedia: Dutch East India Company (VOC) - history, charters, finance",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Dutch_East_India_Company"},
        accessed_at="2026-05-02",
        reliability_score=0.6,
        reliability_basis="百科事典。設立日 1602-03-20、解散 1799、Heeren XVII、"
                          "貿易品目 (香辛料→紅茶/コーヒー/織物) の概略は一般的事実。",
        redistribution="public_redistributable",
    )
    src_voc_gaastra = add_source(
        "secondary_literature",
        "Gaastra, F.S. (2003) The Dutch East India Company: Expansion and Decline",
        authors=["Femme S. Gaastra"],
        publication_date="2003",
        publisher="Walburg Pers",
        reliability_score=0.9,
        reliability_basis="VOC 経済史の標準書。Heeren XVII、Kamers、財政破綻、"
                          "18 世紀の借入依存への移行を扱う代表的二次文献。",
        bias_notes="蘭語圏の主流解釈、植民地搾取側の被害は背景的に扱われる傾向。",
        redistribution="attribution_required",
    )

    src_mitsui_history = add_source(
        "secondary_literature",
        "三井文庫 編『三井事業史』および公式社史 (越後屋→三井合名→三井財閥→三井グループ)",
        authors=["三井文庫"],
        publisher="三井文庫",
        reliability_score=0.85,
        reliability_basis="三井家公式の事業史編纂物。1673 越後屋創業、"
                          "1909 三井合名設立、1947 GHQ 財閥解体、戦後の系列(keiretsu)再編は"
                          "歴史的事実として確立。1904 三越分離も明記される。",
        bias_notes="三井側の自己記述、財閥批判は限定的。",
        redistribution="attribution_required",
    )
    src_mitsukoshi_wiki = add_source(
        "web",
        "Wikipedia: Mitsukoshi - separation from Mitsui Gomei (1904)",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Mitsukoshi"},
        accessed_at="2026-05-02",
        reliability_score=0.6,
        reliability_basis="百貨店事業 (越後屋→三越) の独立年次の概要記述。",
        redistribution="public_redistributable",
    )

    src_benedict_rule = add_source(
        "primary_text",
        "Regula Sancti Benedicti (Rule of St. Benedict)",
        authors=["Benedict of Nursia"],
        publication_date="0530",
        reliability_score=0.95,
        reliability_basis="一次史料。529 年頃の Monte Cassino 創設と修道規則の自治単位"
                          "(各修道院は abbot 統治下で自立) を定義する根本テキスト。",
        bias_notes="規範文書、運用との乖離は別史料で確認が必要。",
        redistribution="public_redistributable",
    )
    src_benedict_history = add_source(
        "secondary_literature",
        "Lawrence, C.H. (2015) Medieval Monasticism, 4th ed.",
        authors=["C.H. Lawrence"],
        publication_date="2015",
        publisher="Routledge",
        reliability_score=0.9,
        reliability_basis="中世修道制研究の代表的概論書。Cluny 連邦化 (10c-)、"
                          "後続の congregations、Reformation 期の離脱・縮小、"
                          "近現代の autonomy 復元の流れを記述。",
        redistribution="attribution_required",
    )
    src_osb_confederation = add_source(
        "web",
        "Benedictine Confederation (1893-) - official site of the Order",
        publisher="Confoederatio Benedictina",
        locator={"url": "https://www.osb.org/"},
        accessed_at="2026-05-02",
        reliability_score=0.7,
        reliability_basis="ベネディクト会連盟の公式紹介。1893 Leo XIII 教皇による"
                          "緩やかな連合体としての Confederation 設立を述べる。",
        redistribution="attribution_required",
    )

    src_makerdao_docs = add_source(
        "web",
        "MakerDAO official documentation - governance evolution: Foundation, "
        "Endgame Plan, SubDAOs",
        publisher="MakerDAO / Sky Ecosystem",
        locator={"url": "https://docs.makerdao.com/"},
        accessed_at="2026-05-02",
        reliability_score=0.7,
        reliability_basis="プロジェクト一次資料。Maker Foundation 設立 (2017-2018)、"
                          "2021 Foundation 解散と完全 DAO 化、2022 Rune Christensen "
                          "Endgame Plan、2024 Sky リブランドの記述。",
        bias_notes="プロジェクト自己記述、批判的視点は別途必要。",
        redistribution="attribution_required",
    )
    src_makerdao_wiki = add_source(
        "web",
        "Wikipedia: MakerDAO - Foundation dissolution, Endgame, governance",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/MakerDAO"},
        accessed_at="2026-05-02",
        reliability_score=0.6,
        reliability_basis="百科事典の整理記述。Foundation 解散 (2021-07)、"
                          "Endgame (2022-)、Sky リブランド (2024) を含む。",
        redistribution="public_redistributable",
    )
    src_defillama = add_source(
        "dataset",
        "DeFiLlama: MakerDAO TVL historical (2018-2026)",
        publisher="DeFiLlama",
        locator={"url": "https://defillama.com/protocol/makerdao"},
        accessed_at="2026-05-02",
        reliability_score=0.75,
        reliability_basis="チェーン上データ集計、TVL 推移は確認可能だが指標として複数定義あり。"
                          "ピーク値は 2021 末で約 USD 18B、2023 以降は数 B レンジで推移。",
        bias_notes="TVL 定義は時期で変動、Sky リブランド後は集計境界が変わる。",
        redistribution="attribution_required",
    )

    src_wilks = add_source(
        "secondary_literature",
        "Wilks, I. (1975) Asante in the Nineteenth Century",
        authors=["Ivor Wilks"],
        publication_date="1975",
        publisher="Cambridge University Press",
        reliability_score=0.95,
        reliability_basis="アシャンティ史の代表的標準書。Osei Tutu 即位 (c.1670s)、"
                          "Feyiase の戦い (1701) によるデンキラ (Denkyira) 撃破と"
                          "中央集権化、19c 拡張、英国との戦争。",
        redistribution="attribution_required",
    )
    src_asante_political = add_source(
        "web",
        "Wikipedia: Political systems of the Asante Empire",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/Political_systems_of_the_Asante_Empire"},
        accessed_at="2026-05-02",
        reliability_score=0.6,
        reliability_basis="アシャンティの統治構造、領域、Asantehene と Kotoko council "
                          "の概要記述。1896 英国保護領化、1957 ガーナ独立。",
        redistribution="public_redistributable",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # ---------- VOC ---------------------------------------------------------
    # scale: 1602 設立、1670 ピーク (船 200+, 従業員 5 万級)、
    #        1730 高水準維持、1799 解散
    f = add_facet(
        ORG["voc"], "scale",
        {
            "phase": "founding",
            "ships": "approx. 40-60 ships in early voyages",
            "capital_guilders": 6429588,
            "notes": "1602 設立時の認可資本 約 6.43 百万ギルダー (Heeren XVII 体制)。"
                     "Gaastra (2003) p.20 前後の整理。",
        },
        valid_from="1602-03-20", valid_from_precision="exact",
        valid_to="1670-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_voc_gaastra,
        note="設立時の認可資本は史料で確定。船舶数は航海年で大きく変動するため範囲表記。",
    )
    facets_inserted.append(("voc", "scale", "founding", f))

    f = add_facet(
        ORG["voc"], "scale",
        {
            "phase": "peak",
            "ships_in_service": "approx. 100-150",
            "employees_estimated": 25000,
            "notes": "17c 後半が VOC 雇用ピーク域。Gaastra (2003) は 17 世紀末の"
                     "European employees + Asian personnel を 2-3 万級と整理。",
        },
        valid_from="1670-01-01", valid_from_precision="decade",
        valid_to="1730-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_voc_gaastra,
        note="ピーク値は研究者により幅。ここでは Gaastra 概観の中央域を採用。",
    )
    facets_inserted.append(("voc", "scale", "peak", f))

    f = add_facet(
        ORG["voc"], "scale",
        {
            "phase": "decline_to_dissolution",
            "fiscal_state": "structural deficit, dependent on loans from Dutch state",
            "notes": "18c 後半は配当継続を借入で賄う構造。1796 国営化、1799 解散。",
        },
        valid_from="1730-01-01", valid_from_precision="decade",
        valid_to="1799-12-31",   valid_to_precision="exact",
        confidence=0.85, source_id=src_voc_gaastra,
    )
    facets_inserted.append(("voc", "scale", "decline", f))

    # resource_base: 香辛料 → 紅茶/コーヒー/織物 → 借入依存
    f = add_facet(
        ORG["voc"], "resource_base",
        {
            "primary": "spices (nutmeg, cloves, mace, pepper)",
            "key_regions": ["Banda Islands", "Maluku", "Java"],
            "notes": "17c 前半-中葉は東南アジア香辛料モノポリーが中核収益。"
                     "Banda Islands 1621 占領も背景。",
        },
        valid_from="1602-03-20", valid_from_precision="exact",
        valid_to="1680-12-31",   valid_to_precision="decade",
        confidence=0.85, source_id=src_voc_gaastra,
    )
    facets_inserted.append(("voc", "resource_base", "spices", f))

    f = add_facet(
        ORG["voc"], "resource_base",
        {
            "primary": "tea, coffee, textiles (cottons), porcelain",
            "secondary": ["spices (declining margin)"],
            "notes": "18c 入って香辛料の利益率が縮小、紅茶・コーヒー・インド綿布"
                     "への商品ポートフォリオ転換。Gaastra (2003) 第 4-5 章。",
        },
        valid_from="1680-01-01", valid_from_precision="decade",
        valid_to="1750-12-31",   valid_to_precision="decade",
        confidence=0.8, source_id=src_voc_gaastra,
    )
    facets_inserted.append(("voc", "resource_base", "tea_textiles", f))

    f = add_facet(
        ORG["voc"], "resource_base",
        {
            "primary": "borrowing (state and private creditors)",
            "secondary": ["intra-Asian trade", "residual commodity income"],
            "notes": "18c 後半は配当を借入で繋ぐ構造、財務破綻が解散の直接要因。",
        },
        valid_from="1750-01-01", valid_from_precision="decade",
        valid_to="1799-12-31",   valid_to_precision="exact",
        confidence=0.85, source_id=src_voc_gaastra,
    )
    facets_inserted.append(("voc", "resource_base", "borrowing", f))

    # ---------- 三井 --------------------------------------------------------
    # governance: 家業 → 合名 → 解体 → keiretsu
    f = add_facet(
        ORG["mitsui"], "governance",
        {
            "regime": "家業 (家族経営、大元方 Omotokata 統治)",
            "decision_locus": "三井家 11 家による Omotokata 合議",
            "key_bodies": ["大元方 (Omotokata)", "三井家家督"],
            "notes": "1673 越後屋呉服店創業、1710 大元方設立で 11 家共同統治。"
                     "明治期まで家業形態。",
        },
        valid_from="1673-05-01", valid_from_precision="exact",
        valid_to="1909-09-30",   valid_to_precision="year",
        confidence=0.85, source_id=src_mitsui_history,
    )
    facets_inserted.append(("mitsui", "governance", "kagyo", f))

    f = add_facet(
        ORG["mitsui"], "governance",
        {
            "regime": "合名会社 (Mitsui Gomei) → 財閥 (zaibatsu) 持株会社化",
            "decision_locus": "三井合名会社、後に三井本社を頂点とする持株支配",
            "notes": "1909 三井合名会社設立、1944 三井本社へ改組。zaibatsu 期。",
        },
        valid_from="1909-10-01", valid_from_precision="year",
        valid_to="1947-09-30",   valid_to_precision="year",
        confidence=0.85, source_id=src_mitsui_history,
    )
    facets_inserted.append(("mitsui", "governance", "zaibatsu", f))

    f = add_facet(
        ORG["mitsui"], "governance",
        {
            "regime": "財閥解体 (zaibatsu dissolution) - 統治体不在",
            "decision_locus": "GHQ 指令により持株会社解体、各事業会社が独立",
            "notes": "1947 持株会社整理委員会令により三井本社解体。",
        },
        valid_from="1945-09-01", valid_from_precision="year",
        valid_to="1953-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_mitsui_history,
    )
    facets_inserted.append(("mitsui", "governance", "dissolution", f))

    f = add_facet(
        ORG["mitsui"], "governance",
        {
            "regime": "keiretsu (企業集団) - 緩やかな相互持合と社長会",
            "decision_locus": "二木会 (Nimoku-kai 社長会) を媒介とした水平協調、"
                              "明示的頂点なし",
            "key_bodies": ["二木会", "三井グループ広報委員会", "中核各社"],
            "notes": "戦後 1950s に二木会形成、相互持合と取引慣行で結合する keiretsu。"
                     "持株会社頂点ではなく合議的水平形態。",
        },
        valid_from="1954-01-01", valid_from_precision="decade",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_mitsui_history,
    )
    facets_inserted.append(("mitsui", "governance", "keiretsu", f))

    # identity: 越後屋 → 三井 → 三越分離
    f = add_facet(
        ORG["mitsui"], "identity",
        {
            "dominant_identity": "呉服商 (Echigoya)",
            "brand_or_name": "越後屋",
            "notes": "創業時のアイデンティティは江戸の呉服商 越後屋。"
                     "現金掛け値なしの商法で知られる。",
        },
        valid_from="1673-05-01", valid_from_precision="exact",
        valid_to="1893-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_mitsui_history,
    )
    facets_inserted.append(("mitsui", "identity", "echigoya", f))

    f = add_facet(
        ORG["mitsui"], "identity",
        {
            "dominant_identity": "総合商社・銀行・鉱山を含む multi-sector zaibatsu / group",
            "brand_or_name": "三井 (Mitsui)",
            "notes": "三井銀行・三井物産・三井鉱山等を擁する複合資本としての"
                     "三井ブランドが中核アイデンティティに移行。",
        },
        valid_from="1876-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_mitsui_history,
        note="銀行 1876、物産 1876 設立で 'Mitsui' が傘ブランドとなる。"
             "Echigoya identity との並走期間あり。",
    )
    facets_inserted.append(("mitsui", "identity", "mitsui_group", f))

    f = add_facet(
        ORG["mitsui"], "identity",
        {
            "dominant_identity": "三越百貨店として呉服事業を分離独立",
            "brand_or_name": "三越 (Mitsukoshi) - 1904 分離",
            "notes": "1904 三井呉服店が三越呉服店として分離。本体 (商社・銀行・鉱山) と"
                     "別法人化。ここでは三井グループ側にとっての identity 縮減を記録。",
        },
        valid_from="1904-12-21", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_mitsukoshi_wiki,
        note="この facet は『三井グループからの三越分離』という変化を識別するもの。"
             "三越自体の系譜は別エンティティで扱うべき。",
    )
    facets_inserted.append(("mitsui", "identity", "mitsukoshi_split", f))

    # ---------- ベネディクト会 ---------------------------------------------
    f = add_facet(
        ORG["benedictine"], "governance",
        {
            "regime": "Monte Cassino 中心の単一修道院 + Regula 規範",
            "decision_locus": "abbot (修道院長) による各院自治、Regula が標準",
            "notes": "529 年頃 Monte Cassino 創設、Regula Sancti Benedicti が"
                     "修道院ごとの自治を定義。中央組織なし。",
        },
        valid_from="0529-01-01", valid_from_precision="year",
        valid_to="0909-12-31",   valid_to_precision="century",
        confidence=0.7, source_id=src_benedict_rule,
        note="期間境界 (~10c の Cluny 改革まで) は概念的、precision=century。",
    )
    facets_inserted.append(("benedictine", "governance", "monte_cassino", f))

    f = add_facet(
        ORG["benedictine"], "governance",
        {
            "regime": "Cluniac federation 期 - 連邦的修道院ネットワーク",
            "decision_locus": "Cluny 修道院長を頂点とする priorate ネットワーク、"
                              "後に他の congregations (Cistercian 等は分派)",
            "notes": "910 Cluny 創設後、Cluniac model が広域の連邦的統治を導入。"
                     "Cistercian (1098) は分派として分離 (本 facet ではベネディクト会"
                     "本体の連邦化期間として記録)。",
        },
        valid_from="0910-01-01", valid_from_precision="year",
        valid_to="1517-12-31",   valid_to_precision="century",
        confidence=0.65, source_id=src_benedict_history,
        note="ベネディクト会全体への適用は緩い。Cluniac は congregation の一種であり、"
             "全 OSB が連邦化したわけではない。期間境界は Reformation を目安。",
    )
    facets_inserted.append(("benedictine", "governance", "cluniac", f))

    f = add_facet(
        ORG["benedictine"], "governance",
        {
            "regime": "Reformation/世俗化による離脱・縮小",
            "decision_locus": "プロテスタント諸国・後にフランス革命期で多数の修道院解散、"
                              "残存院は地域 congregations 単位で自治",
            "notes": "16c Reformation でドイツ・北欧の OSB 修道院多数解散。"
                     "1789-1815 仏革命・ナポレオン期で大陸 OSB 大幅縮小。",
        },
        valid_from="1517-01-01", valid_from_precision="year",
        valid_to="1893-09-11",   valid_to_precision="exact",
        confidence=0.75, source_id=src_benedict_history,
    )
    facets_inserted.append(("benedictine", "governance", "reformation_secularization", f))

    f = add_facet(
        ORG["benedictine"], "governance",
        {
            "regime": "Benedictine Confederation - 緩やかな連合体下で各院自治",
            "decision_locus": "Abbot Primate (Sant'Anselmo, ローマ) は儀礼的・調整的、"
                              "実質的決定は各 congregation / 各修道院の abbot",
            "notes": "1893 Leo XIII の Summum Semper による Benedictine Confederation 設立。"
                     "中央集権ではなく『連合』であり、autonomous abbey の原則を維持。",
        },
        valid_from="1893-09-12", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_osb_confederation,
    )
    facets_inserted.append(("benedictine", "governance", "confederation", f))

    # ---------- MakerDAO ----------------------------------------------------
    f = add_facet(
        ORG["makerdao"], "governance",
        {
            "regime": "Maker Foundation period (developer-led)",
            "decision_locus": "Maker Foundation (Christensen ら) が開発・ガバナンス主導、"
                              "MKR 投票は併存するが実質意思決定は Foundation",
            "notes": "2017 Whitepaper, 2017-12 SAI, 2019-11 Multi-Collateral Dai 移行までは"
                     "Foundation 主導期。",
        },
        valid_from="2017-12-18", valid_from_precision="exact",
        valid_to="2021-07-19",   valid_to_precision="exact",
        confidence=0.8, source_id=src_makerdao_docs,
    )
    facets_inserted.append(("makerdao", "governance", "foundation", f))

    f = add_facet(
        ORG["makerdao"], "governance",
        {
            "regime": "Fully on-chain DAO governance",
            "decision_locus": "MKR holder vote (executive vote, governance poll) のみ。"
                              "Foundation 解散により正式な off-chain 主体は消滅。",
            "notes": "2021-07-20 Maker Foundation が MKR を返却、解散表明。"
                     "Core Units 体制に移行。",
        },
        valid_from="2021-07-20", valid_from_precision="exact",
        valid_to="2022-08-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_makerdao_wiki,
    )
    facets_inserted.append(("makerdao", "governance", "dao_only", f))

    f = add_facet(
        ORG["makerdao"], "governance",
        {
            "regime": "Endgame / SubDAO architecture (later rebranded Sky)",
            "decision_locus": "MakerDAO (後 Sky) を頂点とする SubDAO 階層、"
                              "AI tools とアルゴリズム的調整を組み込む実験的構造",
            "notes": "2022-08 Rune Christensen の Endgame Plan、2024-09 'Sky' へ"
                     "リブランド (USDS / SKY)、SubDAOs (Spark 等) 展開。",
        },
        valid_from="2022-09-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.7, source_id=src_makerdao_docs,
        note="Endgame は段階的展開中、最終形態は未確定。Sky リブランド後の正式な"
             "エンティティ境界は本 DB の MakerDAO ノードに継続帰属させる。",
    )
    facets_inserted.append(("makerdao", "governance", "endgame", f))

    # scale: TVL 推移
    f = add_facet(
        ORG["makerdao"], "scale",
        {
            "metric": "TVL_USD",
            "value_range": "approx. 0 - 0.5B",
            "notes": "2018-2020 立ち上げ期、TVL は数千万-数億 USD レンジ。",
        },
        valid_from="2017-12-18", valid_from_precision="exact",
        valid_to="2020-06-30",   valid_to_precision="year",
        confidence=0.7, source_id=src_defillama,
    )
    facets_inserted.append(("makerdao", "scale", "tvl_early", f))

    f = add_facet(
        ORG["makerdao"], "scale",
        {
            "metric": "TVL_USD",
            "value_range": "approx. 18B at peak (2021-11), 5-10B avg",
            "notes": "DeFi summer 後、2021-11 ピーク約 18B USD (DeFiLlama 集計)。"
                     "数値は集計タイミングと TVL 定義により幅。",
        },
        valid_from="2020-07-01", valid_from_precision="year",
        valid_to="2022-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_defillama,
    )
    facets_inserted.append(("makerdao", "scale", "tvl_peak", f))

    f = add_facet(
        ORG["makerdao"], "scale",
        {
            "metric": "TVL_USD",
            "value_range": "approx. 4-9B (Endgame / Sky era)",
            "notes": "Endgame 移行と Sky リブランド以降は 4-9B レンジを変動。"
                     "RWA・USDS 採用が再加速の試み。",
        },
        valid_from="2023-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.65, source_id=src_defillama,
        note="集計時点 (2026-05-02) のスナップショット。Sky リブランド後の境界に"
             "ついては本 DB では MakerDAO ノードに帰属させて記録。",
    )
    facets_inserted.append(("makerdao", "scale", "tvl_endgame", f))

    # ---------- アシャンティ -----------------------------------------------
    f = add_facet(
        ORG["asante"], "territory",
        {
            "extent_label": "Kumasi 周辺の中核 Asante 連合 (founding)",
            "key_regions": ["Kumasi", "Asante metropolitan area"],
            "notes": "1670s 頃 Osei Tutu 即位、Kumasi を中心に Asante 連合形成。"
                     "未だ Denkyira 宗主下の従属期間を含む。",
        },
        valid_from="1670-01-01", valid_from_precision="decade",
        valid_to="1700-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_wilks,
    )
    facets_inserted.append(("asante", "territory", "founding_kumasi", f))

    f = add_facet(
        ORG["asante"], "territory",
        {
            "extent_label": "Denkyira 撃破後の独立王国、中央 Akan 地域",
            "key_regions": ["Kumasi", "Denkyira 旧領", "中央 Akan forest zone"],
            "notes": "1701 Feyiase の戦いで Denkyira を破り独立、Asantehene の"
                     "中央集権王国確立。",
        },
        valid_from="1701-01-01", valid_from_precision="exact",
        valid_to="1820-12-31",   valid_to_precision="decade",
        confidence=0.85, source_id=src_wilks,
    )
    facets_inserted.append(("asante", "territory", "post_feyiase", f))

    f = add_facet(
        ORG["asante"], "territory",
        {
            "extent_label": "19c 拡張期: 北の savanna 諸国・南の沿岸方面まで版図最大",
            "key_regions": ["Asante metropolitan area", "Brong-Ahafo",
                            "Gonja・Dagbon (北部、tributary)",
                            "南部沿岸方面 (英国との抗争領域)"],
            "notes": "1820s 頃に版図最大、北部 savanna 諸国を tributary 化、"
                     "南部沿岸で英国・Fante 連合と衝突。",
        },
        valid_from="1820-01-01", valid_from_precision="decade",
        valid_to="1896-01-19",   valid_to_precision="exact",
        confidence=0.8, source_id=src_wilks,
    )
    facets_inserted.append(("asante", "territory", "19c_peak", f))

    f = add_facet(
        ORG["asante"], "territory",
        {
            "extent_label": "British protectorate / Asantehene 流刑期",
            "key_regions": ["Kumasi (英国保護領)"],
            "notes": "1896-01 英国による Kumasi 占領、Prempeh I 流刑、"
                     "1900 Yaa Asantewaa の戦い後 1902 正式併合。",
        },
        valid_from="1896-01-20", valid_from_precision="exact",
        valid_to="1957-03-05",   valid_to_precision="exact",
        confidence=0.85, source_id=src_asante_political,
    )
    facets_inserted.append(("asante", "territory", "british_protectorate", f))

    f = add_facet(
        ORG["asante"], "territory",
        {
            "extent_label": "ガーナ独立後の Ashanti Region (儀礼王権 + 行政区)",
            "key_regions": ["Ashanti Region of Ghana"],
            "notes": "1957-03-06 ガーナ独立、Asantehene は儀礼王権として継続、"
                     "領域は Ashanti Region として Ghana 行政に組み込まれる。",
        },
        valid_from="1957-03-06", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.85, source_id=src_asante_political,
        note="organization.status=transformed と整合。儀礼的 organization "
             "として残存。",
    )
    facets_inserted.append(("asante", "territory", "ghana_region", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ実行 (1700 年時点の VOC 状態スナップショット)
    # =========================================================================
    print("=" * 70)
    print(f"投入 facet レコード数: {len(facets_inserted)}")
    print("=" * 70)
    print()
    print("Q1. 1700-01-01 時点の VOC 全 facet スナップショット")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, facet_value, confidence, valid_from, valid_to
        FROM organization_temporal_facet
        WHERE organization_id = ?
          AND (valid_from IS NULL OR valid_from <= '1700-01-01')
          AND (valid_to   IS NULL OR valid_to   >  '1700-01-01')
        ORDER BY facet_type
        """,
        (ORG["voc"],),
    ).fetchall()
    for ft, fv, conf, vf, vt in rows:
        v = json.loads(fv)
        summary = v.get("phase") or v.get("primary") or v.get("regime") or v.get("metric") or "—"
        print(f"  [{ft}] {vf} → {vt or 'open'} | conf={conf} | {summary}")
    print()

    print("Q2. アシャンティの territory 推移")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ? AND facet_type = 'territory'
        ORDER BY valid_from
        """,
        (ORG["asante"],),
    ).fetchall()
    for vf, vt, fv in rows:
        v = json.loads(fv)
        print(f"  {vf} → {vt or 'open'} | {v.get('extent_label')}")
    print()

    print("Q3. governance 変化数 (組織別)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT o.canonical_name, COUNT(*) AS phases
        FROM organization_temporal_facet f
        JOIN organization o ON o.organization_id = f.organization_id
        WHERE f.facet_type = 'governance'
        GROUP BY o.canonical_name
        ORDER BY phases DESC
        """,
    ).fetchall()
    for name, n in rows:
        print(f"  {name}: {n} phases")
    print()

    # facet_type 別件数
    print("facet_type 分布")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, COUNT(*) FROM organization_temporal_facet
        GROUP BY facet_type ORDER BY 2 DESC
        """,
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")

    conn.close()


if __name__ == "__main__":
    main()
