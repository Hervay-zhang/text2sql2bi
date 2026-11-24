CREATE TABLE bi_query_history (
  id BIGSERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  sql TEXT NOT NULL,
  chart_type TEXT NOT NULL,
  duration_ms INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE bi_dashboard (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  definition JSONB NOT NULL DEFAULT '{}'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX bi_query_history_created_at_idx
  ON bi_query_history (created_at DESC);
