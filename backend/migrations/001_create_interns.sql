-- Practicantes registrados (specs/requerimientos.md, sección 7).
-- Las fechas se guardan como texto ISO 8601 con zona: SQLite no tiene tipo fecha.
CREATE TABLE interns (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name        TEXT    NOT NULL CHECK (length(full_name) BETWEEN 3 AND 100),
    email            TEXT    NOT NULL UNIQUE,
    phone            TEXT    NOT NULL,
    university       TEXT    NOT NULL,
    career           TEXT    NOT NULL,
    semester         INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 12),
    cv_file_name     TEXT    NOT NULL,
    cv_original_name TEXT    NOT NULL,
    data_consent_at  TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'PENDING'
                             CHECK (status IN ('PENDING', 'VIABLE', 'NOT_VIABLE')),
    review_note      TEXT,
    reviewed_at      TEXT,
    created_at       TEXT    NOT NULL
);

CREATE INDEX idx_interns_status ON interns (status);
CREATE INDEX idx_interns_created_at ON interns (created_at);
