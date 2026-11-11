"""Acceso a la tabla ``interns`` con SQL directo. Las fechas se guardan como
texto ISO 8601 con zona, porque SQLite no tiene tipo fecha."""

import sqlite3
from datetime import datetime

STATUSES = ("PENDING", "VIABLE", "NOT_VIABLE")

COLUMNS = """id, full_name, email, phone, university, career, semester, cv_file_name,
             cv_original_name, data_consent_at, status, review_note, reviewed_at, created_at"""


def insert(db: sqlite3.Connection, intern: dict) -> int:
    cursor = db.execute(
        """INSERT INTO interns (full_name, email, phone, university, career, semester,
                                cv_file_name, cv_original_name, data_consent_at, status, created_at)
           VALUES (:full_name, :email, :phone, :university, :career, :semester,
                   :cv_file_name, :cv_original_name, :data_consent_at, 'PENDING', :created_at)""",
        intern,
    )
    db.commit()
    return cursor.lastrowid


def exists_by_email(db: sqlite3.Connection, email: str) -> bool:
    return db.execute("SELECT 1 FROM interns WHERE email = ?", (email,)).fetchone() is not None


def find_by_id(db: sqlite3.Connection, intern_id: int) -> sqlite3.Row | None:
    return db.execute(f"SELECT {COLUMNS} FROM interns WHERE id = ?", (intern_id,)).fetchone()


def find_all(db: sqlite3.Connection, status: str | None = None) -> list[sqlite3.Row]:
    """Los más recientes primero (RF-06); ``status`` vacío = todos."""
    if status is None:
        return db.execute(f"SELECT {COLUMNS} FROM interns ORDER BY created_at DESC, id DESC").fetchall()
    return db.execute(
        f"SELECT {COLUMNS} FROM interns WHERE status = ? ORDER BY created_at DESC, id DESC", (status,)
    ).fetchall()


def count_by_status(db: sqlite3.Connection) -> dict[str, int]:
    counts = {status: 0 for status in STATUSES}
    for row in db.execute("SELECT status, count(*) AS total FROM interns GROUP BY status"):
        counts[row["status"]] = row["total"]
    return counts


def count(db: sqlite3.Connection) -> int:
    return db.execute("SELECT count(*) FROM interns").fetchone()[0]


def update_decision(db: sqlite3.Connection, intern_id: int, status: str, note: str | None,
                    reviewed_at: datetime) -> None:
    db.execute(
        "UPDATE interns SET status = ?, review_note = ?, reviewed_at = ? WHERE id = ?",
        (status, note, reviewed_at.isoformat(), intern_id),
    )
    db.commit()


def to_json(row: sqlite3.Row) -> dict:
    """Practicante tal como lo ve el panel (RF-07). No expone el nombre del archivo en el servidor."""
    return {
        "id": row["id"],
        "fullName": row["full_name"],
        "email": row["email"],
        "phone": row["phone"],
        "university": row["university"],
        "career": row["career"],
        "semester": row["semester"],
        "status": row["status"],
        "reviewNote": row["review_note"],
        "reviewedAt": row["reviewed_at"],
        "dataConsentAt": row["data_consent_at"],
        "createdAt": row["created_at"],
    }
