-- =============================================================================
-- schema_sqlite_v05_temporal_facet.sql
-- Phase 4 先取りタスク #P: OrganizationTemporalFacet 実装試行
--
-- 目的:
--   静的属性 (organization.start_date / end_date / status) では捉えられない、
--   組織の長期的内部変容 (governance, scale, resource_base, territory, identity,
--   technology, membership, legitimation_basis) を時系列スライスとして記録する。
--
-- 設計原則:
--   - 既存テーブル (v01) を変更しない (ALTER TABLE しない)。新規テーブル追加のみ。
--   - 各 facet レコードは claim 経由で出典を持つ (entity_type='organization_temporal_facet')。
--   - facet_value は JSON。型は facet_type に依存する(柔軟スキーマ)。
--   - valid_from / valid_to は ISO 8601、precision で粒度を表現 (organization と同じ語彙)。
--
-- codex2 概念モデル対応:
--   OrganizationTemporalFacet (organization × time → state slice)
-- =============================================================================

CREATE TABLE organization_temporal_facet (
  organization_facet_id TEXT PRIMARY KEY,
  organization_id       TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  valid_from            TEXT,
  valid_from_precision  TEXT CHECK (valid_from_precision IN
    ('exact','year','decade','century','period','before','after','unknown') OR valid_from_precision IS NULL),
  valid_to              TEXT,
  valid_to_precision    TEXT CHECK (valid_to_precision IN
    ('exact','year','decade','century','period','before','after','unknown') OR valid_to_precision IS NULL),
  facet_type            TEXT NOT NULL CHECK (facet_type IN
    ('membership','governance','resource_base','territory','technology','identity','scale','legitimation_basis')),
  facet_value           TEXT NOT NULL,  -- JSON
  confidence            REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id              TEXT REFERENCES claim(claim_id),
  created_at            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version        INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_otf_org   ON organization_temporal_facet(organization_id);
CREATE INDEX idx_otf_type  ON organization_temporal_facet(facet_type);
CREATE INDEX idx_otf_dates ON organization_temporal_facet(valid_from, valid_to);

-- =============================================================================
-- 検証クエリ例 (Phase 4 #P で 5 ケースを投入後に実行)
-- =============================================================================
--
-- Q1. ある組織のある年における全 facet 状態スナップショット
--     例: 1700 年時点の VOC
--   SELECT facet_type, facet_value, confidence, valid_from, valid_to
--   FROM organization_temporal_facet
--   WHERE organization_id = (SELECT organization_id FROM organization
--                            WHERE canonical_name LIKE '%VOC%')
--     AND (valid_from IS NULL OR valid_from <= '1700-01-01')
--     AND (valid_to   IS NULL OR valid_to   >  '1700-01-01')
--   ORDER BY facet_type;
--
-- Q2. 特定 facet_type の組織内推移 (例: アシャンティの territory 変遷)
--   SELECT valid_from, valid_to, facet_value
--   FROM organization_temporal_facet
--   WHERE organization_id = (SELECT organization_id FROM organization
--                            WHERE canonical_name LIKE '%アシャンティ%')
--     AND facet_type = 'territory'
--   ORDER BY valid_from;
--
-- Q3. 全組織の指定 facet_type 横断比較 (例: 全ケースの governance 変化数)
--   SELECT o.canonical_name, COUNT(*) AS governance_phases
--   FROM organization_temporal_facet f
--   JOIN organization o ON o.organization_id = f.organization_id
--   WHERE f.facet_type = 'governance'
--   GROUP BY o.canonical_name
--   ORDER BY governance_phases DESC;
