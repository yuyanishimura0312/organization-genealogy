#!/usr/bin/env python3
"""Phase 3 並列タスク #R: 名寄せ品質チェックと外部 ID クロスリンク

実施内容:
  1. 重複候補検出
     - 全 organization (348 件) の canonical_name について difflib.SequenceMatcher を
       全ペアに適用し、ratio > 0.85 のペアをフラグ。
     - ratio が 1.0 に近いほど名寄せ漏れ (誤分離) の疑いが強い。
     - 自動マージはせず、`data/duplicate_candidates.json` に書き出して
       手動レビューに回す。

  2. 外部 ID クロスリンク (Wikidata QID -> ROR ID)
     - 既に ROR を持たず Wikidata QID を持つ organization の中から先頭 30 件を
       パイロットで抽出し、Wikidata REST (Special:EntityData/Q*.json) で
       P6782 (ROR ID) クレームを照会する。WebFetch ではなく urllib を使うのは
       本スクリプトを再現可能なバッチとして実行できるようにするため。
       user-agent: OrganizationGenealogyResearch/0.1 (info@emerging-future.org)
       インターバル: 0.5 秒 (Wikidata の API 利用ガイドライン尊重)
     - クロスリンクが見つかった場合は organization.external_ids に ror を追加
       し、claim を 1 件挿入する (削除は行わない、source は ROR レジストリ)。

  3. 信頼性スコア再算出
     - 対象: entity_type='organization', field_path='canonical_name' の claim。
     - QID のままで正規化が不十分なものは 0.6 -> 0.3 に下げる。
       具体的: canonical_name が ^Q\d+$ (ID をそのまま canonical にしたもの)、
       あるいは alternate_names が空かつ description も空かつ geo_scope も空、
       というように「Wikidata から QID を入れただけ」のケース。
     - 補正:
         + country (geo_scope.country) があれば +0.05
         + end_date があれば +0.05
         + alternate_names が複数言語 (lang が 2 種以上) あれば +0.05
     - 最終 confidence は 0.0..1.0 にクランプ。
     - 旧 claim を superseded_by で連結し、新 claim を挿入 (削除なし)。

成果物:
  - data/duplicate_candidates.json
  - data/data_quality_report.md
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "og.db"
OUT_DUP = ROOT / "data" / "duplicate_candidates.json"
OUT_REPORT = ROOT / "data" / "data_quality_report.md"

USER_AGENT = "OrganizationGenealogyResearch/0.1 (info@emerging-future.org)"
WIKIDATA_BASE = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
WIKIDATA_RATE_SLEEP = 0.5
CROSSLINK_PILOT_LIMIT = 30
DUP_THRESHOLD = 0.85

QID_RE = re.compile(r"^Q\d+$")


def uid():
    return uuid.uuid4().hex


# ----------------------------------------------------------------------
# Wikidata cross-link
# ----------------------------------------------------------------------
def fetch_wikidata_entity(qid: str) -> dict | None:
    url = WIKIDATA_BASE.format(qid=qid)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"  fetch failed {qid}: {e}", flush=True)
        return None
    except json.JSONDecodeError as e:
        print(f"  json decode failed {qid}: {e}", flush=True)
        return None


def extract_ror_from_entity(entity: dict, qid: str) -> str | None:
    """Wikidata entity JSON から P6782 (ROR ID) を抽出。"""
    try:
        ent = entity["entities"][qid]
    except (KeyError, TypeError):
        return None
    claims = ent.get("claims", {})
    p6782 = claims.get("P6782")
    if not p6782:
        return None
    for stmt in p6782:
        try:
            mainsnak = stmt.get("mainsnak", {})
            if mainsnak.get("snaktype") != "value":
                continue
            datavalue = mainsnak.get("datavalue", {})
            value = datavalue.get("value")
            if isinstance(value, str) and value:
                return value.strip()
        except Exception:
            continue
    return None


# ----------------------------------------------------------------------
# Source helpers (look up existing rows; do not duplicate)
# ----------------------------------------------------------------------
def get_or_create_source(cur, title: str, defaults: dict) -> str:
    row = cur.execute("SELECT source_id FROM source WHERE title = ? LIMIT 1", (title,)).fetchone()
    if row:
        return row[0]
    sid = uid()
    cur.execute(
        """INSERT INTO source (source_id, source_type, title, publisher, locator,
            accessed_at, reliability_score, reliability_basis, license, redistribution)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            sid,
            defaults["source_type"],
            title,
            defaults.get("publisher"),
            json.dumps(defaults["locator"], ensure_ascii=False) if defaults.get("locator") else None,
            time.strftime("%Y-%m-%d"),
            defaults.get("reliability_score"),
            defaults.get("reliability_basis"),
            defaults.get("license"),
            defaults.get("redistribution", "attribution_required"),
        ),
    )
    return sid


def insert_claim(cur, *, entity_type, entity_id, field_path, value_kind,
                 claim_value, source_id, confidence, recorded_by, note=None,
                 superseded_by=None) -> str:
    cid = uid()
    cur.execute(
        """INSERT INTO claim
           (claim_id, entity_type, entity_id, field_path, value_kind,
            claim_value, source_id, confidence, recorded_by, interpretation_note,
            superseded_by)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            cid,
            entity_type,
            entity_id,
            field_path,
            value_kind,
            json.dumps(claim_value, ensure_ascii=False) if claim_value is not None else None,
            source_id,
            confidence,
            recorded_by,
            note,
            superseded_by,
        ),
    )
    return cid


# ----------------------------------------------------------------------
# Step 1: duplicate detection
# ----------------------------------------------------------------------
def normalize_for_match(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def detect_duplicates(rows: list[dict]) -> list[dict]:
    """全 organization の canonical_name 全ペアに SequenceMatcher を適用。"""
    n = len(rows)
    pairs: list[dict] = []
    norms = [normalize_for_match(r["canonical_name"]) for r in rows]
    for i in range(n):
        a = norms[i]
        if not a:
            continue
        for j in range(i + 1, n):
            b = norms[j]
            if not b:
                continue
            # 短い名前のペアの誤検出を抑制 (4 文字以下は固有性が低い)
            if min(len(a), len(b)) < 4:
                continue
            ratio = SequenceMatcher(None, a, b).ratio()
            if ratio > DUP_THRESHOLD:
                pairs.append({
                    "ratio": round(ratio, 4),
                    "a": {
                        "organization_id": rows[i]["organization_id"],
                        "canonical_name": rows[i]["canonical_name"],
                        "external_ids": rows[i]["external_ids"],
                    },
                    "b": {
                        "organization_id": rows[j]["organization_id"],
                        "canonical_name": rows[j]["canonical_name"],
                        "external_ids": rows[j]["external_ids"],
                    },
                })
    pairs.sort(key=lambda x: x["ratio"], reverse=True)
    return pairs


# ----------------------------------------------------------------------
# Step 3: confidence recompute
# ----------------------------------------------------------------------
def compute_new_confidence(org: dict, base: float) -> tuple[float, list[str]]:
    """canonical_name claim の新しい confidence を計算。"""
    notes: list[str] = []
    canonical = org["canonical_name"] or ""
    alt_raw = org["alternate_names"]
    geo_raw = org["geo_scope"]
    end_date = org["end_date"]

    try:
        alt = json.loads(alt_raw) if alt_raw else []
    except Exception:
        alt = []
    try:
        geo = json.loads(geo_raw) if geo_raw else {}
    except Exception:
        geo = {}

    # 「QID をそのまま入れただけ」と判断する条件
    qid_only = bool(QID_RE.match(canonical))
    bare_metadata = (not alt) and (not geo) and (not end_date)

    score = base
    if qid_only:
        score = 0.3
        notes.append("canonical=QID のみ -> 0.3")
    elif bare_metadata and base == 0.6:
        score = 0.3
        notes.append("alt/geo/end_date 全欠 -> 0.3")

    # ボーナス
    country = None
    if isinstance(geo, dict):
        country = geo.get("country") or geo.get("hq")
    if country:
        score += 0.05
        notes.append("+0.05 country")
    if end_date:
        score += 0.05
        notes.append("+0.05 end_date")
    if isinstance(alt, list) and alt:
        langs: set[str] = set()
        for a in alt:
            if isinstance(a, dict):
                lang = a.get("lang")
                if lang:
                    langs.add(lang)
        if len(langs) >= 2:
            score += 0.05
            notes.append("+0.05 multi-lang alt")

    # クランプ
    score = max(0.0, min(1.0, score))
    return round(score, 4), notes


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # -------- organizations を取得 --------
    cur.execute(
        """SELECT organization_id, canonical_name, alternate_names, description,
                  geo_scope, start_date, end_date, status, attributes, external_ids
             FROM organization"""
    )
    cols = [c[0] for c in cur.description]
    orgs = [dict(zip(cols, r)) for r in cur.fetchall()]
    print(f"loaded {len(orgs)} organizations", flush=True)

    # -------- Step 1: duplicate detection --------
    print("\n[Step 1] duplicate detection (difflib SequenceMatcher)", flush=True)
    dup_pairs = detect_duplicates(orgs)
    print(f"  duplicate candidates (ratio > {DUP_THRESHOLD}): {len(dup_pairs)}", flush=True)

    OUT_DUP.parent.mkdir(parents=True, exist_ok=True)
    with OUT_DUP.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "threshold": DUP_THRESHOLD,
                "method": "difflib.SequenceMatcher on lowercased canonical_name",
                "n_organizations": len(orgs),
                "n_pairs": len(dup_pairs),
                "pairs": dup_pairs,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  wrote {OUT_DUP}", flush=True)

    # -------- Step 2: cross-link Wikidata QID -> ROR --------
    print("\n[Step 2] Wikidata QID -> ROR cross-link pilot", flush=True)
    candidates: list[dict] = []
    for o in orgs:
        try:
            ext = json.loads(o["external_ids"]) if o["external_ids"] else {}
        except Exception:
            ext = {}
        if "ror" in ext:
            continue
        qid = ext.get("wikidata")
        if not qid or not QID_RE.match(qid):
            continue
        candidates.append({"org": o, "qid": qid})
    print(f"  pure-Wikidata orgs to probe: {len(candidates)} (pilot limit {CROSSLINK_PILOT_LIMIT})", flush=True)

    pilot = candidates[:CROSSLINK_PILOT_LIMIT]
    crosslink_attempts = len(pilot)
    crosslink_hits = 0
    crosslink_results: list[dict] = []

    ror_source_id = None
    if crosslink_attempts:
        ror_source_id = get_or_create_source(
            cur,
            "ROR (Research Organization Registry)",
            {
                "source_type": "dataset",
                "publisher": "Research Organization Registry",
                "locator": {"url": "https://api.ror.org/v2/organizations"},
                "reliability_score": 0.85,
                "reliability_basis": "学術機関の正規化 ID 体系。Crossref/OpenAlex と統合された信頼性の高いオープンデータ。",
                "license": "CC0",
                "redistribution": "public_redistributable",
            },
        )

    for idx, c in enumerate(pilot, 1):
        qid = c["qid"]
        org = c["org"]
        print(f"  [{idx}/{crosslink_attempts}] {qid} :: {org['canonical_name'][:40]}", flush=True)
        entity = fetch_wikidata_entity(qid)
        time.sleep(WIKIDATA_RATE_SLEEP)
        if not entity:
            crosslink_results.append({"qid": qid, "organization_id": org["organization_id"], "ror": None, "error": "fetch_failed"})
            continue
        ror_id = extract_ror_from_entity(entity, qid)
        if not ror_id:
            crosslink_results.append({"qid": qid, "organization_id": org["organization_id"], "ror": None})
            continue
        crosslink_hits += 1
        crosslink_results.append({"qid": qid, "organization_id": org["organization_id"], "ror": ror_id})
        # external_ids 更新 + claim 挿入
        try:
            ext = json.loads(org["external_ids"]) if org["external_ids"] else {}
        except Exception:
            ext = {}
        ext["ror"] = ror_id
        new_ext = json.dumps(ext, ensure_ascii=False)
        cur.execute(
            "UPDATE organization SET external_ids = ? WHERE organization_id = ?",
            (new_ext, org["organization_id"]),
        )
        insert_claim(
            cur,
            entity_type="organization",
            entity_id=org["organization_id"],
            field_path="external_ids.ror",
            value_kind="present",
            claim_value={"ror": ror_id, "via": f"wikidata:{qid}:P6782"},
            source_id=ror_source_id,
            confidence=0.85,
            recorded_by="dedupe_quality_etl",
            note=f"Cross-linked from Wikidata {qid} P6782",
        )
        conn.commit()

    print(f"  cross-link hits: {crosslink_hits}/{crosslink_attempts}", flush=True)

    # -------- Step 3: confidence recompute --------
    print("\n[Step 3] confidence recompute for canonical_name claims", flush=True)
    cur.execute(
        """SELECT claim_id, entity_id, confidence
             FROM claim
            WHERE entity_type='organization'
              AND field_path='canonical_name'
              AND superseded_by IS NULL"""
    )
    existing_claims = cur.fetchall()
    print(f"  active canonical_name claims: {len(existing_claims)}", flush=True)

    by_id = {o["organization_id"]: o for o in orgs}
    before_scores: list[float] = []
    after_scores: list[float] = []
    flagged_low: list[dict] = []
    revised: list[dict] = []

    quality_source_id = get_or_create_source(
        cur,
        "Internal: dedupe & quality re-evaluation 2026-05-02",
        {
            "source_type": "dataset",
            "publisher": "OrganizationGenealogy ETL pipeline",
            "locator": {"script": "etl/17_dedupe_quality.py"},
            "reliability_score": 0.7,
            "reliability_basis": "ルールベース再算出。canonical_name が QID のみ等の貧弱なケースを下方修正、country/end_date/multi-lang alt があれば上方修正。",
            "license": "internal",
            "redistribution": "private",
        },
    )

    for claim_id, entity_id, conf in existing_claims:
        before_scores.append(conf)
        org = by_id.get(entity_id)
        if not org:
            after_scores.append(conf)
            continue
        new_conf, notes = compute_new_confidence(org, conf)
        after_scores.append(new_conf)
        if abs(new_conf - conf) < 1e-9:
            continue
        # 新 claim を挿入し旧 claim を superseded_by で連結
        new_claim_id = insert_claim(
            cur,
            entity_type="organization",
            entity_id=entity_id,
            field_path="canonical_name",
            value_kind="present",
            claim_value={
                "value": org["canonical_name"],
                "previous_confidence": conf,
                "delta": round(new_conf - conf, 4),
                "rules_applied": notes,
            },
            source_id=quality_source_id,
            confidence=new_conf,
            recorded_by="dedupe_quality_etl",
            note="Re-evaluated by 17_dedupe_quality.py rules",
        )
        cur.execute(
            "UPDATE claim SET superseded_by = ? WHERE claim_id = ?",
            (new_claim_id, claim_id),
        )
        revised.append({
            "organization_id": entity_id,
            "canonical_name": org["canonical_name"],
            "before": conf,
            "after": new_conf,
            "rules": notes,
        })
        if new_conf <= 0.35:
            flagged_low.append({
                "organization_id": entity_id,
                "canonical_name": org["canonical_name"],
                "before": conf,
                "after": new_conf,
                "rules": notes,
            })

    conn.commit()

    avg_before = sum(before_scores) / len(before_scores) if before_scores else 0.0
    avg_after = sum(after_scores) / len(after_scores) if after_scores else 0.0
    print(f"  revised claims: {len(revised)}", flush=True)
    print(f"  avg confidence before={avg_before:.4f} after={avg_after:.4f}", flush=True)

    # -------- distribution buckets --------
    def bucketize(values: list[float]) -> dict[str, int]:
        buckets = {
            "<0.30": 0,
            "0.30-0.49": 0,
            "0.50-0.69": 0,
            "0.70-0.84": 0,
            "0.85-1.00": 0,
        }
        for v in values:
            if v < 0.30:
                buckets["<0.30"] += 1
            elif v < 0.50:
                buckets["0.30-0.49"] += 1
            elif v < 0.70:
                buckets["0.50-0.69"] += 1
            elif v < 0.85:
                buckets["0.70-0.84"] += 1
            else:
                buckets["0.85-1.00"] += 1
        return buckets

    dist_before = bucketize(before_scores)
    dist_after = bucketize(after_scores)

    # -------- Manual review top 20 --------
    # 重複候補 ratio 上位 20 を中心に、加えて低信頼 (after <= 0.35) を補完
    review_seen: set[str] = set()
    review_items: list[dict] = []
    for p in dup_pairs[:20]:
        key = f"{p['a']['organization_id']}|{p['b']['organization_id']}"
        review_seen.add(key)
        review_items.append({
            "kind": "duplicate_candidate",
            "ratio": p["ratio"],
            "a_name": p["a"]["canonical_name"],
            "b_name": p["b"]["canonical_name"],
            "a_id": p["a"]["organization_id"],
            "b_id": p["b"]["organization_id"],
        })
    review_items = review_items[:20]

    # -------- Step 4: write report --------
    lines: list[str] = []
    lines.append("# Data Quality Report (Phase 3 #R)\n")
    lines.append(f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_\n")
    lines.append(f"- organizations 総数: **{len(orgs)}**\n")
    lines.append("\n## 1. 重複候補 (canonical_name ratio > 0.85)\n")
    lines.append(f"- 候補ペア数: **{len(dup_pairs)}**\n")
    lines.append(f"- 検出手法: difflib.SequenceMatcher (lowercase normalize、最短 4 字未満は除外)\n")
    if dup_pairs:
        lines.append("\n### Top 10 by ratio\n")
        lines.append("| ratio | A | B |\n")
        lines.append("|---:|---|---|\n")
        for p in dup_pairs[:10]:
            a = p["a"]["canonical_name"].replace("|", r"\|")
            b = p["b"]["canonical_name"].replace("|", r"\|")
            lines.append(f"| {p['ratio']:.3f} | {a} (`{p['a']['organization_id'][:8]}`) | {b} (`{p['b']['organization_id'][:8]}`) |\n")
    else:
        lines.append("\n_該当なし_\n")

    lines.append("\n## 2. 外部 ID クロスリンク (Wikidata QID -> ROR)\n")
    lines.append(f"- 試行: **{crosslink_attempts}** 件 (パイロット limit {CROSSLINK_PILOT_LIMIT})\n")
    lines.append(f"- 取得成功: **{crosslink_hits}** 件\n")
    lines.append(f"- API: Wikidata REST `Special:EntityData/Qxxx.json`、user-agent={USER_AGENT}、interval={WIKIDATA_RATE_SLEEP}s\n")
    if crosslink_hits:
        lines.append("\n### 取得した ROR ID\n")
        lines.append("| QID | organization_id | ROR |\n")
        lines.append("|---|---|---|\n")
        for r in crosslink_results:
            if r.get("ror"):
                lines.append(f"| {r['qid']} | `{r['organization_id'][:8]}` | {r['ror']} |\n")

    lines.append("\n## 3. 信頼性スコア再算出\n")
    lines.append(f"- 対象 claim: canonical_name (active) **{len(existing_claims)}** 件\n")
    lines.append(f"- 修正された claim: **{len(revised)}** 件\n")
    lines.append(f"- 平均 confidence: before=**{avg_before:.4f}** -> after=**{avg_after:.4f}**\n")
    lines.append(f"- フラグ件数 (after <= 0.35): **{len(flagged_low)}**\n")
    lines.append("\n### 分布 (before / after)\n")
    lines.append("| bucket | before | after |\n")
    lines.append("|---|---:|---:|\n")
    for k in ["<0.30", "0.30-0.49", "0.50-0.69", "0.70-0.84", "0.85-1.00"]:
        lines.append(f"| {k} | {dist_before[k]} | {dist_after[k]} |\n")

    lines.append("\n## 4. 手動レビュー対象 Top 20\n")
    if review_items:
        lines.append("| # | kind | ratio | A | B |\n")
        lines.append("|---:|---|---:|---|---|\n")
        for i, r in enumerate(review_items, 1):
            a = r.get("a_name", "").replace("|", r"\|")
            b = r.get("b_name", "").replace("|", r"\|")
            lines.append(f"| {i} | {r['kind']} | {r.get('ratio', ''):.3f} | {a} (`{r['a_id'][:8]}`) | {b} (`{r['b_id'][:8]}`) |\n")
    else:
        lines.append("\n_該当なし_\n")

    lines.append("\n## 5. ルール\n")
    lines.append("- 削除なし: 旧 claim は `superseded_by` で新 claim にリンク。\n")
    lines.append("- canonical_name が `^Q\\d+$` のとき confidence -> 0.3。\n")
    lines.append("- alternate_names 空 + geo_scope 空 + end_date 空、かつ before=0.6 のとき confidence -> 0.3。\n")
    lines.append("- ボーナス: country 有 +0.05 / end_date 有 +0.05 / alt 多言語 +0.05 (clamp 0..1)。\n")

    OUT_REPORT.write_text("".join(lines), encoding="utf-8")
    print(f"\nwrote {OUT_REPORT}", flush=True)

    # -------- Print summary including most prominent dup + averages --------
    print("\n=== summary ===", flush=True)
    if dup_pairs:
        top = dup_pairs[0]
        print(f"top duplicate: ratio={top['ratio']:.3f}", flush=True)
        print(f"  A: {top['a']['canonical_name']} ({top['a']['organization_id']})", flush=True)
        print(f"  B: {top['b']['canonical_name']} ({top['b']['organization_id']})", flush=True)
    print(f"avg confidence before={avg_before:.4f} after={avg_after:.4f}", flush=True)
    print(f"crosslink hits={crosslink_hits}/{crosslink_attempts}", flush=True)
    print(f"revised claims={len(revised)} flagged_low={len(flagged_low)}", flush=True)

    conn.close()


if __name__ == "__main__":
    main()
