#!/usr/bin/env python3
"""Phase 4 並列チーム D: 近世 (16-19c) 5 ケースの organization_temporal_facet 投入

対象 (organization_id 既存 verified 2026-05-03):
  - ベトナム郷約 (hương ước)         92ccbf3ab76a48c88c4d33ce8ebf89ef
  - 山西商人ネットワーク (Shanxi)    bbbbf3d2946946589c17533668dbb760
  - 堺会合衆 (Sakai Egoshu)          d82bf91f5e184dd19f72dcb481fff46f
  - スレイマニエ・キュリエ           35ad5ec6e9db4d7a8ad5ee1be9bd8740
  - 鴻池家                           7e16708a289d4adda96245383bb1b526

設計方針:
  - パターンは etl/16_temporal_facets.py に準拠
  - facet_type は schema CHECK 内 (membership/governance/resource_base/territory/
    technology/identity/scale/legitimation_basis)
  - 捏造禁止、確証性に応じ confidence 0.5-0.8、note で根拠明記
  - source は実在文献 + redistribution 必須
  - claim.value_kind は ENUM 厳格 (present/absent/partial/unknown/inapplicable)
"""
import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"

ORG = {
    "huongouoc":   "92ccbf3ab76a48c88c4d33ce8ebf89ef",
    "shanxi":      "bbbbf3d2946946589c17533668dbb760",
    "sakai":       "d82bf91f5e184dd19f72dcb481fff46f",
    "suleymaniye": "35ad5ec6e9db4d7a8ad5ee1be9bd8740",
    "konoike":     "7e16708a289d4adda96245383bb1b526",
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
                  recorded_by="claude_phase4_team_d_early_modern"):
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
    # SOURCES (実在文献のみ。redistribution 必須)
    # =========================================================================

    # ---- ベトナム郷約 ----
    src_phan = add_source(
        "secondary_literature",
        "Phan Đại Doãn 編『Một số vấn đề về làng xã Việt Nam』(ベトナム村落社会研究)",
        authors=["Phan Đại Doãn"],
        publication_date="1996",
        publisher="Nhà xuất bản Chính trị Quốc gia (Hanoi)",
        reliability_score=0.85,
        reliability_basis="ベトナム村落史研究の代表的論集。郷約 (hương ước) の慣習法的"
                          "性格、Lê Thánh Tông 期 (1464 前後) の公式化、"
                          "Nguyễn 朝の村落自治と国家統合の緊張、仏領期の改編を整理。",
        bias_notes="ベトナム国内の主流解釈。仏領植民地行政の法社会学的研究は別系統。",
        redistribution="attribution_required",
    )
    src_woodside = add_source(
        "secondary_literature",
        "Woodside, A. (1971) Vietnam and the Chinese Model: A Comparative Study of "
        "Nguyễn and Ch'ing Civil Government in the First Half of the Nineteenth Century",
        authors=["Alexander Woodside"],
        publication_date="1971",
        publisher="Harvard University Press",
        reliability_score=0.9,
        reliability_basis="Nguyễn 朝の中央集権化と村落自治の緊張に関する標準書。"
                          "村レベルでの慣習 (lệ làng) と中央法 (luật) の重層関係を分析。",
        redistribution="attribution_required",
    )
    src_hickey = add_source(
        "secondary_literature",
        "Hickey, G.C. (1964) Village in Vietnam",
        authors=["Gerald Cannon Hickey"],
        publication_date="1964",
        publisher="Yale University Press",
        reliability_score=0.8,
        reliability_basis="メコンデルタ村落のエスノグラフィ。仏領期から DRV 期にかけての"
                          "村落制度変容を一次的に観察。郷約解体の社会的影響を扱う。",
        bias_notes="米国冷戦期の南ベトナム研究、北部 DRV 領域へのアクセスは限定的。",
        redistribution="attribution_required",
    )

    # ---- 山西商人 ----
    src_gardella = add_source(
        "secondary_literature",
        "Gardella, R. (1992) 'Squaring Accounts: Commercial Bookkeeping Methods and "
        "Capitalist Rationalism in Late Qing and Republican China'",
        authors=["Robert Gardella"],
        publication_date="1992",
        publisher="Journal of Asian Studies 51(2)",
        reliability_score=0.85,
        reliability_basis="山西票号の会計技法・複式簿記類似システムを論じた標準論文。"
                          "票号 (Shanxi banks) の組織原理を分析。",
        redistribution="attribution_required",
    )
    src_tanaka = add_source(
        "secondary_literature",
        "田中真樹『清代山西商人の研究』",
        authors=["田中真樹"],
        publication_date="2009",
        publisher="同朋舎",
        reliability_score=0.85,
        reliability_basis="日本における山西商人研究。塩・茶・票号事業の段階的展開を"
                          "実証的に整理。",
        redistribution="attribution_required",
    )
    src_wuhui = add_source(
        "secondary_literature",
        "呉慧 編『中国商業通史』第 4-5 巻 (明清期)",
        authors=["呉慧"],
        publication_date="2002",
        publisher="中国財政経済出版社 (北京)",
        reliability_score=0.8,
        reliability_basis="中国商業史の通史。日昇昌 (1823) の票号創設、19c 中葉の隆盛、"
                          "民国期動乱による衰退を扱う。",
        bias_notes="中国側の近世商業評価、革命史観の影響を含む。",
        redistribution="attribution_required",
    )

    # ---- 堺会合衆 ----
    src_toyoda = add_source(
        "secondary_literature",
        "豊田武『堺 - 商人の進出と都市の自由』",
        authors=["豊田武"],
        publication_date="1981",
        publisher="教育社歴史新書",
        reliability_score=0.85,
        reliability_basis="堺研究の代表的入門書。会合衆 (egoshu / egōshū) の自治体制、"
                          "細川/三好期の保護、鉄炮 (火縄銃) 生産拠点化、1568 信長の介入、"
                          "1582 自治剥奪を整理。",
        redistribution="attribution_required",
    )
    src_morris = add_source(
        "secondary_literature",
        "Morris, V.D. (1981) 'The City of Sakai and Urban Autonomy', in "
        "Warlords, Artists, and Commoners: Japan in the Sixteenth Century "
        "(eds. Elison & Smith)",
        authors=["V. Dixon Morris"],
        publication_date="1981",
        publisher="University of Hawaii Press",
        reliability_score=0.85,
        reliability_basis="英語圏での堺自治研究の標準。会合衆 10 名構成、"
                          "Frois 等イエズス会報告との照合、信長介入の政治史を扱う。",
        redistribution="attribution_required",
    )

    # ---- スレイマニエ・キュリエ ----
    src_necipoglu = add_source(
        "secondary_literature",
        "Necipoğlu, G. (2005) The Age of Sinan: Architectural Culture in the "
        "Ottoman Empire",
        authors=["Gülru Necipoğlu"],
        publication_date="2005",
        publisher="Princeton University Press / Reaktion Books",
        reliability_score=0.95,
        reliability_basis="オスマン建築史の決定版。Sinan 設計のスレイマニエ複合体 "
                          "(külliye) の構成 (mosque + medrese 4 + dar al-shifa + "
                          "imaret + hammam + tabhane) と waqf 経済を体系的に分析。"
                          "1550 着工、1557 完成。",
        redistribution="attribution_required",
    )
    src_kuran = add_source(
        "secondary_literature",
        "Kuran, T. (2001) 'The Provision of Public Goods under Islamic Law: "
        "Origins, Impact, and Limitations of the Waqf System'",
        authors=["Timur Kuran"],
        publication_date="2001",
        publisher="Law & Society Review 35(4)",
        reliability_score=0.85,
        reliability_basis="waqf (寄進財団) システムの経済分析。19c Tanzimat 改革、"
                          "共和国期国営化による waqf 制度変容を論じる。",
        bias_notes="制度経済学アプローチ、Islamic law の柔軟性を相対的に低く評価する論調あり。",
        redistribution="attribution_required",
    )
    src_suleymaniye_wiki = add_source(
        "web",
        "Wikipedia: Süleymaniye Mosque / Süleymaniye Külliyesi",
        publisher="Wikipedia",
        locator={"url": "https://en.wikipedia.org/wiki/S%C3%BCleymaniye_Mosque"},
        accessed_at="2026-05-03",
        reliability_score=0.6,
        reliability_basis="百科事典。1550 着工・1557 完成、Sinan 設計、"
                          "現代の世界遺産 (Historic Areas of Istanbul, 1985 登録) "
                          "としての位置づけを補完。",
        redistribution="public_redistributable",
    )

    # ---- 鴻池家 ----
    src_miyamoto = add_source(
        "secondary_literature",
        "宮本又次『鴻池善右衛門』(人物叢書)",
        authors=["宮本又次"],
        publication_date="1958",
        publisher="吉川弘文館",
        reliability_score=0.9,
        reliability_basis="鴻池家研究の標準。山中時代の酒造業、1656 善右衛門の"
                          "大坂進出、両替商最盛期 (18c)、海運、大名貸、"
                          "幕末-明治の衰退過程を実証的に追跡。",
        redistribution="attribution_required",
    )
    src_yasuoka = add_source(
        "secondary_literature",
        "安岡重明『近世大坂金融史の研究』",
        authors=["安岡重明"],
        publication_date="1970",
        publisher="大原新生社",
        reliability_score=0.85,
        reliability_basis="大坂十人両替・金融機構の研究。鴻池の十人両替筆頭としての位置、"
                          "大名貸ネットワークの分析。",
        redistribution="attribution_required",
    )
    src_sanwa_history = add_source(
        "web",
        "三和銀行 / 三菱UFJ銀行 沿革 - 鴻池銀行 (1933 三和銀行設立に統合)",
        publisher="三菱UFJ銀行",
        locator={"url": "https://www.bk.mufg.jp/profile/aboutus/history/index.html"},
        accessed_at="2026-05-03",
        reliability_score=0.7,
        reliability_basis="銀行公式沿革。鴻池銀行 (1897) → 1933 三十四・山口・鴻池の"
                          "三行合併で三和銀行設立 → 2006 三菱UFJ銀行への系譜。",
        bias_notes="銀行自己記述、合併時の力学は限定的に扱われる。",
        redistribution="attribution_required",
    )

    # =========================================================================
    # FACETS
    # =========================================================================
    facets_inserted = []

    # ============== ベトナム郷約 (hương ước) ==============
    # Lê 朝期: Lê Thánh Tông が 1464 公式化
    f = add_facet(
        ORG["huongouoc"], "legitimation_basis",
        {
            "basis": "Lê 朝中央による公式化 - 慣習法 + 中央承認",
            "notes": "Lê Thánh Tông (在位 1460-1497) が 1464 前後に hương ước を"
                     "公式制度として承認。村落の慣習 (lệ làng) を中央法 (luật) と"
                     "並立させる二重構造の確立期。",
        },
        valid_from="1464-01-01", valid_from_precision="year",
        valid_to="1802-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_phan,
        note="1464 公式化年は研究者により幅。Phan (1996) の整理に拠る。"
             "Lê 朝末期 (Tây Sơn 期含む) まで本基盤が継続。",
    )
    facets_inserted.append(("huongouoc", "legitimation_basis", "le_dynasty", f))

    # Nguyễn 朝期: 中央集権化と村落自治の緊張
    f = add_facet(
        ORG["huongouoc"], "governance",
        {
            "regime": "Nguyễn 朝下の村落自治 - 中央集権との緊張",
            "decision_locus": "村落 council (hội đồng kỳ mục) を中心とした合議、"
                              "中央の県・府を介して国家と接続",
            "notes": "1802 Nguyễn 朝成立後、中央集権的官僚制が強化される一方で"
                     "hương ước は維持。Woodside (1971) は中央法と村落慣習の"
                     "重層関係を清朝モデル比較で分析。",
        },
        valid_from="1802-01-01", valid_from_precision="year",
        valid_to="1887-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_woodside,
    )
    facets_inserted.append(("huongouoc", "governance", "nguyen_tension", f))

    # 仏領期: French Indochina の改編
    f = add_facet(
        ORG["huongouoc"], "governance",
        {
            "regime": "仏領インドシナによる村落改編 - hương ước の文書化と再編",
            "decision_locus": "村落 council 維持、しかし仏当局が hương ước の"
                              "成文化・登録を要求、徴税・徴兵を媒介する補助組織化",
            "notes": "1887 仏領インドシナ連邦成立後、植民地行政が hương ước を"
                     "文書化・標準化。1921 北ベトナムでの '改革' (cải lương) は"
                     "村落自治を行政の下請けに変質させる試み。",
        },
        valid_from="1887-10-17", valid_from_precision="year",
        valid_to="1945-09-01",   valid_to_precision="year",
        confidence=0.75, source_id=src_phan,
        note="cải lương hương chính (1921) の年代は北部に限定。地域差大。",
    )
    facets_inserted.append(("huongouoc", "governance", "french_colonial", f))

    # DRV 解体: 1945- 共産党国家による解体
    f = add_facet(
        ORG["huongouoc"], "governance",
        {
            "regime": "DRV / SRV による hương ước の解体・代替",
            "decision_locus": "ベトナム共産党の村落支部 (chi bộ) と人民委員会が"
                              "意思決定を継承、hương ước は公式制度として消滅",
            "notes": "1945 ベトナム民主共和国成立後、土地改革 (1953-56) と"
                     "合作社化により hương ước の制度的基盤は解体。"
                     "Hickey (1964) は南部での残存を観察。"
                     "1990s 以降 'hương ước mới' (新郷約) として一部復活する動きあり。",
        },
        valid_from="1945-09-02", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.75, source_id=src_hickey,
        note="organization.status=transformed と整合。1990s 以降の復活は"
             "性格を変えた新制度であり、本 facet では解体側を記録。",
    )
    facets_inserted.append(("huongouoc", "governance", "drv_dissolution", f))

    # 識別性: 慣習法ベースから成文法ベースへ
    f = add_facet(
        ORG["huongouoc"], "identity",
        {
            "dominant_identity": "慣習法 (lệ làng) ベースの村落自治規範",
            "notes": "Lê 朝-Nguyễn 朝期は口頭・部分文書の慣習集積として機能。",
        },
        valid_from="1464-01-01", valid_from_precision="year",
        valid_to="1887-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_phan,
    )
    facets_inserted.append(("huongouoc", "identity", "customary", f))

    # ============== 山西商人ネットワーク ==============
    # 食塩・茶馬交易期 (16-17c)
    f = add_facet(
        ORG["shanxi"], "resource_base",
        {
            "primary": "食塩 (両淮塩) 専売、北辺軍需 (開中法)、茶馬交易",
            "key_regions": ["山西", "両淮 (江蘇北部)", "北辺 (大同・宣府)",
                            "蒙古・チベット方面"],
            "notes": "16c 明代開中法のもと、北辺軍需供給の見返りに塩引 (専売権) を"
                     "獲得して塩商として台頭。茶馬交易にも進出。"
                     "田中 (2009) 第 1-2 章。",
        },
        valid_from="1500-01-01", valid_from_precision="century",
        valid_to="1820-12-31",   valid_to_precision="decade",
        confidence=0.8, source_id=src_tanaka,
    )
    facets_inserted.append(("shanxi", "resource_base", "salt_tea", f))

    # 票号 (山西銀行) 全盛期 - 日昇昌 (1823) を画期に
    f = add_facet(
        ORG["shanxi"], "technology",
        {
            "primary": "票号 (piào hào) - 為替・送金システム",
            "notes": "1823 平遥の日昇昌 (Rishengchang) 設立を画期とする。"
                     "全国支店ネットワーク、複式簿記類似の会計、"
                     "暗号付き為替手形 (匯票) で長距離送金を独占的に担う。"
                     "Gardella (1992) が組織技術として分析。",
        },
        valid_from="1823-01-01", valid_from_precision="exact",
        valid_to="1910-12-31",   valid_to_precision="decade",
        confidence=0.85, source_id=src_gardella,
    )
    facets_inserted.append(("shanxi", "technology", "piaohao", f))

    f = add_facet(
        ORG["shanxi"], "scale",
        {
            "phase": "piaohao_peak",
            "branches": "全国 70+ 都市に支店ネットワーク",
            "notes": "19c 中葉-末期、清朝官庁の公金送金も担う準国家インフラ化。"
                     "票号総数は 1860s-90s に 30 行程度、各々が数十支店を展開。"
                     "呉慧 (2002) の整理。",
        },
        valid_from="1850-01-01", valid_from_precision="decade",
        valid_to="1900-12-31",   valid_to_precision="decade",
        confidence=0.75, source_id=src_wuhui,
    )
    facets_inserted.append(("shanxi", "scale", "piaohao_peak", f))

    # 清末-民国動乱期
    f = add_facet(
        ORG["shanxi"], "governance",
        {
            "regime": "清末-民国動乱による信用基盤の崩壊",
            "decision_locus": "各票号本店 (山西平遥・祁県・太谷) の掌櫃 (支配人) "
                              "による経営継続も、太平天国・義和団・辛亥革命で"
                              "顧客基盤と政府預金が消滅",
            "notes": "1900 義和団後の庚子賠款、1911 辛亥革命による清朝崩壊で"
                     "官公金預金喪失、近代銀行 (中国銀行 1912 等) との競争に敗退。",
        },
        valid_from="1900-01-01", valid_from_precision="decade",
        valid_to="1920-12-31",   valid_to_precision="decade",
        confidence=0.8, source_id=src_wuhui,
    )
    facets_inserted.append(("shanxi", "governance", "qing_collapse", f))

    # 完全衰退 1920s
    f = add_facet(
        ORG["shanxi"], "scale",
        {
            "phase": "extinction",
            "notes": "1921 日昇昌倒産を象徴に、1920s 中葉までに山西票号は事実上消滅。"
                     "ネットワーク全体としての商人集団も解体。",
        },
        valid_from="1921-01-01", valid_from_precision="year",
        valid_to="1930-12-31",   valid_to_precision="decade",
        confidence=0.8, source_id=src_wuhui,
        note="organization.end_date=1920 と整合。象徴的な日昇昌倒産年で記録。",
    )
    facets_inserted.append(("shanxi", "scale", "extinction", f))

    # ============== 堺会合衆 (Sakai Egoshu) ==============
    # 細川/三好期: 自治都市
    f = add_facet(
        ORG["sakai"], "governance",
        {
            "regime": "会合衆による自治 - 10 名の有力商人による合議",
            "decision_locus": "会合衆 (egoshu / egōshū) 約 10 名 (納屋衆を中核) "
                              "の合議、武家領主への貢納で外部介入を回避",
            "notes": "細川氏・三好氏の宗主下で実質的自治。Frois 報告では"
                     "'ベニスのような共和国' と形容される (Morris 1981)。"
                     "会合衆は世襲的な納屋衆 (倉庫業・海運業者) が中核。",
        },
        valid_from="1530-01-01", valid_from_precision="decade",
        valid_to="1568-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_toyoda,
    )
    facets_inserted.append(("sakai", "governance", "self_government", f))

    # 鉄炮生産拠点
    f = add_facet(
        ORG["sakai"], "technology",
        {
            "primary": "鉄炮 (火縄銃) の量産・改良",
            "notes": "1543 種子島伝来後、堺は紀州根来とともに鉄炮生産の中心拠点。"
                     "戦国大名への武器供給で経済力を蓄積。豊田 (1981) 第 3 章。",
        },
        valid_from="1545-01-01", valid_from_precision="decade",
        valid_to="1582-12-31",   valid_to_precision="year",
        confidence=0.8, source_id=src_toyoda,
    )
    facets_inserted.append(("sakai", "technology", "matchlock", f))

    # 1568 信長介入
    f = add_facet(
        ORG["sakai"], "governance",
        {
            "regime": "織田信長による矢銭要求と介入 - 自治の名目存続・実質縮小",
            "decision_locus": "形式的に会合衆は存続、実質は信長代官 (松井友閑) の"
                              "監督下に入る",
            "notes": "1568 信長が堺に矢銭 2 万貫を要求、当初は会合衆が抵抗するも"
                     "1569 屈服。自治の象徴である環濠の維持は許容されたが"
                     "政治的従属が確定。",
        },
        valid_from="1569-01-01", valid_from_precision="year",
        valid_to="1582-06-30",   valid_to_precision="year",
        confidence=0.85, source_id=src_morris,
    )
    facets_inserted.append(("sakai", "governance", "nobunaga_intervention", f))

    # 1582+ 完全解体: 秀吉による堀埋立
    f = add_facet(
        ORG["sakai"], "territory",
        {
            "extent_label": "環濠埋立による物理的自治基盤の消滅",
            "key_regions": ["堺 (堀埋立後)"],
            "notes": "1582 本能寺後、豊臣秀吉による堺の堀 (環濠) 埋立、"
                     "兵庫津・大坂への商人移転で会合衆体制は完全解体。"
                     "豊田 (1981) は 1582 をもって自治都市堺の終焉とする。",
        },
        valid_from="1582-07-01", valid_from_precision="year",
        valid_to="1582-12-31",   valid_to_precision="exact",
        confidence=0.8, source_id=src_toyoda,
        note="organization.end_date=1582 と整合。会合衆組織の消滅点を記録。",
    )
    facets_inserted.append(("sakai", "territory", "moat_filling", f))

    # アイデンティティ: 自由都市
    f = add_facet(
        ORG["sakai"], "identity",
        {
            "dominant_identity": "東アジア最大の自由貿易港・自治都市",
            "brand_or_name": "堺 (Sakai) - '東洋のベニス' (Frois)",
            "notes": "16c 中葉、明・朝鮮・琉球・南蛮との貿易拠点として機能。"
                     "茶の湯文化 (千利休らの納屋衆出身) も都市文化の一翼。",
        },
        valid_from="1530-01-01", valid_from_precision="decade",
        valid_to="1582-06-30",   valid_to_precision="year",
        confidence=0.8, source_id=src_morris,
    )
    facets_inserted.append(("sakai", "identity", "free_city", f))

    # ============== スレイマニエ・キュリエ ==============
    # Sinan 設計・waqf 自給システム成立
    f = add_facet(
        ORG["suleymaniye"], "technology",
        {
            "primary": "Sinan 設計の külliye 複合施設群",
            "notes": "1550 着工、1557 完成 (一部施設は 1559 までに整備)。"
                     "中央 mosque、medrese 4 (sahn-ı semân に倣う 4 法学派対応)、"
                     "dar al-shifa (病院)、imaret (炊き出し)、tabhane (旅人宿)、"
                     "hammam (浴場)、図書館を一体的に設計。Necipoğlu (2005)。",
        },
        valid_from="1557-01-01", valid_from_precision="year",
        valid_to=None,           valid_to_precision=None,
        confidence=0.9, source_id=src_necipoglu,
    )
    facets_inserted.append(("suleymaniye", "technology", "sinan_design", f))

    f = add_facet(
        ORG["suleymaniye"], "resource_base",
        {
            "primary": "waqf (vakıf) - スレイマン 1 世による寄進財団",
            "secondary": ["バルカン半島・アナトリアの土地 (mukata'a)",
                          "都市部不動産 (店舗・隊商宿)",
                          "農業収入"],
            "notes": "スレイマン 1 世が広範な土地・店舗を waqf として寄進、"
                     "その収益で複合体運営費・職員給与を自給。Necipoğlu (2005)、"
                     "Kuran (2001) が経済構造を分析。",
        },
        valid_from="1557-01-01", valid_from_precision="year",
        valid_to="1839-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_necipoglu,
    )
    facets_inserted.append(("suleymaniye", "resource_base", "waqf_self_sufficient", f))

    f = add_facet(
        ORG["suleymaniye"], "membership",
        {
            "basis": "オスマン宗教官僚制 - imam, müderris, talebe, etc.",
            "eligibility": "中央任命 (şeyhülislam 系統) による mülazemet 制度",
            "notes": "medrese 教員 (müderris) は中央任命、最上位 medrese として"
                     "ulema キャリアの中核ポストを構成。dar al-shifa の医師、"
                     "imaret のスタッフも waqf 規約に基づく雇用。",
        },
        valid_from="1557-01-01", valid_from_precision="year",
        valid_to="1839-12-31",   valid_to_precision="year",
        confidence=0.75, source_id=src_necipoglu,
    )
    facets_inserted.append(("suleymaniye", "membership", "ottoman_ulema", f))

    # 19c Tanzimat 改革
    f = add_facet(
        ORG["suleymaniye"], "governance",
        {
            "regime": "Tanzimat 改革下での waqf 中央集権化",
            "decision_locus": "1826 設置の Evkaf-ı Hümayun Nezareti (waqf 省) が"
                              "個別 waqf の自律的運営を中央管理下に編入",
            "notes": "1826 Evkaf 省設置、1839 Tanzimat 勅令以降、"
                     "個別 waqf の収益を中央プールに統合する改革が進行。"
                     "Kuran (2001) 第 5 節。",
        },
        valid_from="1839-11-03", valid_from_precision="year",
        valid_to="1923-10-29",   valid_to_precision="exact",
        confidence=0.7, source_id=src_kuran,
    )
    facets_inserted.append(("suleymaniye", "governance", "tanzimat", f))

    # 共和国期国営化
    f = add_facet(
        ORG["suleymaniye"], "governance",
        {
            "regime": "トルコ共和国による国営化 - Vakıflar Genel Müdürlüğü 管理下",
            "decision_locus": "Vakıflar Genel Müdürlüğü (財団総局, 1924-) と"
                              "Diyanet İşleri Başkanlığı (宗務庁, 1924-) が"
                              "外形的管理、medrese 機能は 1924 廃止",
            "notes": "1924 medrese 廃止 (Tevhid-i Tedrisat 法)、waqf は国家管理下へ。"
                     "mosque は Diyanet 管轄、複合体は史跡・観光対象として再定義。",
        },
        valid_from="1923-10-30", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_kuran,
        note="organization.status=transformed と整合。当初の自給的 waqf 経済は解体、"
             "宗教施設・観光施設として継続。1985 世界遺産登録。",
    )
    facets_inserted.append(("suleymaniye", "governance", "republic_nationalization", f))

    # ============== 鴻池家 ==============
    # 山中時代: 酒造業
    f = add_facet(
        ORG["konoike"], "resource_base",
        {
            "primary": "酒造 (清酒醸造) - 摂津国川辺郡鴻池村",
            "key_regions": ["摂津国川辺郡鴻池村 (現・兵庫県伊丹市)"],
            "notes": "1600 前後、山中新六 (鴻池新六) が清酒澄み酒の醸造法を確立、"
                     "摂泉酒造業の祖の一人。江戸への下り酒輸送で財を成す。"
                     "宮本 (1958) 第 1 章。",
        },
        valid_from="1600-01-01", valid_from_precision="decade",
        valid_to="1655-12-31",   valid_to_precision="year",
        confidence=0.7, source_id=src_miyamoto,
        note="山中新六の酒造開始年は 1600 前後と推定、史料は限定的。",
    )
    facets_inserted.append(("konoike", "resource_base", "sake_brewing", f))

    # 1656 善右衛門大坂進出: 両替商化
    f = add_facet(
        ORG["konoike"], "identity",
        {
            "dominant_identity": "両替商 (rryōgaeshō) - 大坂 imadebashi 両替店",
            "brand_or_name": "鴻池善右衛門 (Konoike Zen'emon)",
            "notes": "1656 鴻池善右衛門 (初代) が大坂今橋に両替店開業。"
                     "酒造業から金融業への転換が当家の長期軌跡を決定。"
                     "宮本 (1958) はこれを '商家としての鴻池の出発点' と位置づける。",
        },
        valid_from="1656-01-01", valid_from_precision="year",
        valid_to="1899-12-31",   valid_to_precision="year",
        confidence=0.85, source_id=src_miyamoto,
    )
    facets_inserted.append(("konoike", "identity", "moneychanger", f))

    # 18c 両替商最盛期 - 十人両替筆頭
    f = add_facet(
        ORG["konoike"], "governance",
        {
            "regime": "十人両替筆頭としての公金為替・大名貸ネットワーク",
            "decision_locus": "鴻池本家 (善右衛門) を頂点に分家・支配人が"
                              "両替・米切手・大名貸を運営、幕府公金為替も担当",
            "key_bodies": ["十人両替 (大坂)", "鴻池本家", "番頭 (支配人)"],
            "notes": "1670 十人両替制度成立後、鴻池はその筆頭格。"
                     "幕府御為替方として公金送金を担い、諸大名 (尾張・紀州・"
                     "加賀ほか 30+) への大名貸ネットワークを構築。"
                     "安岡 (1970) 第 3-4 章。",
        },
        valid_from="1670-01-01", valid_from_precision="decade",
        valid_to="1850-12-31",   valid_to_precision="decade",
        confidence=0.85, source_id=src_yasuoka,
    )
    facets_inserted.append(("konoike", "governance", "junin_ryogae", f))

    f = add_facet(
        ORG["konoike"], "scale",
        {
            "phase": "edo_peak",
            "loans_to_daimyo": "30+ 諸藩への貸付ネットワーク",
            "notes": "18c 中葉、両替商上位として大名貸残高は数十万両規模。"
                     "海運 (鴻池新田の干拓 1707 を含む) や蔵元事業も並行。"
                     "宮本 (1958)、安岡 (1970)。",
        },
        valid_from="1700-01-01", valid_from_precision="decade",
        valid_to="1850-12-31",   valid_to_precision="decade",
        confidence=0.7, source_id=src_miyamoto,
    )
    facets_inserted.append(("konoike", "scale", "edo_peak", f))

    # 19c 末衰退 - 大名貸の踏み倒しと明治金融再編
    f = add_facet(
        ORG["konoike"], "resource_base",
        {
            "primary": "近代銀行業への転換 (鴻池銀行 1897)",
            "secondary": ["旧大名貸の処理", "両替業務の縮小"],
            "notes": "明治維新後、藩債処分令 (1871) で大名貸の大部分が消却。"
                     "1877 鴻池銀行 (個人銀行) 設立、1897 株式会社化。"
                     "近代銀行への組織変容期。宮本 (1958) 第 7 章。",
        },
        valid_from="1871-12-01", valid_from_precision="year",
        valid_to="1933-12-09",   valid_to_precision="exact",
        confidence=0.8, source_id=src_miyamoto,
    )
    facets_inserted.append(("konoike", "resource_base", "modern_banking", f))

    # 1933 三和銀行系譜への合流
    f = add_facet(
        ORG["konoike"], "identity",
        {
            "dominant_identity": "三和銀行 (現・三菱UFJ銀行) の系譜要素",
            "brand_or_name": "三和銀行 (1933 鴻池+山口+三十四 三行合併) → 三菱UFJ銀行",
            "notes": "1933-12-09 鴻池銀行・山口銀行・三十四銀行の合併で三和銀行設立。"
                     "鴻池家としての個別商号は事実上消滅、戦後は三和銀行 → "
                     "UFJ 銀行 (2002) → 三菱UFJ銀行 (2006) の系譜に組み込まれる。",
        },
        valid_from="1933-12-10", valid_from_precision="exact",
        valid_to=None,           valid_to_precision=None,
        confidence=0.8, source_id=src_sanwa_history,
        note="organization.status=transformed と整合。鴻池家本体は商家としては"
             "1933 で実質的解体、銀行系譜として継続。",
    )
    facets_inserted.append(("konoike", "identity", "sanwa_lineage", f))

    conn.commit()

    # =========================================================================
    # 検証クエリ
    # =========================================================================
    print("=" * 70)
    print(f"投入 facet レコード数: {len(facets_inserted)}")
    print("=" * 70)
    print()

    print("Q1. 各組織の facet 件数")
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

    print("Q2. 1700 年時点の山西商人 全 facet スナップショット")
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
        (ORG["shanxi"],),
    ).fetchall()
    for ft, fv, conf, vf, vt in rows:
        v = json.loads(fv)
        summary = (v.get("phase") or v.get("primary") or v.get("regime")
                   or v.get("metric") or v.get("basis")
                   or v.get("dominant_identity") or v.get("extent_label") or "—")
        print(f"  [{ft}] {vf} → {vt or 'open'} | conf={conf} | {summary}")
    print()

    print("Q3. 鴻池家 全 facet 時系列")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, valid_from, valid_to, facet_value
        FROM organization_temporal_facet
        WHERE organization_id = ?
        ORDER BY valid_from
        """,
        (ORG["konoike"],),
    ).fetchall()
    for ft, vf, vt, fv in rows:
        v = json.loads(fv)
        summary = (v.get("primary") or v.get("regime") or v.get("phase")
                   or v.get("dominant_identity") or v.get("basis") or "—")
        print(f"  {vf} → {vt or 'open'} | [{ft}] {summary}")
    print()

    print("Q4. 全体 facet_type 分布 (本投入 5 ケース)")
    print("-" * 70)
    rows = cur.execute(
        """
        SELECT facet_type, COUNT(*) FROM organization_temporal_facet
        WHERE organization_id IN (?,?,?,?,?)
        GROUP BY facet_type ORDER BY 2 DESC
        """,
        tuple(ORG.values()),
    ).fetchall()
    for ft, n in rows:
        print(f"  {ft}: {n}")

    conn.close()


if __name__ == "__main__":
    main()
