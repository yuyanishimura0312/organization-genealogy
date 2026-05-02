-- ===================================================================
-- 組織を生命として捉える系譜分析 — DDL v0.2
-- 活動・機能・インパクトの分離
-- v0.1 の上に追加。Activity / Function / ImpactRecord を導入する。
-- ===================================================================
-- 設計判断:
--   1. Activity は「何をしたか」、Function は「何の機能を果たしたか」を分離
--   2. function_type は codex7_function_taxonomy.json の 25 マスタータクソノミーに制約
--      (Miller 20 critical subsystems + Beer VSM 5)
--   3. ImpactRecord は direction を CHECK で制限し価値判断を露見させる
--   4. Activity と Function の orientation (exploration/exploitation) はラベル列で扱う
-- ===================================================================

-- -------------------------------------------------------------------
-- ENUM 拡張
-- -------------------------------------------------------------------

CREATE TYPE activity_orientation AS ENUM (
  'exploration', 'exploitation', 'mixed', 'unspecified'
);
COMMENT ON TYPE activity_orientation IS
  'March (1991) の探索/活用。Function ではなく Activity の側面として扱う (codex7 設計判断)。';

CREATE TYPE impact_direction AS ENUM (
  'positive', 'negative', 'mixed', 'uncertain', 'descriptive'
);
COMMENT ON TYPE impact_direction IS
  'インパクトの方向性。価値判断であることを露見させ、descriptive (記述のみ) を許容。';

CREATE TYPE impact_time_horizon AS ENUM (
  'immediate', 'short_term', 'medium_term', 'long_term', 'intergenerational'
);

-- -------------------------------------------------------------------
-- Function Type マスター (codex7 タクソノミーから生成される参照テーブル)
-- -------------------------------------------------------------------

CREATE TABLE function_type (
  function_type_id     TEXT PRIMARY KEY,
  name_ja              TEXT NOT NULL,
  name_en              TEXT NOT NULL,
  source_framework     TEXT NOT NULL CHECK (source_framework IN ('miller_living_systems', 'beer_vsm', 'compound')),
  miller_subsystem_no  INTEGER,
  vsm_system_no        TEXT,
  parent_function_type_id TEXT REFERENCES function_type(function_type_id),
  definition           TEXT NOT NULL,
  observable_indicators JSONB,
  era_examples         JSONB,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE function_type IS
  'codex7_function_taxonomy.json をロードする参照表。Miller 20 + VSM 5 の 25 機能を主軸とする。';
COMMENT ON COLUMN function_type.era_examples IS
  '時代別の発現例。{"ancient": "...", "medieval": "...", "modern": "...", "contemporary": "...", "digital": "..."}';

-- -------------------------------------------------------------------
-- Activity (何をしたか)
-- -------------------------------------------------------------------

CREATE TABLE activity (
  activity_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  activity_type        TEXT NOT NULL,
  domain               TEXT,
  description          TEXT,
  inputs               JSONB,
  outputs              JSONB,
  scale                JSONB,
  orientation          activity_orientation NOT NULL DEFAULT 'unspecified',
  valid_from           DATE,
  valid_from_precision date_precision,
  valid_to             DATE,
  valid_to_precision   date_precision,
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE activity IS
  '組織が実行した活動・事業領域。生業から DAO のプロトコル運営まで同構造で扱う。';
COMMENT ON COLUMN activity.domain IS
  '生産 / 交換 / 統治 / 儀礼 / 知識 / ケア / 軍事 / 金融 / 教育 / プラットフォーム運営 等';
COMMENT ON COLUMN activity.scale IS
  '規模・頻度・参加者数・取引量。{"unit":"members","value":150,"as_of":"1850"} 等。';

CREATE INDEX idx_activity_org ON activity (organization_id);
CREATE INDEX idx_activity_type ON activity (activity_type);
CREATE INDEX idx_activity_domain ON activity (domain);
CREATE INDEX idx_activity_valid_brin ON activity USING BRIN (valid_from, valid_to);
CREATE INDEX idx_activity_inputs_gin ON activity USING GIN (inputs);
CREATE INDEX idx_activity_outputs_gin ON activity USING GIN (outputs);

-- -------------------------------------------------------------------
-- Function (何の機能を果たしたか)
-- -------------------------------------------------------------------

CREATE TABLE function (
  function_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  function_type_id     TEXT NOT NULL REFERENCES function_type(function_type_id),
  mechanism            JSONB,
  beneficiaries        JSONB,
  dependency           JSONB,
  activity_id          UUID REFERENCES activity(activity_id),
  valid_from           DATE,
  valid_from_precision date_precision,
  valid_to             DATE,
  valid_to_precision   date_precision,
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE function IS
  '活動の背後にある社会的・組織的機能 (codex7 25 マスタータクソノミーから選択)。';
COMMENT ON COLUMN function.mechanism IS
  '機能を実現する具体的仕組み (制度、部門、技術、手続き、役職、ベンダー)。';
COMMENT ON COLUMN function.activity_id IS
  '同じ機能が複数活動に分散することを許容。activity_id を NULL にすれば「機能のみ」記録可能。';

CREATE INDEX idx_function_org ON function (organization_id);
CREATE INDEX idx_function_type ON function (function_type_id);
CREATE INDEX idx_function_activity ON function (activity_id);
CREATE INDEX idx_function_valid_brin ON function USING BRIN (valid_from, valid_to);
CREATE INDEX idx_function_mechanism_gin ON function USING GIN (mechanism);

-- -------------------------------------------------------------------
-- ImpactRecord (組織が外部環境に与えた影響)
-- -------------------------------------------------------------------

CREATE TABLE impact_record (
  impact_id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id      UUID NOT NULL REFERENCES organization(organization_id) ON DELETE CASCADE,
  impact_domain        TEXT NOT NULL,
  metric_name          TEXT NOT NULL,
  metric_value         JSONB NOT NULL,
  direction            impact_direction NOT NULL,
  time_horizon         impact_time_horizon NOT NULL,
  affected_scope       JSONB,
  evaluation_method    TEXT,
  valid_from           DATE,
  valid_from_precision date_precision,
  valid_to             DATE,
  valid_to_precision   date_precision,
  confidence           NUMERIC(3,2) CHECK (confidence >= 0.0 AND confidence <= 1.0),
  claim_id             UUID REFERENCES claim(claim_id),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  record_version       INTEGER NOT NULL DEFAULT 1
);
COMMENT ON TABLE impact_record IS
  '組織が経済・政治・文化・技術・環境・人口・知識に与えた影響を記録する。';
COMMENT ON COLUMN impact_record.impact_domain IS
  '経済 / 政治 / 文化 / 技術 / 環境 / 人口 / 知識 / 健康 / 規範 / 軍事 等';
COMMENT ON COLUMN impact_record.metric_value IS
  '数値・カテゴリ・範囲・推定値を JSONB で。例: {"value":640e6,"unit":"guilders","est_method":"VOC ledger"}';
COMMENT ON COLUMN impact_record.evaluation_method IS
  'comparison / quantitative_estimation / expert_judgment / historical_interpretation 等';

CREATE INDEX idx_impact_org ON impact_record (organization_id);
CREATE INDEX idx_impact_domain ON impact_record (impact_domain);
CREATE INDEX idx_impact_direction ON impact_record (direction);
CREATE INDEX idx_impact_valid_brin ON impact_record USING BRIN (valid_from, valid_to);
CREATE INDEX idx_impact_metric_gin ON impact_record USING GIN (metric_value);

-- -------------------------------------------------------------------
-- updated_at トリガ
-- -------------------------------------------------------------------

DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['function_type','activity','function','impact_record']
  LOOP
    EXECUTE format(
      'CREATE TRIGGER %I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at()',
      t || '_set_updated', t
    );
  END LOOP;
END $$;
