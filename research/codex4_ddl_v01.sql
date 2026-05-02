-- ===================================================================
-- 組織を生命として捉える系譜分析 — DDL v0.1
-- 最小入力モデル: organization, organization_form, source, claim
-- ===================================================================
-- 設計原則 (codex2 概念モデル準拠):
--   1. 組織を「時点ごとの観測状態の束」として扱う
--   2. すべての記述を claim 経由で source と confidence に紐づける
--   3. 法人を標準型にせず、家・宗族・修道院・DAO を同等に扱う
--   4. 日付精度を必須化 (exact / year / decade / century / period / unknown)
--   5. JSONB で時代・地域差を吸収しつつ、検索可能性は正規化列で確保
--   6. 倫理的留意: Stream J (Seshat) の NA→Absent 変換問題回避のため
--      claim_value_kind を 5 値化 (present / absent / partial / unknown / inapplicable)
-- ===================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "vector";

-- -------------------------------------------------------------------
-- 共通 ENUM
-- -------------------------------------------------------------------

CREATE TYPE date_precision AS ENUM (
  'exact', 'year', 'decade', 'century', 'period', 'before', 'after', 'unknown'
);
COMMENT ON TYPE date_precision IS
  '日付精度。歴史的組織は exact 日付が取れないことが多いため精度を必須化する。';

CREATE TYPE org_status AS ENUM (
  'active', 'dormant', 'transformed', 'merged', 'split', 'extinct', 'unknown'
);
COMMENT ON TYPE org_status IS
  '組織状態。Stream I (organizational mortality) を踏まえ dormant / transformed を扱う。';

CREATE TYPE claim_value_kind AS ENUM (
  'present', 'absent', 'partial', 'unknown', 'inapplicable'
);
COMMENT ON TYPE claim_value_kind IS
  'claim の値の種類。Stream J (Seshat NA→Absent 撤回事件) を踏まえ、不明・該当なし・部分的 を区別する。';

CREATE TYPE source_type AS ENUM (
  'primary_text', 'secondary_literature', 'dataset', 'interview',
  'archive', 'artifact', 'onchain', 'web', 'oral_history', 'ethnography'
);
COMMENT ON TYPE source_type IS '出典の種類。一次史料からオンチェーンまで全域をカバー。';

-- -------------------------------------------------------------------
-- Source (典拠)
-- -------------------------------------------------------------------

CREATE TABLE source (
  source_id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_type          source_type NOT NULL,
  title                TEXT NOT NULL,
  authors              JSONB,
  publication_date     DATE,
  publisher            TEXT,
  locator              JSONB,
  accessed_at          DATE,
  reliability_score    NUMERIC(3,2) CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0),
  reliability_basis    TEXT,
  bias_notes           TEXT,
  license              TEXT,
  redistribution       TEXT CHECK (redistribution IN ('public_redistributable', 'attribution_required', 'noncommercial', 'private', 'restricted')),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE source IS '文献・史料・データセット等の典拠。再配布条件をフィールド化し公開ゲートで判定可能にする。';
COMMENT ON COLUMN source.reliability_score IS '0.0-1.0 の信頼度。一次史料 ≥ 0.8, 二次文献 0.5-0.8, ブログ等 < 0.5 を目安。';
COMMENT ON COLUMN source.redistribution IS 'public_redistributable のみが v1.0 公開対象。商用 DB は private / restricted。';

CREATE INDEX idx_source_type ON source (source_type);
CREATE INDEX idx_source_redistribution ON source (redistribution);
CREATE INDEX idx_source_pubdate_brin ON source USING BRIN (publication_date);

-- -------------------------------------------------------------------
-- Claim (主張) — すべての記述の親
-- -------------------------------------------------------------------

CREATE TABLE claim (
  claim_id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type          TEXT NOT NULL,
  entity_id            UUID NOT NULL,
  field_path           TEXT,
  value_kind           claim_value_kind NOT NULL,
  claim_value          JSONB,
  source_id            UUID REFERENCES source(source_id) ON DELETE RESTRICT,
  confidence           NUMERIC(3,2) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
  interpretation_note  TEXT,
  recorded_by          TEXT NOT NULL,
  recorded_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  superseded_by        UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE claim IS
  'すべての実体記述の正本。entity_type+entity_id で対象を polymorphic に指す。' ||
  ' Stream J を踏まえ value_kind を 5 値化、Stream I を踏まえ supersede 履歴を持つ。';
COMMENT ON COLUMN claim.entity_type IS '対象テーブル名 (organization, organization_form_assignment 等)';
COMMENT ON COLUMN claim.value_kind IS '値の種類。absent と unknown と inapplicable を区別する (Seshat 教訓)。';
COMMENT ON COLUMN claim.superseded_by IS '後の claim によって置き換えられた場合に参照。元 claim も削除しない。';

CREATE INDEX idx_claim_entity ON claim (entity_type, entity_id);
CREATE INDEX idx_claim_source ON claim (source_id);
CREATE INDEX idx_claim_value_jsonb ON claim USING GIN (claim_value);
CREATE INDEX idx_claim_recorded_brin ON claim USING BRIN (recorded_at);

-- -------------------------------------------------------------------
-- OrganizationForm (型分類)
-- -------------------------------------------------------------------

CREATE TABLE organization_form (
  form_id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  taxonomy_name        TEXT NOT NULL,
  form_code            TEXT NOT NULL,
  label                TEXT NOT NULL,
  parent_form_id       UUID REFERENCES organization_form(form_id),
  definition           TEXT,
  criteria             JSONB,
  valid_period         DATERANGE,
  notes                TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1,
  UNIQUE (taxonomy_name, form_code)
);
COMMENT ON TABLE organization_form IS
  '組織型の分類体系。複数タクソノミー (Mintzberg / Hannan / Laloux / Wikidata 等) を併存させる。';
COMMENT ON COLUMN organization_form.taxonomy_name IS
  '分類体系名。例: "wikidata_subclass", "mintzberg_1989", "hannan_freeman", "laloux_2014", "legal_form_jp"';
COMMENT ON COLUMN organization_form.valid_period IS
  '分類が有効な歴史時期。"za" (中世日本) や "VOC" (1602-1799) のような時代限定型を扱う。';

CREATE INDEX idx_form_taxonomy ON organization_form (taxonomy_name);
CREATE INDEX idx_form_parent ON organization_form (parent_form_id);

-- -------------------------------------------------------------------
-- Organization (コア)
-- -------------------------------------------------------------------

CREATE TABLE organization (
  organization_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_name       TEXT NOT NULL,
  alternate_names      JSONB,
  description          TEXT,
  primary_form_id      UUID REFERENCES organization_form(form_id),
  geo_scope            JSONB,
  start_date           DATE,
  start_date_precision date_precision,
  end_date             DATE,
  end_date_precision   date_precision,
  status               org_status NOT NULL DEFAULT 'unknown',
  attributes           JSONB,
  embedding            vector(384),
  external_ids         JSONB,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE organization IS
  '組織ノードの最小単位。原初バンドから DAO まで同枠で扱う。法人を標準型にしない。';
COMMENT ON COLUMN organization.alternate_names IS
  '別名・現地語名・翻訳名の配列。例: [{"name":"三井越後屋","lang":"ja"},{"name":"Mitsui","lang":"en"}]';
COMMENT ON COLUMN organization.geo_scope IS
  '地理的範囲。点・領域・移動範囲・拠点群のいずれも JSONB で記録。例: {"type":"polity","wkt":"POLYGON(...)"} 等。';
COMMENT ON COLUMN organization.attributes IS
  'core feature 以外の可変属性。Stream codex3 の継承原理・境界・身体性などを格納。';
COMMENT ON COLUMN organization.embedding IS
  'pgvector 用の組織記述 embedding。SBERT (384次元) を想定、規模で 768/1024 へ拡張可能。';
COMMENT ON COLUMN organization.external_ids IS
  '他データベースの ID。例: {"wikidata":"Q312","gleif_lei":"...", "ror":"...", "edinet":"..."}';

CREATE INDEX idx_org_form ON organization (primary_form_id);
CREATE INDEX idx_org_status ON organization (status);
CREATE INDEX idx_org_dates_brin ON organization USING BRIN (start_date, end_date);
CREATE INDEX idx_org_attributes_gin ON organization USING GIN (attributes);
CREATE INDEX idx_org_external_ids_gin ON organization USING GIN (external_ids);
CREATE INDEX idx_org_alternate_names_gin ON organization USING GIN (alternate_names);
-- HNSW vector index は pgvector 0.5+ で利用可。スキーマ作成時にコメント解除。
-- CREATE INDEX idx_org_embedding ON organization USING hnsw (embedding vector_cosine_ops);

-- -------------------------------------------------------------------
-- OrganizationFormAssignment (組織×型の M:N 紐付け、期間つき)
-- -------------------------------------------------------------------

CREATE TABLE organization_form_assignment (
  assignment_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  form_id              UUID NOT NULL REFERENCES organization_form(form_id) ON DELETE RESTRICT,
  valid_from           DATE,
  valid_from_precision date_precision,
  valid_to             DATE,
  valid_to_precision   date_precision,
  is_primary           BOOLEAN NOT NULL DEFAULT false,
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE organization_form_assignment IS
  '組織と分類型の多対多関係。同じ組織が複数タクソノミーで違う型に属するのを許容。';
COMMENT ON COLUMN organization_form_assignment.is_primary IS
  '同一 taxonomy 内で primary はひとつ。アプリ側で UNIQUE 制約を補強する。';

CREATE INDEX idx_ofa_org ON organization_form_assignment (organization_id);
CREATE INDEX idx_ofa_form ON organization_form_assignment (form_id);
CREATE INDEX idx_ofa_valid_brin ON organization_form_assignment USING BRIN (valid_from, valid_to);

-- -------------------------------------------------------------------
-- updated_at トリガ (共通)
-- -------------------------------------------------------------------

CREATE OR REPLACE FUNCTION trg_set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at := now();
  NEW.record_version := COALESCE(OLD.record_version, 0) + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['source','claim','organization_form','organization','organization_form_assignment']
  LOOP
    EXECUTE format(
      'CREATE TRIGGER %I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()',
      t || '_set_updated', t
    );
  END LOOP;
END $$;
