-- ===================================================================
-- 組織を生命として捉える系譜分析 — SQLite サンドボックス v0.1+v0.2+v0.3
-- 本番 PostgreSQL DDL (research/codex4_ddl_v0*.sql) の SQLite 移植版
-- ===================================================================
-- 互換性メモ:
--   - UUID は TEXT で扱う (uuid 関数は Python 側で uuid4().hex)
--   - JSONB は TEXT (json1 拡張で json_extract 等が使える)
--   - ENUM は CHECK constraint で代替
--   - vector(384) は BLOB (本番移行時に pgvector へ)
--   - daterange は TEXT (ISO 8601 の "from..to") で代替
--   - BRIN/GIN/HNSW はインデックスなしまたは btree
--   - 5 値 claim_value_kind / Stream J 教訓は厳格に維持
-- ===================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- -------------------------------------------------------------------
-- v0.1: source / claim / organization_form / organization
-- -------------------------------------------------------------------

CREATE TABLE source (
  source_id            TEXT PRIMARY KEY,
  source_type          TEXT NOT NULL CHECK (source_type IN
    ('primary_text','secondary_literature','dataset','interview','archive','artifact','onchain','web','oral_history','ethnography')),
  title                TEXT NOT NULL,
  authors              TEXT,    -- JSON array
  publication_date     TEXT,    -- ISO 8601
  publisher            TEXT,
  locator              TEXT,    -- JSON
  accessed_at          TEXT,    -- ISO 8601
  reliability_score    REAL CHECK (reliability_score IS NULL OR (reliability_score >= 0.0 AND reliability_score <= 1.0)),
  reliability_basis    TEXT,
  bias_notes           TEXT,
  license              TEXT,
  redistribution       TEXT CHECK (redistribution IN
    ('public_redistributable','attribution_required','noncommercial','private','restricted')),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_source_type ON source(source_type);
CREATE INDEX idx_source_redist ON source(redistribution);

CREATE TABLE claim (
  claim_id             TEXT PRIMARY KEY,
  entity_type          TEXT NOT NULL,
  entity_id            TEXT NOT NULL,
  field_path           TEXT,
  value_kind           TEXT NOT NULL CHECK (value_kind IN
    ('present','absent','partial','unknown','inapplicable')),
  claim_value          TEXT,    -- JSON
  source_id            TEXT REFERENCES source(source_id) ON DELETE RESTRICT,
  confidence           REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
  interpretation_note  TEXT,
  recorded_by          TEXT NOT NULL,
  recorded_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  superseded_by        TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_claim_entity ON claim(entity_type, entity_id);
CREATE INDEX idx_claim_source ON claim(source_id);

CREATE TABLE organization_form (
  form_id              TEXT PRIMARY KEY,
  taxonomy_name        TEXT NOT NULL,
  form_code            TEXT NOT NULL,
  label                TEXT NOT NULL,
  parent_form_id       TEXT REFERENCES organization_form(form_id),
  definition           TEXT,
  criteria             TEXT,    -- JSON
  valid_period_from    TEXT,
  valid_period_to      TEXT,
  notes                TEXT,
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1,
  UNIQUE (taxonomy_name, form_code)
);
CREATE INDEX idx_form_taxonomy ON organization_form(taxonomy_name);

CREATE TABLE organization (
  organization_id      TEXT PRIMARY KEY,
  canonical_name       TEXT NOT NULL,
  alternate_names      TEXT,    -- JSON array of {name, lang}
  description          TEXT,
  primary_form_id      TEXT REFERENCES organization_form(form_id),
  geo_scope            TEXT,    -- JSON
  start_date           TEXT,
  start_date_precision TEXT CHECK (start_date_precision IN
    ('exact','year','decade','century','period','before','after','unknown') OR start_date_precision IS NULL),
  end_date             TEXT,
  end_date_precision   TEXT CHECK (end_date_precision IN
    ('exact','year','decade','century','period','before','after','unknown') OR end_date_precision IS NULL),
  status               TEXT NOT NULL DEFAULT 'unknown' CHECK (status IN
    ('active','dormant','transformed','merged','split','extinct','unknown')),
  attributes           TEXT,    -- JSON
  embedding            BLOB,    -- pgvector 移行時に変換
  external_ids         TEXT,    -- JSON {wikidata, gleif_lei, ror, edinet, ...}
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_org_form ON organization(primary_form_id);
CREATE INDEX idx_org_status ON organization(status);
CREATE INDEX idx_org_dates ON organization(start_date, end_date);

CREATE TABLE organization_form_assignment (
  assignment_id        TEXT PRIMARY KEY,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  form_id              TEXT NOT NULL REFERENCES organization_form(form_id) ON DELETE RESTRICT,
  valid_from           TEXT,
  valid_from_precision TEXT,
  valid_to             TEXT,
  valid_to_precision   TEXT,
  is_primary           INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0,1)),
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_ofa_org ON organization_form_assignment(organization_id);
CREATE INDEX idx_ofa_form ON organization_form_assignment(form_id);

-- -------------------------------------------------------------------
-- v0.2: function_type / activity / function_record / impact_record
-- -------------------------------------------------------------------

CREATE TABLE function_type (
  function_type_id     TEXT PRIMARY KEY,
  name_ja              TEXT NOT NULL,
  name_en              TEXT NOT NULL,
  source_framework     TEXT NOT NULL CHECK (source_framework IN
    ('miller_living_systems','beer_vsm','compound')),
  miller_subsystem_no  INTEGER,
  vsm_system_no        TEXT,
  parent_function_type_id TEXT REFERENCES function_type(function_type_id),
  definition           TEXT NOT NULL,
  observable_indicators TEXT,    -- JSON
  era_examples         TEXT,    -- JSON
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE activity (
  activity_id          TEXT PRIMARY KEY,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  activity_type        TEXT NOT NULL,
  domain               TEXT,
  description          TEXT,
  inputs               TEXT,    -- JSON
  outputs              TEXT,    -- JSON
  scale                TEXT,    -- JSON
  orientation          TEXT NOT NULL DEFAULT 'unspecified' CHECK (orientation IN
    ('exploration','exploitation','mixed','unspecified')),
  valid_from           TEXT,
  valid_from_precision TEXT,
  valid_to             TEXT,
  valid_to_precision   TEXT,
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_activity_org ON activity(organization_id);
CREATE INDEX idx_activity_type ON activity(activity_type);

-- function は SQLite 予約語ではないが、PG では予約語に近い。テーブル名 function_record に変更。
CREATE TABLE function_record (
  function_id          TEXT PRIMARY KEY,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  function_type_id     TEXT NOT NULL REFERENCES function_type(function_type_id),
  mechanism            TEXT,    -- JSON
  beneficiaries        TEXT,    -- JSON
  dependency           TEXT,    -- JSON
  activity_id          TEXT REFERENCES activity(activity_id),
  valid_from           TEXT,
  valid_from_precision TEXT,
  valid_to             TEXT,
  valid_to_precision   TEXT,
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_fr_org ON function_record(organization_id);
CREATE INDEX idx_fr_type ON function_record(function_type_id);

CREATE TABLE impact_record (
  impact_id            TEXT PRIMARY KEY,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  impact_domain        TEXT NOT NULL,
  metric_name          TEXT NOT NULL,
  metric_value         TEXT NOT NULL,    -- JSON
  direction            TEXT NOT NULL CHECK (direction IN
    ('positive','negative','mixed','uncertain','descriptive')),
  time_horizon         TEXT NOT NULL CHECK (time_horizon IN
    ('immediate','short_term','medium_term','long_term','intergenerational')),
  affected_scope       TEXT,    -- JSON
  evaluation_method    TEXT,
  valid_from           TEXT,
  valid_from_precision TEXT,
  valid_to             TEXT,
  valid_to_precision   TEXT,
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_impact_org ON impact_record(organization_id);
CREATE INDEX idx_impact_domain ON impact_record(impact_domain);

-- -------------------------------------------------------------------
-- v0.3: relation / event / event_organization / event_relation / dormancy_record
-- -------------------------------------------------------------------

CREATE TABLE relation (
  relation_id          TEXT PRIMARY KEY,
  source_organization_id TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  target_organization_id TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  relation_type        TEXT NOT NULL CHECK (relation_type IN
    ('alliance','competition','control','subsidiary','partnership',
     'membership','succession','spin_off','merger','acquisition',
     'trade','funding','shareholding',
     'knowledge_transfer','mimetic_isomorphism','normative_pressure','coercive_pressure',
     'protocol_dependency','supply_chain','interlocking_directorate',
     'patronage','rivalry','schism','unknown')),
  directionality       TEXT NOT NULL DEFAULT 'directed' CHECK (directionality IN
    ('directed','undirected','bidirectional')),
  valid_from           TEXT,
  valid_from_precision TEXT,
  valid_to             TEXT,
  valid_to_precision   TEXT,
  strength             REAL CHECK (strength IS NULL OR (strength >= 0.0 AND strength <= 1.0)),
  strength_basis       TEXT,
  relation_attributes  TEXT,    -- JSON
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1,
  CHECK (source_organization_id <> target_organization_id)
);
CREATE INDEX idx_rel_source ON relation(source_organization_id);
CREATE INDEX idx_rel_target ON relation(target_organization_id);
CREATE INDEX idx_rel_type ON relation(relation_type);

CREATE TABLE event (
  event_id             TEXT PRIMARY KEY,
  event_type           TEXT NOT NULL CHECK (event_type IN
    ('founding','dissolution','merger','acquisition','split','spin_off',
     'renaming','relocation','reform','crisis','governance_change',
     'platform_shift','ipo','privatization','nationalization',
     'dormancy_start','dormancy_end','revival','reorganization','unknown')),
  event_date           TEXT,
  event_date_precision TEXT NOT NULL DEFAULT 'unknown',
  description          TEXT,
  participants         TEXT,    -- JSON
  causes               TEXT,    -- JSON
  outcomes             TEXT,    -- JSON
  location             TEXT,    -- JSON
  dissolution_cause    TEXT CHECK (dissolution_cause IS NULL OR dissolution_cause IN
    ('bankruptcy','merger_into_other','split_into_others','voluntary_wind_down',
     'regulatory_dissolution','war_destruction','religious_schism',
     'political_purge','natural_disaster','succession_failure',
     'obsolescence','absorption','transformation','unknown')),
  vsr_label            TEXT CHECK (vsr_label IS NULL OR vsr_label IN
    ('variation','selection','retention','struggle')),
  confidence           REAL CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_event_type ON event(event_type);
CREATE INDEX idx_event_date ON event(event_date);

CREATE TABLE event_organization (
  event_organization_id TEXT PRIMARY KEY,
  event_id             TEXT NOT NULL REFERENCES event(event_id) ON DELETE CASCADE,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  role                 TEXT NOT NULL,
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1,
  UNIQUE (event_id, organization_id, role)
);

CREATE TABLE event_relation (
  event_relation_id    TEXT PRIMARY KEY,
  event_id             TEXT NOT NULL REFERENCES event(event_id) ON DELETE CASCADE,
  relation_id          TEXT NOT NULL REFERENCES relation(relation_id) ON DELETE CASCADE,
  change_type          TEXT NOT NULL CHECK (change_type IN
    ('relation_started','relation_ended','strength_changed','type_changed')),
  before_value         TEXT,
  after_value          TEXT,
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE dormancy_record (
  dormancy_id          TEXT PRIMARY KEY,
  organization_id      TEXT NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  start_date           TEXT,
  start_date_precision TEXT,
  end_date             TEXT,
  end_date_precision   TEXT,
  start_event_id       TEXT REFERENCES event(event_id),
  end_event_id         TEXT REFERENCES event(event_id),
  dormancy_type        TEXT CHECK (dormancy_type IS NULL OR dormancy_type IN
    ('legal_dormant','inactive_active_legal','cultural_only','shell','unknown')),
  notes                TEXT,
  claim_id             TEXT REFERENCES claim(claim_id),
  created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_version       INTEGER NOT NULL DEFAULT 1
);

-- -------------------------------------------------------------------
-- updated_at トリガ
-- -------------------------------------------------------------------

-- SQLite では FOR EACH ROW + UPDATE OF が必要
CREATE TRIGGER trg_source_updated AFTER UPDATE ON source FOR EACH ROW BEGIN
  UPDATE source SET updated_at = CURRENT_TIMESTAMP, record_version = OLD.record_version + 1 WHERE source_id = OLD.source_id;
END;
CREATE TRIGGER trg_claim_updated AFTER UPDATE ON claim FOR EACH ROW BEGIN
  UPDATE claim SET updated_at = CURRENT_TIMESTAMP, record_version = OLD.record_version + 1 WHERE claim_id = OLD.claim_id;
END;
CREATE TRIGGER trg_org_updated AFTER UPDATE ON organization FOR EACH ROW BEGIN
  UPDATE organization SET updated_at = CURRENT_TIMESTAMP, record_version = OLD.record_version + 1 WHERE organization_id = OLD.organization_id;
END;
