"""SQLite schema definitions for the cell count database."""

POPULATIONS = (
    "b_cell",
    "cd8_t_cell",
    "cd4_t_cell",
    "nk_cell",
    "monocyte",
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    condition TEXT,
    age INTEGER,
    sex TEXT,
    treatment TEXT,
    response TEXT
);

CREATE TABLE IF NOT EXISTS samples (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    sample_type TEXT NOT NULL,
    time_from_treatment_start INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
);

CREATE TABLE IF NOT EXISTS cell_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_id TEXT NOT NULL,
    population TEXT NOT NULL,
    count INTEGER NOT NULL,
    FOREIGN KEY (sample_id) REFERENCES samples (sample_id),
    UNIQUE (sample_id, population)
);

CREATE INDEX IF NOT EXISTS idx_samples_subject_id
    ON samples (subject_id);

CREATE INDEX IF NOT EXISTS idx_samples_type_time
    ON samples (sample_type, time_from_treatment_start);

CREATE INDEX IF NOT EXISTS idx_cell_counts_sample_id
    ON cell_counts (sample_id);

CREATE INDEX IF NOT EXISTS idx_subjects_condition_treatment
    ON subjects (condition, treatment);
"""


def init_schema(conn) -> None:
    """Create all tables and indexes in the given SQLite connection."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()
