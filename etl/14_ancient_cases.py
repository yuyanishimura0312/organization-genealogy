#!/usr/bin/env python3
"""Phase 4 古代カバレッジ拡大 — 5 ケース完全注釈

ターゲット (BC500 以前を含む古代に厚みを足す):
  1. ウルク Eanna 神殿 (BC3500–BC2900) — 神殿経済、楔形文字会計の発祥地
  2. エジプト第18王朝の宰相 (djati / vizier) (BC1550–BC1295) — 古代官僚制の頂点
  3. ローマ legio (Marian reform 後, BC107–AD476) — 国家常備軍と職業軍人制
  4. ローマ collegia (BC50–AD476) — 職業組合・互助結社の鋳型
  5. Spartan agoge (BC700–BC371) — 国家による系統的人材成形プログラム

BC 日付方針:
  - SQLite の start_date は TEXT で AD のゼロ埋め 4 桁 ("0529-01-01") を採用してきた。
  - BC は ISO 8601 拡張形式の負年だと parse_year (date_str[:4]) で破綻するため、
    start_date=NULL / start_date_precision='period' とし、BC 開始年は
    attributes.bc_start_year_int / .bc_end_year_int (負整数) と
    attributes.period_label ("BC3500-BC2900" 等) に格納する。
  - SVG 09 は parse_year が None を返した場合のフォールバックを持つので破綻しない。
  - 将来 temporal_facet テーブルで signed-year を表現する際は migration で吸い上げる。

文献:
  - Pollock, S. (1999) Ancient Mesopotamia: The Eden That Never Was, Cambridge UP.
  - Bottéro, J. (1992) Mesopotamia: Writing, Reasoning, and the Gods, U. of Chicago.
  - Nissen / Damerow / Englund (1993) Archaic Bookkeeping, U. of Chicago.
  - van den Boorn, G.P.F. (1988) The Duties of the Vizier, Kegan Paul.
  - Erdkamp, P. (ed.) (2007) A Companion to the Roman Army, Blackwell.
  - Liu, J. (2009) Collegia Centonariorum: The Guilds of Textile Dealers, Brill.
  - Kennell, N.M. (1995) The Gymnasium of Virtue: Education and Culture in Ancient
    Sparta, U. of North Carolina Press.

各ケースで activity / function / impact / event / form_assignment / 既存ケースとの
relation (legio→中世ギルド・近代軍隊、エジプト宰相→マンサブダール、Eanna→ベネディクト会
の修道院経済、collegia→ハンザ同盟・guild、agoge→ベネディクト会のフォーメーション)
を投入する。捏造禁止: 確証のない継承主張は confidence <=0.55、
value_kind='partial' / 'unknown' とし、interpretation_note で理由を明記。
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"


def uid() -> str:
    return uuid.uuid4().hex


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    inserted: list[tuple[str, str, str]] = []

    # ----- helpers (04_representative_cases.py と同形) -----
    def get_form_id(taxonomy: str, code: str) -> str | None:
        row = cur.execute(
            "SELECT form_id FROM organization_form WHERE taxonomy_name=? AND form_code=?",
            (taxonomy, code),
        ).fetchone()
        return row[0] if row else None

    def get_org_id(name_like: str) -> str | None:
        row = cur.execute(
            "SELECT organization_id FROM organization WHERE canonical_name LIKE ? LIMIT 1",
            (name_like,),
        ).fetchone()
        return row[0] if row else None

    def add_source(stype: str, title: str, **kw) -> str:
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
             kw.get("redistribution", "attribution_required")),
        )
        return sid

    def add_claim(entity_type, entity_id, field_path, value_kind, claim_value,
                  source_id, confidence, recorded_by="claude_code_v1", note=None) -> str:
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

    def add_org(canonical_name: str, **kw) -> str:
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
             json.dumps(kw.get("external_ids"), ensure_ascii=False) if kw.get("external_ids") else None),
        )
        return oid

    def assign_form(org_id, taxonomy, code, *, is_primary=False, valid_from=None,
                    valid_to=None, confidence=0.8, claim_id=None) -> str | None:
        fid = get_form_id(taxonomy, code)
        if not fid:
            print(f"  [warn] form not found: {taxonomy}.{code}")
            return None
        aid = uid()
        cur.execute(
            """INSERT INTO organization_form_assignment
                (assignment_id, organization_id, form_id, valid_from, valid_to,
                 is_primary, confidence, claim_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (aid, org_id, fid, valid_from, valid_to,
             1 if is_primary else 0, confidence, claim_id),
        )
        if is_primary:
            cur.execute(
                "UPDATE organization SET primary_form_id=? WHERE organization_id=?",
                (fid, org_id),
            )
        return aid

    def add_activity(org_id, atype, **kw) -> str:
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
             kw.get("confidence"), kw.get("claim_id")),
        )
        return aid

    def add_function(org_id, func_type_id, mechanism=None, activity_id=None,
                     valid_from=None, valid_to=None, confidence=None, claim_id=None) -> str:
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

    def add_impact(org_id, domain, metric_name, metric_value, direction, time_horizon,
                   evaluation_method=None, valid_from=None, valid_to=None,
                   confidence=None, claim_id=None, affected_scope=None) -> str:
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

    def add_relation(src, tgt, rtype, **kw) -> str:
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

    def add_event(etype, **kw) -> str:
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

    def link_event_org(event_id, org_id, role) -> None:
        cur.execute(
            """INSERT OR IGNORE INTO event_organization
                (event_organization_id, event_id, organization_id, role)
               VALUES (?,?,?,?)""",
            (uid(), event_id, org_id, role),
        )

    # ============================================================
    # Sources
    # ============================================================
    src_pollock = add_source("secondary_literature",
        "Pollock, S. (1999) Ancient Mesopotamia: The Eden That Never Was",
        authors=["Susan Pollock"], publication_date="1999-01-01",
        publisher="Cambridge University Press",
        reliability_score=0.9,
        reliability_basis="メソポタミア考古学の標準的学術書、複数の発掘成果に基づく",
        redistribution="restricted")

    src_bottero = add_source("secondary_literature",
        "Bottéro, J. (1992) Mesopotamia: Writing, Reasoning, and the Gods",
        authors=["Jean Bottéro"], publication_date="1992-01-01",
        publisher="University of Chicago Press",
        reliability_score=0.9,
        reliability_basis="アッシリア学の権威による標準的解釈",
        redistribution="restricted")

    src_nissen_1993 = add_source("secondary_literature",
        "Nissen, H.J., Damerow, P., Englund, R.K. (1993) Archaic Bookkeeping",
        authors=["Hans Nissen", "Peter Damerow", "Robert Englund"],
        publication_date="1993-01-01",
        publisher="University of Chicago Press",
        reliability_score=0.95,
        reliability_basis="ウルク古拙文字粘土板の一次解読、原版図版を含む",
        redistribution="restricted")

    src_van_den_boorn = add_source("secondary_literature",
        "van den Boorn, G.P.F. (1988) The Duties of the Vizier",
        authors=["G.P.F. van den Boorn"], publication_date="1988-01-01",
        publisher="Kegan Paul International",
        reliability_score=0.9,
        reliability_basis="Rekhmire 墓碑文 (TT100) の宰相職務テキスト一次校訂",
        redistribution="restricted")

    src_erdkamp = add_source("secondary_literature",
        "Erdkamp, P. (ed.) (2007) A Companion to the Roman Army",
        authors=["Paul Erdkamp"], publication_date="2007-01-01",
        publisher="Blackwell",
        reliability_score=0.9,
        reliability_basis="ローマ軍研究の総説、複数執筆者による査読書",
        redistribution="restricted")

    src_liu_collegia = add_source("secondary_literature",
        "Liu, J. (2009) Collegia Centonariorum: The Guilds of Textile Dealers in the Roman West",
        authors=["Jinyu Liu"], publication_date="2009-01-01",
        publisher="Brill",
        reliability_score=0.9,
        reliability_basis="Centonarii 碑文一次史料に基づくモノグラフ、collegia 制度史の標準",
        redistribution="restricted")

    src_kennell = add_source("secondary_literature",
        "Kennell, N.M. (1995) The Gymnasium of Virtue: Education and Culture in Ancient Sparta",
        authors=["Nigel M. Kennell"], publication_date="1995-01-01",
        publisher="University of North Carolina Press",
        reliability_score=0.85,
        reliability_basis="agoge の起源と再構築 (Roman 期の Spartan ミラージュを批判的に分離)",
        redistribution="restricted")

    src_finer = add_source("secondary_literature",
        "Finer, S.E. (1997) The History of Government from the Earliest Times, Vol. I",
        authors=["Samuel E. Finer"], publication_date="1997-01-01",
        publisher="Oxford University Press",
        reliability_score=0.85,
        reliability_basis="比較統治史の古典、官僚制比較で言及多数",
        redistribution="restricted")

    src_diodorus = add_source("primary_text",
        "Diodorus Siculus, Bibliotheca Historica (Loeb edition)",
        authors=["Diodorus Siculus"], publication_date=None,
        publisher="Loeb Classical Library",
        reliability_score=0.6,
        reliability_basis="一次史料 (BC1 世紀著述) だが Spartan 制度については後代の理想化を含む",
        redistribution="public_redistributable",
        locator={"original_composition": "circa BC30", "edition": "Loeb Classical Library"})

    # ============================================================
    # CASE 1: ウルク Eanna 神殿 (BC3500-BC2900)
    # ============================================================
    eanna = add_org(
        canonical_name="ウルク Eanna 神殿 (Eanna Temple of Uruk)",
        alternate_names=[
            {"name": "Eanna", "lang": "akk"},
            {"name": "𒂍𒀭", "lang": "sux"},
            {"name": "House of Heaven (Inanna's temple)", "lang": "en"},
        ],
        description="ウルク (現イラク Warka) の女神イナンナ/アヌに捧げられた神殿複合体。後期ウルク期 (Uruk IV–III, BC3500–BC2900 頃) に楔形文字の前身である数値・物品トークンと粘土板会計が出現した場所。神殿は労働力と穀物を集約し、配給する経済単位として機能した。",
        geo_scope={"site": "Uruk (Warka)", "region": "Sumer", "country_modern": "Iraq"},
        start_date=None, start_date_precision="period",
        end_date=None, end_date_precision="period",
        status="extinct",
        attributes={
            "bc_start_year_int": -3500,
            "bc_end_year_int": -2900,
            "period_label": "BC3500-BC2900 (Uruk IV-III; later phases continue with breaks)",
            "innovations": ["proto-cuneiform tablets", "standardized ration accounting",
                            "centralized labor coordination"],
            "tablets_excavated": "5000+ archaic tablets (Uruk IV-III)",
            "date_convention_note": "start/end_date は NULL で precision='period'。BC 年は attributes と claim にて記録",
        },
        external_ids={"wikidata": "Q839929"},
    )
    inserted.append(("organization", eanna, "Eanna 神殿"))

    eanna_claim_period = add_claim(
        "organization", eanna, "start_date", "partial",
        {"bc_start_year_int": -3500, "bc_end_year_int": -2900,
         "phase": "Uruk IV-III",
         "context": "考古層位による相対年代。絶対年代は ±100 年程度の幅"},
        src_pollock, 0.8,
        note="後期ウルク期の標準的編年 (Pollock 1999, Nissen 1993)。神殿区画の連続性は前後の期にも及ぶがピークはこの期")

    assign_form(eanna, "historical_era", "temple_economy", is_primary=True,
                confidence=0.95, claim_id=eanna_claim_period)
    assign_form(eanna, "historical_era", "ancient_bureaucracy", confidence=0.7,
                claim_id=add_claim("organization_form_assignment", eanna, "form", "partial",
                    {"reasoning": "神殿経済が proto-bureaucracy を含むという解釈は標準的だが、'bureaucracy' を当てるかは学派による"},
                    src_bottero, 0.7,
                    note="Weber 的官僚制概念をそのまま当てるのは慎重に"))

    act_eanna_redist = add_activity(
        eanna, "redistribution", domain="経済",
        description="穀物・羊毛・ビールの集積と労働者への配給。粘土板に bevel-rim bowl 単位の rations を記録",
        inputs={"crops": "barley", "livestock": "sheep", "labor": "corvée"},
        outputs={"rations": "bevel-rim bowls of barley/beer", "textiles": "wool products"},
        scale={"tablets_per_year": "hundreds", "estimate_workers": "thousands"},
        orientation="exploitation", confidence=0.85,
        claim_id=add_claim("activity", "pending", "scale", "partial",
            {"basis": "Nissen 1993 の出土粘土板計数および bevel-rim bowl 大量出土から推定"},
            src_nissen_1993, 0.8))

    act_eanna_writing = add_activity(
        eanna, "knowledge_preservation", domain="知識",
        description="proto-cuneiform 粘土板による会計、後の楔形文字へ発展する記号体系の発祥",
        outputs={"innovation": "proto-cuneiform script", "lex_lists": "early word lists"},
        orientation="exploration", confidence=0.9)

    act_eanna_ritual = add_activity(
        eanna, "religious_practice", domain="儀礼",
        description="イナンナ/アヌ祭祀、年中行事と王権の正統化儀礼",
        orientation="exploitation", confidence=0.85)

    add_function(eanna, "miller_03_ingestor",
                 mechanism={"means": ["租税・貢納", "神殿土地からの収穫", "強制労働 (corvée)"]},
                 activity_id=act_eanna_redist, confidence=0.85)
    add_function(eanna, "miller_07_matter_energy_storage",
                 mechanism={"means": ["神殿倉庫 (granary)", "標準容器 (bevel-rim bowl)"]},
                 confidence=0.9)
    add_function(eanna, "miller_04_distributor",
                 mechanism={"means": ["労働者への ration 配給", "祭祀供物配分"]},
                 activity_id=act_eanna_redist, confidence=0.85)
    add_function(eanna, "miller_17_memory",
                 mechanism={"means": ["proto-cuneiform 粘土板", "数値トークン"]},
                 activity_id=act_eanna_writing, confidence=0.95)
    add_function(eanna, "miller_15_decoder",
                 mechanism={"means": ["神官筆記者 (umbisag) による粘土板解読", "標準化された記号体系"]},
                 confidence=0.8)
    add_function(eanna, "vsm_s5_policy_identity",
                 mechanism={"means": ["女神イナンナの神殿としての宇宙論的正当化", "王権との結合"]},
                 confidence=0.75)

    add_impact(eanna, "文化", "writing_invention",
               {"description": "proto-cuneiform は世界最古級の体系的書記の一つで、後の楔形文字・西アジア書記文化全般の鋳型"},
               "positive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.95,
               affected_scope={"region": "ancient_near_east", "duration_years": 3000})
    add_impact(eanna, "経済", "redistributive_economy_template",
               {"description": "神殿による集積・配給モデルはメソポタミア都市国家経済の基本形となり、palace economy へ受け継がれた"},
               "descriptive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.85,
               affected_scope={"region": "sumer_akkad", "duration_years": 2000})

    e_eanna_proto = add_event("founding",
        event_date=None, event_date_precision="period",
        description="Eanna 神殿区画の Uruk IV 期建設フェーズ、proto-cuneiform 出現",
        causes={"social": "都市化 (Uruk expansion)", "economic": "余剰穀物の集中管理需要"},
        outcomes={"innovation": "proto-cuneiform", "institution": "temple economy"},
        location={"site": "Eanna precinct, Uruk"},
        vsr_label="variation", confidence=0.85,
        claim_id=add_claim("event", "pending", "event_date", "partial",
            {"phase": "Uruk IV", "bc_year_approx": -3300},
            src_nissen_1993, 0.75,
            note="絶対年代は標準偏年で BC3300±100 程度"))
    link_event_org(e_eanna_proto, eanna, "venue")

    # ============================================================
    # CASE 2: エジプト第18王朝の宰相 djati / vizier (BC1550-BC1295)
    # ============================================================
    djati = add_org(
        canonical_name="エジプト第18王朝の宰相 (djati / vizier)",
        alternate_names=[
            {"name": "djati", "lang": "egy"},
            {"name": "tjati", "lang": "egy"},
            {"name": "vizier of the 18th Dynasty", "lang": "en"},
            {"name": "ジャティ", "lang": "ja"},
        ],
        description="新王国時代第18王朝 (BC1550–BC1295) において、ファラオに次ぐ最高位の文官職。Rekhmire 墓 (TT100) に詳述された 'Duties of the Vizier' 文書により職務範囲が明確化。徴税・司法・国家倉庫管理・地方総督監督を統括する古代官僚制の頂点で、上下エジプトに二人体制 (上エジプト宰相と下エジプト宰相) が敷かれた。",
        geo_scope={"capitals": ["Thebes", "Memphis"], "region": "Egypt"},
        start_date=None, start_date_precision="period",
        end_date=None, end_date_precision="period",
        status="extinct",
        attributes={
            "bc_start_year_int": -1550,
            "bc_end_year_int": -1295,
            "period_label": "BC1550-BC1295 (18th Dynasty, New Kingdom)",
            "structure": "dual_vizier (Upper & Lower Egypt)",
            "primary_source": "Tomb of Rekhmire TT100 'Duties of the Vizier'",
            "non_hereditary": "原則任命職 (世襲ではない)",
            "date_convention_note": "djati 職位そのものは古王国から既にあるが、本ケースは18王朝期の制度成熟形に焦点",
        },
        external_ids={"wikidata": "Q1057714"},
    )
    inserted.append(("organization", djati, "djati 宰相 (18th Dynasty)"))

    djati_claim = add_claim(
        "organization", djati, "start_date", "partial",
        {"period": "18th Dynasty", "bc_start_year_int": -1550, "bc_end_year_int": -1295,
         "context": "職位は古王国から存在するが、Rekhmire 文書による職務記述は18王朝期"},
        src_van_den_boorn, 0.85,
        note="本ケースは職位の歴史全期ではなく18王朝の制度成熟形に絞っている")

    assign_form(djati, "historical_era", "ancient_bureaucracy", is_primary=True,
                confidence=0.95, claim_id=djati_claim)
    assign_form(djati, "mintzberg_1989", "machine_bureaucracy", confidence=0.5,
                claim_id=add_claim("organization_form_assignment", djati, "form", "partial",
                    {"reasoning": "標準化された手続きに依拠する点で機械的官僚制の前駆だが、Mintzberg の現代型分類を完全適用するのは時代錯誤"},
                    src_finer, 0.5,
                    note="比較解釈レベル"))

    act_djati_admin = add_activity(
        djati, "administration", domain="統治",
        description="徴税監督、司法 (六法廷を主宰)、国家倉庫管理、地方総督任免",
        scale={"province_oversight": "all_nomes", "court_role": "supreme_judge_under_pharaoh"},
        orientation="exploitation", confidence=0.85,
        claim_id=add_claim("activity", "pending", "description", "present",
            {"source": "Rekhmire TT100 'Duties of the Vizier' に記述"},
            src_van_den_boorn, 0.85))

    act_djati_recordkeep = add_activity(
        djati, "recordkeeping", domain="知識",
        description="王令の写本作成、徴税台帳・司法判決の保管、官印管理",
        outputs={"records": "papyrus rolls", "seals": "official seal of vizier"},
        orientation="exploitation", confidence=0.85)

    add_function(djati, "miller_18_decider",
                 mechanism={"means": ["宰相裁定 (六法廷)", "ファラオへの上奏とそれに基づく勅令起案"]},
                 activity_id=act_djati_admin, confidence=0.9)
    add_function(djati, "vsm_s3_internal_control",
                 mechanism={"means": ["地方 nome 総督への監督指示", "倉庫監査"]},
                 confidence=0.9)
    add_function(djati, "miller_17_memory",
                 mechanism={"means": ["パピルス記録庫", "宰相印", "王令写本"]},
                 activity_id=act_djati_recordkeep, confidence=0.9)
    add_function(djati, "miller_03_ingestor",
                 mechanism={"means": ["徴税監督 (収穫税、人頭労役)"]},
                 confidence=0.8)
    add_function(djati, "miller_19_encoder",
                 mechanism={"means": ["王令の正式な書式化と封印", "ヒエログリフ・ヒエラティック文書"]},
                 confidence=0.85)

    add_impact(djati, "政治", "centralized_administration",
               {"description": "ファラオ直下の単一最高官による中央集権的官僚制のモデル"},
               "descriptive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.85,
               affected_scope={"region": "egypt", "duration_years": 1500})
    add_impact(djati, "文化", "duties_text_legacy",
               {"description": "'Duties of the Vizier' 文書は古代エジプト行政文書の代表的テキストとして残存"},
               "descriptive", "intergenerational",
               evaluation_method="textual_analysis", confidence=0.9)

    e_djati_rekhmire = add_event("reform",
        event_date=None, event_date_precision="period",
        description="Rekhmire (Thutmose III/Amenhotep II 治世) の墓 TT100 に 'Duties of the Vizier' が彫刻され、宰相職務が成文化される",
        outcomes={"artifact": "TT100 inscriptions", "knowledge": "vizier role codified"},
        location={"site": "Sheikh Abd el-Qurna, Thebes"},
        vsr_label="retention", confidence=0.9,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"reign": "Thutmose III - Amenhotep II", "bc_year_approx": -1450},
            src_van_den_boorn, 0.9))
    link_event_org(e_djati_rekhmire, djati, "subject")

    # ============================================================
    # CASE 3: ローマ legio (post-Marian reform, BC107-AD476)
    # ============================================================
    legio = add_org(
        canonical_name="ローマ軍団 (Roman legio, post-Marian)",
        alternate_names=[
            {"name": "legio", "lang": "la"},
            {"name": "Roman legion", "lang": "en"},
            {"name": "ローマ・レギオ", "lang": "ja"},
        ],
        description="マリウス改革 (BC107) 以降の職業常備軍としてのローマ軍団。市民兵制から募兵制 (proletarii の徴募) へ転換し、16-25 年の任期、退役時の土地給付、標準化された装備と組織 (cohort 単位への再編) を採用した。約 5,000 人の重装歩兵と補助兵を中核とする戦術組織であり、同時に道路・要塞建設・属州行政の実行装置でもあった。",
        geo_scope={"hq": "Rome", "deployment": "Mediterranean and beyond"},
        start_date=None, start_date_precision="period",
        end_date="0476-09-04", end_date_precision="year",
        status="extinct",
        attributes={
            "bc_start_year_int": -107,
            "bc_end_year_int": 476,
            "period_label": "BC107 (Marian reform) - AD476 (Western Empire fall)",
            "core_unit_size": "5000 legionaries + auxilia",
            "tenure_years": "16-25",
            "innovations": ["professional standing army", "post-service land grants",
                            "cohort organization", "engineer corps"],
            "peak_legion_count": "approx 25-33 legions in early Empire",
        },
        external_ids={"wikidata": "Q41241"},
    )
    inserted.append(("organization", legio, "ローマ legio"))

    legio_claim = add_claim(
        "organization", legio, "start_date", "partial",
        {"context": "BC107 の Marian reform を制度的起点とするが、共和政期の legio 自体は BC4 世紀から存在",
         "scope_note": "本ケースは職業常備軍化以降の legio に焦点"},
        src_erdkamp, 0.85)

    assign_form(legio, "historical_era", "ancient_bureaucracy", is_primary=True,
                confidence=0.85, claim_id=legio_claim)
    assign_form(legio, "mintzberg_1989", "machine_bureaucracy", confidence=0.7,
                claim_id=add_claim("organization_form_assignment", legio, "form", "partial",
                    {"reasoning": "標準化作業 + 階層的指揮系統で機械的官僚制の古代版モデルとされる"},
                    src_erdkamp, 0.7))
    assign_form(legio, "hannan_freeman", "specialist_narrow", confidence=0.65,
                claim_id=add_claim("organization_form_assignment", legio, "form", "partial",
                    {"reasoning": "戦闘という単一ニッチに特化、ただし工兵・行政機能も備える点で polymorphous 寄り"},
                    src_erdkamp, 0.55,
                    note="解釈は揺れる"))

    act_legio_war = add_activity(
        legio, "military_operations", domain="軍事",
        description="戦闘・征服・占領、属州治安維持",
        scale={"legion_size": 5000, "imperial_total_estimate": "150000-300000"},
        orientation="exploitation", confidence=0.9)

    act_legio_eng = add_activity(
        legio, "infrastructure_construction", domain="生産",
        description="軍道 (via militaris)、要塞 (castra)、橋梁、水道の建設",
        outputs={"road_network_km": "approx 80000 (imperial peak)",
                 "fortifications": "permanent castra across frontiers"},
        orientation="mixed", confidence=0.85)

    act_legio_admin = add_activity(
        legio, "provincial_administration", domain="統治",
        description="占領属州での徴税補助、治安、辺境防衛、書記官 (cornicularii) による文書管理",
        orientation="exploitation", confidence=0.8)

    add_function(legio, "miller_03_ingestor",
                 mechanism={"means": ["徴募 (dilectus)", "退役兵土地給付による継続的補充"]},
                 confidence=0.85)
    add_function(legio, "miller_18_decider",
                 mechanism={"means": ["legatus / centurion 階層", "consilium による合議"]},
                 confidence=0.9)
    add_function(legio, "vsm_s2_coordination",
                 mechanism={"means": ["標準化された訓練 (drill)", "tessera tactica による合言葉伝達"]},
                 confidence=0.85)
    add_function(legio, "miller_01_reproducer",
                 mechanism={"means": ["新兵訓練", "centurion 昇進経路", "退役兵植民市 (colonia) 設立"]},
                 confidence=0.85)
    add_function(legio, "miller_17_memory",
                 mechanism={"means": ["軍団記録 (acta diurna)", "退役証書 (diploma militare)"]},
                 confidence=0.85)
    add_function(legio, "miller_06_producer",
                 mechanism={"means": ["軍団工兵 (fabri) による武具生産・修理"]},
                 confidence=0.75)

    add_impact(legio, "政治", "professional_army_template",
               {"description": "後代の常備軍 (中世後期傭兵団、近代国民軍) のひな型として参照される"},
               "descriptive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.85,
               affected_scope={"region": "western_eurasia", "duration_years": 2000})
    add_impact(legio, "経済", "infrastructure_legacy",
               {"description": "via militaris 網は中世以降も交易路として残存、欧州交通体系の骨格"},
               "positive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.85)
    add_impact(legio, "政治", "imperator_loyalty_shift",
               {"description": "Marian reform 後、兵士の忠誠は元老院ではなく将軍個人へ移り、共和政崩壊を加速"},
               "negative", "long_term",
               evaluation_method="historical_interpretation", confidence=0.8)

    e_legio_marian = add_event("reorganization",
        event_date=None, event_date_precision="period",
        description="Marius によるローマ軍改革。proletarii の徴募開放、装備標準化、cohort 制導入",
        causes={"political": "ユグルタ戦争・キンブリ戦争で兵員不足", "social": "市民兵制の限界"},
        outcomes={"new_form": "professional standing army"},
        vsr_label="variation", confidence=0.85,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"bc_year_approx": -107}, src_erdkamp, 0.85))
    link_event_org(e_legio_marian, legio, "transformed")

    e_legio_fall = add_event("dissolution",
        event_date="0476-09-04", event_date_precision="year",
        description="西ローマ帝国崩壊により西方の legio 体制が機能停止 (東方では Eastern Roman army へ継続)",
        dissolution_cause="war_destruction",
        causes={"political": "西ローマ帝国の解体", "war": "ゲルマン諸族の侵入"},
        outcomes={"successor_partial": "Eastern Roman army (Byzantine themata)"},
        vsr_label="selection", confidence=0.8)
    link_event_org(e_legio_fall, legio, "dissolved")

    # ============================================================
    # CASE 4: ローマ collegia (BC50-AD476)
    # ============================================================
    collegia = add_org(
        canonical_name="ローマの collegia (職業組合・互助結社)",
        alternate_names=[
            {"name": "collegium", "lang": "la"},
            {"name": "Roman professional associations", "lang": "en"},
            {"name": "コレギア", "lang": "ja"},
        ],
        description="共和政末期から帝政期にかけてローマ世界で広く展開した職業・宗教・葬祭目的の自発結社の総称。職人 (fabri)、商人 (mercatores)、船乗り (navicularii)、繊維業者 (centonarii) 等の業種別 collegia が碑文・元老院議決から数百例確認される。共通基金 (arca)、月例会食、葬祭扶助、守護神祭祀を行い、独自の lex (会則) を持った。中世ヨーロッパのギルドとの直接系譜は学派により評価が異なる。",
        geo_scope={"hq": "Rome", "spread": "Italy and provinces"},
        start_date=None, start_date_precision="period",
        end_date="0476-09-04", end_date_precision="year",
        status="extinct",
        attributes={
            "bc_start_year_int": -50,
            "bc_end_year_int": 476,
            "period_label": "BC50 (lex Iulia 規制期前後) - AD476",
            "evidence_count": "数百種の碑文 (CIL) で確認",
            "trade_examples": ["fabri (大工)", "centonarii (古布業)", "navicularii (船主)",
                                "dendrophori (木材運送)", "fullones (洗濯業)"],
            "primary_corpus": "Corpus Inscriptionum Latinarum, lex collegii Lanuvini (CIL XIV 2112)",
        },
        external_ids={"wikidata": "Q1090413"},
    )
    inserted.append(("organization", collegia, "ローマ collegia"))

    collegia_claim = add_claim(
        "organization", collegia, "start_date", "partial",
        {"context": "起源は王政期に遡るとも (Plutarch, Numa) されるが伝説的。共和政後期 BC1 世紀に lex Iulia de collegiis (BC64 廃止令、その後規制) で制度的可視化"},
        src_liu_collegia, 0.7,
        note="制度史上の連続性は議論が多い")

    assign_form(collegia, "historical_era", "medieval_guild", confidence=0.4,
                claim_id=add_claim("organization_form_assignment", collegia, "form", "partial",
                    {"reasoning": "形態類似性はあるが、'medieval_guild' を古代に当てるのは時代錯誤。本割当は taxonomy 比較目的のみ"},
                    src_liu_collegia, 0.4,
                    note="解釈用、is_primary ではない"))
    assign_form(collegia, "legal_form", "guild", is_primary=True, confidence=0.7,
                claim_id=add_claim("organization_form_assignment", collegia, "form", "partial",
                    {"reasoning": "'guild' を広義に取れば該当。狭義の中世ギルドとは制度的に切れている"},
                    src_liu_collegia, 0.7))

    act_col_mutual = add_activity(
        collegia, "mutual_aid", domain="社会",
        description="月例会食、葬祭扶助、守護神祭祀、相互扶助基金 (arca)",
        outputs={"social_function": "professional solidarity, funeral coverage"},
        orientation="exploitation", confidence=0.9,
        claim_id=add_claim("activity", "pending", "description", "present",
            {"source": "lex collegii salutaris of Lanuvium (CIL XIV 2112)"},
            src_liu_collegia, 0.95))

    act_col_trade = add_activity(
        collegia, "trade_coordination", domain="交換",
        description="同業者間の調整、共有施設 (schola)、契約・徒弟慣行の標準化",
        orientation="mixed", confidence=0.7,
        claim_id=add_claim("activity", "pending", "scale", "partial",
            {"caveat": "経済的調整機能は中世ギルドほど強くない、宗教・社交が主"},
            src_liu_collegia, 0.7))

    add_function(collegia, "miller_02_boundary",
                 mechanism={"means": ["入会金 (stips)", "lex collegii (会則) による会員資格"]},
                 confidence=0.9)
    add_function(collegia, "miller_07_matter_energy_storage",
                 mechanism={"means": ["arca (共通金庫)", "schola (集会所)"]},
                 confidence=0.85)
    add_function(collegia, "miller_01_reproducer",
                 mechanism={"means": ["守護神祭祀の継承", "新規 collegium のスポンサーシップ"]},
                 confidence=0.7)
    add_function(collegia, "vsm_s5_policy_identity",
                 mechanism={"means": ["守護神 (patron deity)", "lex collegii"]},
                 confidence=0.85)
    add_function(collegia, "miller_17_memory",
                 mechanism={"means": ["album (会員名簿碑文)", "lex 銘文"]},
                 confidence=0.85)

    add_impact(collegia, "社会", "mutual_aid_template",
               {"description": "都市労働者の自発的互助結社モデル — 葬祭扶助・職業共同体の古代普及形"},
               "positive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.85,
               affected_scope={"region": "roman_empire", "city_count": "数百都市"})
    add_impact(collegia, "政治", "regulatory_attention",
               {"description": "lex Iulia 等の規制対象になるほど政治的に存在感を持つ — 結社の自由と国家統制の最古級事例"},
               "descriptive", "long_term",
               evaluation_method="historical_interpretation", confidence=0.8)

    e_col_lex_iulia = add_event("reform",
        event_date=None, event_date_precision="period",
        description="Lex Iulia de collegiis (Augustus 治世) — 認可制への移行による collegia 規制",
        outcomes={"regulatory_form": "license-based"},
        causes={"political": "Caesar 暗殺後の結社の政治的影響への警戒"},
        vsr_label="selection", confidence=0.8,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"bc_year_approx": -7, "uncertainty_years": 10},
            src_liu_collegia, 0.7))
    link_event_org(e_col_lex_iulia, collegia, "regulated")

    # ============================================================
    # CASE 5: Spartan agoge (BC700-BC371)
    # ============================================================
    agoge = add_org(
        canonical_name="スパルタ agoge (Spartan ἀγωγή education system)",
        alternate_names=[
            {"name": "agōgē", "lang": "grc"},
            {"name": "ἀγωγή", "lang": "grc"},
            {"name": "Spartan upbringing", "lang": "en"},
            {"name": "アゴーゲー", "lang": "ja"},
        ],
        description="古典期スパルタにおいて 7 歳から 30 歳までの男子市民 (Spartiates) を国家が系統的に育成する寄宿制教育・軍事訓練システム。年齢階梯 (rhōba/rhōbidas) に分かれ、共同食堂 (syssitia) で生活、戦闘技能と忍耐・服従を訓練し、krypteia (秘密任務) を経て正式市民となる。Roman 期の懐古主義により多くが理想化されたため、古典期の実態と Roman Sparta の再構築を分離する必要がある (Kennell 1995)。",
        geo_scope={"site": "Sparta (Lakedaimon)", "region": "Laconia"},
        start_date=None, start_date_precision="period",
        end_date=None, end_date_precision="period",
        status="extinct",
        attributes={
            "bc_start_year_int": -700,
            "bc_end_year_int": -371,
            "period_label": "BC700-BC371 (Lycurgan reforms - Battle of Leuctra)",
            "age_grades": "7-30 years (multiple rhōba steps)",
            "graduation": "homoios (peer) status, syssition membership",
            "post_leuctra_decline": "BC371 後は Spartiate 人口激減で機能不全",
            "roman_revival_note": "Roman 期 (BC1-AD3) の 'Spartan mirage' とは分離して扱う (Kennell 1995)",
        },
        external_ids={"wikidata": "Q740192"},
    )
    inserted.append(("organization", agoge, "Spartan agoge"))

    agoge_claim = add_claim(
        "organization", agoge, "start_date", "partial",
        {"context": "起源は Lycurgus 立法 (伝統的に BC9-7 世紀) と伝えられるが Lycurgus 自身が伝説的人物。古典期の制度として確立するのは BC7 世紀後半",
         "bc_start_year_int": -700, "bc_end_year_int": -371},
        src_kennell, 0.65,
        note="絶対年代は曖昧、Kennell は Roman 期再構築との切り分けを強調")

    assign_form(agoge, "historical_era", "ancient_bureaucracy", confidence=0.5,
                claim_id=add_claim("organization_form_assignment", agoge, "form", "partial",
                    {"reasoning": "国家による系統的な人材成形装置だが、'bureaucracy' の語義は弱い。教育機関 + 軍事組織 hybrid"},
                    src_kennell, 0.5,
                    note="該当 taxonomy がないため近接形態を割当"))
    assign_form(agoge, "mintzberg_1989", "missionary", is_primary=True, confidence=0.7,
                claim_id=add_claim("organization_form_assignment", agoge, "form", "partial",
                    {"reasoning": "規範の標準化 (Spartan ethos) が支配的調整メカニズムである点で missionary 形態に近い"},
                    src_kennell, 0.65))

    act_agoge_train = add_activity(
        agoge, "education_training", domain="知識",
        description="7-30 歳男子の段階的軍事・身体・徳育訓練、共同生活、krypteia",
        scale={"cohort_size": "全 Spartiate 男子", "estimated_homoioi_peak": "8000-10000"},
        orientation="exploitation", confidence=0.8)

    act_agoge_socialize = add_activity(
        agoge, "syssitia_messing", domain="社会",
        description="共同食堂 (syssitia / pheiditia) での生涯にわたる共食、相互監視と紐帯形成",
        orientation="exploitation", confidence=0.85,
        claim_id=add_claim("activity", "pending", "description", "present",
            {"source": "Plutarch, Lycurgus 12; Xenophon, Lac. Pol."},
            src_diodorus, 0.7,
            note="一次史料はあるが古典期の運用詳細は再構築含み"))

    act_agoge_krypteia = add_activity(
        agoge, "secret_service", domain="軍事",
        description="krypteia — 上級訓練者がヘイロタイ (helots) を秘密任務で監視・粛清",
        orientation="exploitation", confidence=0.6,
        claim_id=add_claim("activity", "pending", "scale", "partial",
            {"caveat": "krypteia の規模・恒常性は古代史料間で食い違いあり"},
            src_kennell, 0.55,
            note="一次史料の信頼度ばらつき"))

    add_function(agoge, "miller_01_reproducer",
                 mechanism={"means": ["年齢階梯による段階的成形", "Lycurgan ethos の世代継承"]},
                 confidence=0.85)
    add_function(agoge, "miller_05_converter",
                 mechanism={"means": ["少年 (paides) を homoios (戦士市民) へ変換するパイプライン"]},
                 activity_id=act_agoge_train, confidence=0.85)
    add_function(agoge, "vsm_s5_policy_identity",
                 mechanism={"means": ["Lycurgan 体制神話", "Spartan ethos (eunomia)"]},
                 confidence=0.85)
    add_function(agoge, "miller_02_boundary",
                 mechanism={"means": ["agoge 完了 = Spartiate 市民権", "脱落者 (tresantes) の市民権剥奪"]},
                 confidence=0.85)
    add_function(agoge, "miller_06_producer",
                 mechanism={"means": ["重装歩兵 (hoplite) の量産"]},
                 confidence=0.8)

    add_impact(agoge, "政治", "spartan_military_supremacy",
               {"description": "Persian Wars / Peloponnesian War 期の Spartan 重装歩兵優位を支えた人的基盤"},
               "positive", "long_term",
               evaluation_method="historical_interpretation", confidence=0.8,
               affected_scope={"region": "greek_world", "duration_years": 300})
    add_impact(agoge, "文化", "education_archetype",
               {"description": "近代の士官学校・パブリックスクール・全寮制軍事教育の比較対象として参照される"},
               "descriptive", "intergenerational",
               evaluation_method="historical_interpretation", confidence=0.7,
               affected_scope={"target": "modern_military_academies"})
    add_impact(agoge, "社会", "demographic_fragility",
               {"description": "agoge を完了できる Spartiates 男子のプールが減少し oliganthropia (人口欠乏) を招いた"},
               "negative", "long_term",
               evaluation_method="historical_interpretation", confidence=0.8)

    e_agoge_lycurgan = add_event("founding",
        event_date=None, event_date_precision="period",
        description="伝説的な Lycurgan 立法による agoge 制度化 (年代は伝統的伝承)",
        causes={"social": "ヘイロタイ抑圧維持の必要", "political": "Spartan 二重王制下の統合装置"},
        location={"site": "Sparta"},
        vsr_label="variation", confidence=0.55,
        claim_id=add_claim("event", "pending", "date", "partial",
            {"caveat": "Lycurgus 自体が伝説人物の可能性。年代は学説により BC9-7 世紀で揺れる"},
            src_kennell, 0.55))
    link_event_org(e_agoge_lycurgan, agoge, "founder")

    e_agoge_leuctra = add_event("crisis",
        event_date=None, event_date_precision="year",
        description="Battle of Leuctra (BC371) で Spartan 重装歩兵が Theban 軍に敗北、Spartiate 人口危機により agoge 機能低下",
        outcomes={"impact": "agoge の制度的衰退"},
        vsr_label="selection", confidence=0.85,
        claim_id=add_claim("event", "pending", "date", "present",
            {"bc_year_int": -371, "context": "Battle of Leuctra"},
            src_kennell, 0.9))
    link_event_org(e_agoge_leuctra, agoge, "subject")

    # ============================================================
    # Relations: 古代-中世-近代を結ぶ系譜
    # ============================================================
    benedictines_id = get_org_id("ベネディクト会%")
    hansa_id = get_org_id("ハンザ同盟%")
    voc_id = get_org_id("オランダ東インド会社%")
    mansabdar_id = get_org_id("ムガル朝マンサブダール%")
    bologna_id = get_org_id("ボローニャ大学%")
    cluny_id = get_org_id("Cluny 修道会%")

    # Eanna -> ベネディクト会: 神殿の再分配経済 → 修道院経済 (knowledge_transfer 弱め)
    if benedictines_id:
        add_relation(eanna, benedictines_id, "mimetic_isomorphism",
            valid_from=None, valid_to=None,
            relation_attributes={
                "transfer": "神殿経済の再分配・倉庫・記録モデル → 中世修道院経済 (granary, scriptorium)",
                "channel": "古代地中海全般の temple/palace economy 経由、直接系譜は薄い"},
            confidence=0.35, strength=0.3,
            strength_basis="形態類似だが直接的史料連鎖は薄い",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "両者とも自己充足型再分配経済 + 集中倉庫 + 文書記録 を共有するが、3000+年の隔たりがあり中間経路 (Egyptian temple, Roman estate) を経由する"},
                src_pollock, 0.35,
                note="メタファー的・構造的類似のレベル"))

    # djati -> Mansabdari: 古代官僚制 → ムガル官僚制 (制度史的比較)
    if mansabdar_id:
        add_relation(djati, mansabdar_id, "mimetic_isomorphism",
            valid_from=None, valid_to=None,
            relation_attributes={
                "transfer": "中央集権的非世襲官僚制 (徴税 + 司法 + 文書管理) のモデル",
                "channel": "Persian Achaemenid → Sasanian → Islamic 官僚制経由が想定される"},
            confidence=0.4, strength=0.35,
            strength_basis="制度史的比較レベル、直接の文書経路は不明",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "Finer (1997) は古代エジプト官僚制を比較統治史の起点に置くが、ムガルへの伝播は仲介的"},
                src_finer, 0.4,
                note="直接継承ではなく構造比較"))

    # legio -> 中世ギルド (collegia 経由を意図して legio→hansa は弱、collegia→hansa を主)
    if hansa_id:
        add_relation(collegia, hansa_id, "mimetic_isomorphism",
            valid_from=None, valid_to=None,
            relation_attributes={
                "transfer": "都市職業結社モデル (会則・共通基金・守護神/守護聖人)",
                "channel": "古典遺制 (lex collegii) → 教会下の職人結社 (Carolingian) → 中世ギルド"},
            confidence=0.5, strength=0.5,
            strength_basis="制度連続性については学派により評価が割れるが Black 1984, Liu 2009 で部分的支持",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "形態類似 + Carolingian 期の連続性証拠あり、ただし完全連続説は否定的見解も強い"},
                src_liu_collegia, 0.5,
                note="部分継承説。中世ギルドの直接祖型としての主張は強くない"))

    # legio -> VOC (近代企業の準軍事的構造): 弱い mimetic
    if voc_id:
        add_relation(legio, voc_id, "mimetic_isomorphism",
            valid_from="1602-03-20", valid_to="1799-12-31",
            relation_attributes={
                "transfer": "階層的指揮系統 + 標準化作業 + 遠征兵站の鋳型",
                "channel": "Renaissance 軍事マニュアル (Maurice of Nassau) 経由"},
            confidence=0.4, strength=0.35,
            strength_basis="VOC 自身の準軍事性 (要塞・私兵) に Roman/近世軍制の影響",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "Maurice of Nassau の軍事改革 (1590s) が legio をモデルにしたという通説、VOC 準軍事組織はこの線にある"},
                src_erdkamp, 0.4,
                note="間接 (Renaissance 軍制学者経由)"))

    # collegia -> ボローニャ大学 (universitas 概念): legal_form 系譜
    if bologna_id:
        add_relation(collegia, bologna_id, "mimetic_isomorphism",
            valid_from=None, valid_to=None,
            relation_attributes={
                "transfer": "universitas (法人格を持つ自発結社) の語と概念は Roman collegium / corporatio に源流",
                "channel": "Roman law (Digest) 経由、12 世紀のローマ法復興"},
            confidence=0.55, strength=0.55,
            strength_basis="法制史的に確立した用語継承",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "Justinian Digest における collegium / corpus 概念が中世 universitas 法人理論の基礎"},
                src_liu_collegia, 0.6,
                note="法制度上の用語・概念継承は学界で広く認められる"))

    # agoge -> ベネディクト会: 共同生活による人材成形
    if benedictines_id:
        add_relation(agoge, benedictines_id, "mimetic_isomorphism",
            valid_from="0529-01-01", valid_to=None,
            relation_attributes={
                "transfer": "段階的入会 (novitiate)、共同食堂 (refectory ≈ syssitia)、共通規則による生活成形",
                "channel": "古典教養経由、ベネディクトゥス自身の教養に Cassian/砂漠教父経由のギリシャ修徳伝統"},
            confidence=0.3, strength=0.25,
            strength_basis="形態類似のみ。直接的な agoge 言及は Rule にない",
            claim_id=add_claim("relation", "pending", "type", "partial",
                {"reasoning": "両者とも共同生活+段階的入会+規律訓練の構造を持つが、直接系譜の主張は弱い"},
                src_kennell, 0.3,
                note="比較類型として置く、直接継承は主張しない"))

    # agoge -> legio: 古代ギリシャ軍事教育 → ローマ軍訓練 (古典学的弱継承)
    add_relation(agoge, legio, "knowledge_transfer",
        valid_from=None, valid_to=None,
        relation_attributes={
            "transfer": "ヘレニズム期の軍事教育論 (Polybius らによる Spartan 賛美) が Roman 軍規論に影響",
            "channel": "Polybius 等のヘレニズム史家経由"},
        confidence=0.4, strength=0.35,
        strength_basis="Polybius 6 巻における比較憲政論を経由",
        claim_id=add_claim("relation", "pending", "type", "partial",
            {"reasoning": "Polybius は Roman 制度を Spartan/Carthaginian と比較し、後の Roman 自意識に影響"},
            src_kennell, 0.4,
            note="文献的影響レベル、制度的継承ではない"))

    conn.commit()

    # ============================================================
    # Verification
    # ============================================================
    org_ids = (eanna, djati, legio, collegia, agoge)
    print("\n=== 5 ancient cases verification ===")
    cur.execute(
        f"SELECT COUNT(*) FROM organization WHERE organization_id IN ({','.join('?'*5)})",
        org_ids)
    print(f"organizations created: {cur.fetchone()[0]}")
    cur.execute(
        f"SELECT COUNT(*) FROM organization_form_assignment WHERE organization_id IN ({','.join('?'*5)})",
        org_ids)
    print(f"form assignments: {cur.fetchone()[0]}")
    cur.execute(
        f"SELECT COUNT(*) FROM activity WHERE organization_id IN ({','.join('?'*5)})",
        org_ids)
    print(f"activities: {cur.fetchone()[0]}")
    cur.execute(
        f"SELECT COUNT(*) FROM function_record WHERE organization_id IN ({','.join('?'*5)})",
        org_ids)
    print(f"functions: {cur.fetchone()[0]}")
    cur.execute(
        f"SELECT COUNT(*) FROM impact_record WHERE organization_id IN ({','.join('?'*5)})",
        org_ids)
    print(f"impacts: {cur.fetchone()[0]}")
    cur.execute(
        f"""SELECT COUNT(*) FROM relation
            WHERE source_organization_id IN ({','.join('?'*5)})
               OR target_organization_id IN ({','.join('?'*5)})""",
        org_ids + org_ids)
    print(f"relations involving these 5: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM event")
    print(f"events (total): {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claim")
    print(f"claims (total): {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM source")
    print(f"sources (total): {cur.fetchone()[0]}")
    cur.execute("""SELECT COUNT(*) FROM organization
                   WHERE description IS NOT NULL AND attributes IS NOT NULL""")
    print(f"fully-annotated organizations (description + attributes): {cur.fetchone()[0]}")

    print("\n=== inserted ancient cases ===")
    for entity_type, eid, name in inserted:
        print(f"  {entity_type:20s}  {eid[:12]}...  {name}")

    conn.close()


if __name__ == "__main__":
    main()
