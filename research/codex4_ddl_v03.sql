-- ===================================================================
-- 組織を生命として捉える系譜分析 — DDL v0.3
-- 関係 (Relation) と イベント (Event) の追加
-- v0.1 + v0.2 の上に積む。系譜ネットワークの基盤。
-- ===================================================================
-- 設計判断:
--   1. Relation は M&A・模倣・継承を扱うため水平伝達 (horizontal transmission) を許容
--      Stream K の phylogenetic network 対応として relation_type に knowledge_transfer/mimetic を含める
--   2. Event は組織の死亡・分裂・再生を扱う。Stream I に基づき dormancy 状態を別途記録
--   3. 制度的同型化 (DiMaggio-Powell) を捕捉するため Stream L の coercive/mimetic/normative を relation_type に
-- ===================================================================

-- -------------------------------------------------------------------
-- ENUM
-- -------------------------------------------------------------------

CREATE TYPE relation_type AS ENUM (
  'alliance', 'competition', 'control', 'subsidiary', 'partnership',
  'membership', 'succession', 'spin_off', 'merger', 'acquisition',
  'trade', 'funding', 'shareholding',
  'knowledge_transfer', 'mimetic_isomorphism', 'normative_pressure', 'coercive_pressure',
  'protocol_dependency', 'supply_chain', 'interlocking_directorate',
  'patronage', 'rivalry', 'schism', 'unknown'
);
COMMENT ON TYPE relation_type IS
  '組織間関係の種別。Stream B (歴史系譜) + Stream L (制度論) + Stream K (水平伝達) を統合。' ||
  'mimetic/normative/coercive は DiMaggio-Powell の同型化圧力。';

CREATE TYPE relation_directionality AS ENUM ('directed', 'undirected', 'bidirectional');

CREATE TYPE event_type AS ENUM (
  'founding', 'dissolution', 'merger', 'acquisition', 'split', 'spin_off',
  'renaming', 'relocation', 'reform', 'crisis', 'governance_change',
  'platform_shift', 'ipo', 'privatization', 'nationalization',
  'dormancy_start', 'dormancy_end', 'revival', 'reorganization', 'unknown'
);
COMMENT ON TYPE event_type IS
  '組織イベント。Stream I (dormancy / revival) を踏まえた状態遷移を扱う。';

CREATE TYPE dissolution_cause AS ENUM (
  'bankruptcy', 'merger_into_other', 'split_into_others', 'voluntary_wind_down',
  'regulatory_dissolution', 'war_destruction', 'religious_schism',
  'political_purge', 'natural_disaster', 'succession_failure',
  'obsolescence', 'absorption', 'transformation', 'unknown'
);
COMMENT ON TYPE dissolution_cause IS
  '解散・消滅の原因。Stream I の理論 (Stinchcombe newness, Hannan inertia, Carroll-Hannan obsolescence) と歴史事例から。';

-- -------------------------------------------------------------------
-- Relation (組織間関係)
-- -------------------------------------------------------------------

CREATE TABLE relation (
  relation_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_organization_id UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  target_organization_id UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  relation_type        relation_type NOT NULL,
  directionality       relation_directionality NOT NULL DEFAULT 'directed',
  valid_from           DATE,
  valid_from_precision date_precision,
  valid_to             DATE,
  valid_to_precision   date_precision,
  strength             NUMERIC(3,2) CHECK (strength IS NULL OR (strength >= 0.0 AND strength <= 1.0)),
  strength_basis       TEXT,
  relation_attributes  JSONB,
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1,
  CHECK (source_organization_id <> target_organization_id)
);
COMMENT ON TABLE relation IS
  '組織間エッジ。系譜分析で tree → network 化する際の主要構造。';
COMMENT ON COLUMN relation.strength IS
  '関係強度 0.0-1.0。NULL を許容 (根拠ある場合のみ記録)。Roadmap Phase 3 の品質ゲート参照。';
COMMENT ON COLUMN relation.relation_attributes IS
  '関係固有の属性。例: 持株比率, 取引額, 共有プロトコル名, 派遣役員数 等。';

CREATE INDEX idx_relation_source ON relation (source_organization_id);
CREATE INDEX idx_relation_target ON relation (target_organization_id);
CREATE INDEX idx_relation_type ON relation (relation_type);
CREATE INDEX idx_relation_valid_brin ON relation USING BRIN (valid_from, valid_to);
CREATE INDEX idx_relation_attributes_gin ON relation USING GIN (relation_attributes);

-- -------------------------------------------------------------------
-- Event (組織イベント)
-- -------------------------------------------------------------------

CREATE TABLE event (
  event_id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type           event_type NOT NULL,
  event_date           DATE,
  event_date_precision date_precision NOT NULL DEFAULT 'unknown',
  description          TEXT,
  participants         JSONB,
  causes               JSONB,
  outcomes             JSONB,
  location             JSONB,
  dissolution_cause    dissolution_cause,
  vsr_label            TEXT CHECK (vsr_label IN ('variation', 'selection', 'retention', 'struggle', NULL)),
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE event IS
  '組織の状態変化イベント。Aldrich VSR 軸ラベルを横断軸として付与可能。';
COMMENT ON COLUMN event.dissolution_cause IS
  'event_type が dissolution / merger / split のときに使用。Stream I の死亡因子分析の基盤。';
COMMENT ON COLUMN event.vsr_label IS
  'Aldrich (1999) の Variation / Selection / Retention / Struggle ラベル。NULL 許容 (codex7 の横断軸設計)。';

CREATE INDEX idx_event_type ON event (event_type);
CREATE INDEX idx_event_date_brin ON event USING BRIN (event_date);
CREATE INDEX idx_event_dissolution ON event (dissolution_cause) WHERE dissolution_cause IS NOT NULL;

-- -------------------------------------------------------------------
-- EventOrganization (イベント × 組織の M:N、役割つき)
-- -------------------------------------------------------------------

CREATE TABLE event_organization (
  event_organization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id             UUID NOT NULL REFERENCES event(event_id) ON DELETE CASCADE,
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  role                 TEXT NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1,
  UNIQUE (event_id, organization_id, role)
);
COMMENT ON TABLE event_organization IS
  'イベント × 組織。役割は founder / successor / merged_into / spinoff_parent / acquired / dissolved / affected 等。';

CREATE INDEX idx_eo_event ON event_organization (event_id);
CREATE INDEX idx_eo_org ON event_organization (organization_id);
CREATE INDEX idx_eo_role ON event_organization (role);

-- -------------------------------------------------------------------
-- EventRelation (イベントによる関係の開始/終了/強度変化)
-- -------------------------------------------------------------------

CREATE TABLE event_relation (
  event_relation_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_id             UUID NOT NULL REFERENCES event(event_id) ON DELETE CASCADE,
  relation_id          UUID NOT NULL REFERENCES relation(relation_id) ON DELETE CASCADE,
  change_type          TEXT NOT NULL CHECK (change_type IN ('relation_started', 'relation_ended', 'strength_changed', 'type_changed')),
  before_value         JSONB,
  after_value          JSONB,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE event_relation IS
  'イベントが Relation を開始・終了・変更したことを記録。系譜エッジの時間的変化を辿れる。';

CREATE INDEX idx_er_event ON event_relation (event_id);
CREATE INDEX idx_er_relation ON event_relation (relation_id);

-- -------------------------------------------------------------------
-- DormancyRecord (休眠状態)
-- -------------------------------------------------------------------

CREATE TABLE dormancy_record (
  dormancy_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  start_date           DATE,
  start_date_precision date_precision,
  end_date             DATE,
  end_date_precision   date_precision,
  start_event_id       UUID REFERENCES event(event_id),
  end_event_id         UUID REFERENCES event(event_id),
  dormancy_type        TEXT CHECK (dormancy_type IN ('legal_dormant', 'inactive_active_legal', 'cultural_only', 'shell', 'unknown')),
  notes                TEXT,
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE dormancy_record IS
  '組織の休眠期間。Stream I (organizational mortality) — 完全な死と継続の中間状態を扱う。' ||
  '老舗の事業休止、シェルカンパニー、文化的継承のみの状態を区別する。';

CREATE INDEX idx_dormancy_org ON dormancy_record (organization_id);
CREATE INDEX idx_dormancy_dates_brin ON dormancy_record USING BRIN (start_date, end_date);

-- -------------------------------------------------------------------
-- updated_at トリガ
-- -------------------------------------------------------------------

DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['relation','event','event_organization','event_relation','dormancy_record']
  LOOP
    EXECUTE format(
      'CREATE TRIGGER %I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()',
      t || '_set_updated', t
    );
  END LOOP;
END $$;
