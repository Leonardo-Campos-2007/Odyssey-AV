-- Esquema inicial do histórico (MODELO-DE-DADOS.md, seção 11).
-- A versão do esquema é gravada em PRAGMA user_version.

BEGIN;

CREATE TABLE IF NOT EXISTS analysis_runs (
    id           TEXT PRIMARY KEY,
    instance_id  TEXT NOT NULL,
    module       TEXT NOT NULL
                 CHECK (module IN ('FILE', 'HASH', 'NETWORK', 'PASSWORD', 'URL', 'PROCESS', 'HISTORY')),
    command      TEXT NOT NULL,
    status       TEXT NOT NULL
                 CHECK (status IN ('RUNNING', 'SUCCESS', 'PARTIAL', 'FAILED', 'INTERRUPTED')),
    started_at   TEXT NOT NULL,
    finished_at  TEXT,
    duration_ms  INTEGER CHECK (duration_ms IS NULL OR duration_ms >= 0),
    summary      TEXT
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id               TEXT PRIMARY KEY,
    analysis_run_id  TEXT NOT NULL REFERENCES analysis_runs (id) ON DELETE CASCADE,
    result_type      TEXT NOT NULL,
    status           TEXT NOT NULL
                     CHECK (status IN ('SUCCESS', 'WARNING', 'ERROR', 'INFO')),
    data             TEXT,
    message          TEXT,
    created_at       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_analysis_runs_module     ON analysis_runs (module);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_started_at ON analysis_runs (started_at);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_status     ON analysis_runs (status);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_instance   ON analysis_runs (instance_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_run_id  ON analysis_results (analysis_run_id);

PRAGMA user_version = 1;

COMMIT;