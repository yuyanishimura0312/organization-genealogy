#!/usr/bin/env python3
"""Seed organization_form with key taxonomies:
- Mintzberg 7 configurations
- Hannan-Freeman organizational ecology niche types
- Laloux 5 paradigms
- Legal forms (JP / global)
- Historical/era forms (狩猟採集バンド ... DAO)
"""
import sqlite3
import uuid
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"


def uid():
    return uuid.uuid4().hex


# (taxonomy_name, form_code, label, definition, parent_code, valid_from, valid_to, notes)
FORMS = [
    # ----- Mintzberg 1979/1989 -----
    ("mintzberg_1989", "simple", "Simple Structure (Entrepreneurial)",
     "直接監督による調整、戦略的頂点が支配する小規模・若年組織", None, None, None,
     "起業家組織。創業期・小規模・単純環境向き"),
    ("mintzberg_1989", "machine_bureaucracy", "Machine Bureaucracy",
     "作業プロセスの標準化、テクノストラクチャが支配", None, None, None,
     "大規模・安定環境・反復作業 (大量生産工場、政府事務、銀行業務など)"),
    ("mintzberg_1989", "professional_bureaucracy", "Professional Bureaucracy",
     "スキルの標準化、業務核 (専門家) が支配", None, None, None,
     "大学、病院、会計事務所、法律事務所"),
    ("mintzberg_1989", "divisional", "Divisionalized Form",
     "アウトプットの標準化、中間ラインが支配", None, None, None,
     "M-form (GM, Du Pont 等)"),
    ("mintzberg_1989", "adhocracy", "Adhocracy / Innovative",
     "相互調整、支援スタッフが支配", None, None, None,
     "プロジェクト型・革新志向 (映画製作、研究機関、NASA など)"),
    ("mintzberg_1989", "missionary", "Missionary",
     "規範の標準化、イデオロギーが支配", None, None, None,
     "宗教団体、運動組織、社会的企業"),
    ("mintzberg_1989", "political", "Political",
     "支配的調整メカニズム不在、権力闘争が組織を動かす", None, None, None,
     "破綻間際の組織や移行期"),

    # ----- Hannan-Freeman -----
    ("hannan_freeman", "specialist_narrow", "Specialist (Narrow Niche)",
     "狭いニッチに特化した組織、特定環境で高効率", None, None, None,
     "ニッチ幅が狭い、環境変化に脆弱"),
    ("hannan_freeman", "generalist_broad", "Generalist (Broad Niche)",
     "広いニッチをカバー、複数環境で生存可能", None, None, None,
     "ニッチ幅が広い、変動環境に強い"),
    ("hannan_freeman", "polymorphous", "Polymorphous Generalist",
     "複数の専門部門を持つ generalist", None, None, None,
     "コングロマリット型"),

    # ----- Laloux 5 paradigms -----
    ("laloux_2014", "red", "Red — 衝動的",
     "首長制、恐怖支配、短期志向", None, None, None,
     "ストリートギャング、初期帝国"),
    ("laloux_2014", "amber", "Amber — 順応的",
     "ヒエラルキー、規則、長期計画", None, None, None,
     "教会、軍、政府機関"),
    ("laloux_2014", "orange", "Orange — 達成的",
     "業績主義、機械論、能力主義", None, None, None,
     "近代多国籍企業"),
    ("laloux_2014", "green", "Green — 多元的",
     "ステークホルダー型、価値駆動、エンパワーメント", None, None, None,
     "ベン&ジェリーズ、Patagonia 等"),
    ("laloux_2014", "teal", "Teal — 進化的",
     "自己経営、全体性、進化的目的", None, None, None,
     "Buurtzorg, Morning Star, FAVI"),

    # ----- Legal forms (グローバル) -----
    ("legal_form", "kk_jp", "株式会社 (KK)", "日本の株式会社", None, "1899-01-01", None, "商法・会社法に基づく"),
    ("legal_form", "godo_kaisha_jp", "合同会社 (GK)", "日本の合同会社", None, "2006-05-01", None, "LLC 相当"),
    ("legal_form", "ippan_shadan_jp", "一般社団法人", "日本の一般社団法人", None, "2008-12-01", None, None),
    ("legal_form", "npo_jp", "特定非営利活動法人 (NPO)", "日本の NPO 法人", None, "1998-12-01", None, "NPO 法に基づく"),
    ("legal_form", "c_corp_us", "C Corporation", "米国 C Corp", None, None, None, None),
    ("legal_form", "llc_us", "Limited Liability Company", "米国 LLC", None, "1977-01-01", None, "Wyoming 起源"),
    ("legal_form", "501c3_us", "501(c)(3) Nonprofit", "米国非営利公益法人", None, None, None, None),
    ("legal_form", "b_corp", "B Corporation", "B Lab 認証＋Benefit Corp 法人格", None, "2007-04-01", None, None),
    ("legal_form", "cooperative", "Cooperative", "協同組合", None, "1844-12-21", None, "Rochdale Pioneers が起源"),
    ("legal_form", "dao_llc_wyoming", "Wyoming DAO LLC", "ワイオミング州 DAO LLC", None, "2021-07-01", None, "世界初の DAO 専用法人格"),
    ("legal_form", "voc_charter", "Charter Company (VOC type)", "国家特許による独占貿易会社", None, "1602-03-20", "1799-12-31", "VOC, EIC 等"),
    ("legal_form", "guild", "Guild", "中世ギルド", None, "1100-01-01", "1791-06-14", "Le Chapelier 法でフランスで廃止"),
    ("legal_form", "monastic_order", "Monastic Order", "修道会", None, "529-01-01", None, "ベネディクト会以降"),
    ("legal_form", "waqf", "Waqf", "イスラームのワクフ", None, "650-01-01", None, "私有財産を公益用途に永久拘束"),

    # ----- Historical era forms -----
    ("historical_era", "hunter_gatherer_band", "狩猟採集バンド", "30-50人規模の平等主義集団", None, "-200000-01-01", None, "Boehm の逆転的支配階層、Dunbar 数 150"),
    ("historical_era", "tribe", "氏族・部族", "親族原理による集団", None, "-10000-01-01", None, "Sahlins 分節リネージ"),
    ("historical_era", "chiefdom", "首長制", "世襲的階層を持つ前国家組織", None, "-5000-01-01", None, "Service Primitive Social Organization"),
    ("historical_era", "temple_economy", "神殿経済", "余剰穀物の集中保管と配給を担う", None, "-3500-01-01", None, "ウルク Eanna 等"),
    ("historical_era", "ancient_bureaucracy", "古代官僚制", "書記階層を持つ専門組織", None, "-2500-01-01", None, "エジプト宰相、メソポタミア"),
    ("historical_era", "monastery", "修道院", "祈り・労働・知識継承の自給自足共同体", None, "529-01-01", None, "ベネディクト会、シトー会"),
    ("historical_era", "medieval_guild", "中世ギルド", "都市の職能組合", None, "1100-01-01", "1791-06-14", "ハンザ同盟、craft/merchant guilds"),
    ("historical_era", "charter_company", "特許貿易会社", "国家特許による独占＋公開株式", None, "1600-12-31", "1799-12-31", "VOC, EIC"),
    ("historical_era", "weberian_bureaucracy", "近代官僚制", "Weber 合理的・法的支配", None, "1850-01-01", None, "プロイセン、明治日本"),
    ("historical_era", "u_form", "産業企業 (U-form)", "職能別階層", None, "1850-01-01", None, "Pennsylvania 鉄道、Carnegie Steel"),
    ("historical_era", "m_form", "多事業部制 (M-form)", "プロフィットセンター + 中央本社", None, "1920-01-01", None, "GM Sloan, Du Pont"),
    ("historical_era", "zaibatsu", "財閥", "持株会社頂点の縦型ピラミッド", None, "1880-01-01", "1947-12-31", "三井三菱住友安田、GHQ で解体"),
    ("historical_era", "keiretsu", "系列", "横型相互持合企業集団", None, "1955-01-01", None, "戦後日本"),
    ("historical_era", "platform", "プラットフォーム", "多面市場マッチング", None, "2000-01-01", None, "Apple App Store, Uber"),
    ("historical_era", "dao", "DAO", "スマートコントラクトによる分散自律組織", None, "2016-04-30", None, "The DAO 起点"),

    # ----- East Asian-specific forms -----
    ("east_asian", "ie_household", "家 (Ie)", "血縁＋養子＋奉公人＋名跡＋家産の継続体", None, None, None, "中世から近世日本"),
    ("east_asian", "noren", "暖簾", "店名・信用・修業・分家を束ねる無形資産", None, None, None, "近世商家"),
    ("east_asian", "za", "座", "中世日本の同業組合", None, "1100-01-01", "1582-01-01", "織豊政権の楽市楽座で衰退"),
    ("east_asian", "kabu_nakama", "株仲間", "江戸期商人ギルド", None, "1721-01-01", "1841-12-31", "幕府公認"),
    ("east_asian", "tonya", "問屋", "流通・金融・情報の中間組織", None, "1700-01-01", None, "近世から近代へ"),
    ("east_asian", "zongzu", "宗族 (中国)", "父系親族組織、祠堂・族譜", None, "960-01-01", None, "宋代以降に制度化"),
    ("east_asian", "huiguan", "会館 (中国)", "同郷会・相互扶助", None, "1500-01-01", None, "明清の都市商業"),
    ("east_asian", "piaohao", "票号 (中国)", "山西商人の送金為替", None, "1820-01-01", "1920-12-31", "清代後期に発展"),
    ("east_asian", "munjung", "門中 (朝鮮)", "父系リネージ", None, None, None, "朝鮮王朝の儒教的親族秩序"),
]


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = 0
    for tax, code, label, definition, parent, vfrom, vto, notes in FORMS:
        # find parent by code if specified
        parent_id = None
        if parent:
            row = cur.execute(
                "SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
                (tax, parent),
            ).fetchone()
            if row:
                parent_id = row[0]
        try:
            cur.execute(
                """INSERT INTO organization_form
                   (form_id, taxonomy_name, form_code, label, parent_form_id,
                    definition, valid_period_from, valid_period_to, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uid(), tax, code, label, parent_id, definition, vfrom, vto, notes),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # already exists

    conn.commit()
    cur.execute("SELECT taxonomy_name, COUNT(*) FROM organization_form GROUP BY taxonomy_name ORDER BY 1")
    print(f"inserted: {inserted}")
    print("by taxonomy:")
    for tn, c in cur.fetchall():
        print(f"  {tn:20s} {c}")
    cur.execute("SELECT COUNT(*) FROM organization_form")
    print(f"total: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()
