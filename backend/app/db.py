"""Conexión a SQLite y migraciones numeradas (RNF-02).

Cada archivo ``migrations/NNN_descripcion.sql`` se aplica una sola vez, en
orden, y queda registrado en la tabla ``schema_migrations``, como hace Flyway
en Kronos. Nunca se edita una migración ya aplicada: se agrega una nueva.
"""

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app, g

MIGRATION_NAME = re.compile(r"^(\d{3})_[a-z0-9_]+\.sql$")


def connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> sqlite3.Connection:
    """Una conexión por petición; se cierra sola al terminar (ver ``close_db``)."""
    if "db" not in g:
        g.db = connect(current_app.config["SETTINGS"].db_path)
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def migrate(db_path: Path, migrations_dir: Path) -> list[str]:
    """Aplica las migraciones pendientes y devuelve las que aplicó."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in migrations_dir.glob("*.sql"))
    for path in files:
        if not MIGRATION_NAME.match(path.name):
            raise RuntimeError(f"Nombre de migración inválido: {path.name} (usa NNN_descripcion.sql)")

    applied_now: list[str] = []
    connection = connect(db_path)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version TEXT PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        done = {row["version"] for row in connection.execute("SELECT version FROM schema_migrations")}
        for path in files:
            version = path.name[:3]
            if version in done:
                continue
            script = path.read_text(encoding="utf-8")
            # executescript hace COMMIT antes de empezar; el BEGIN explícito hace
            # que la migración y su registro entren juntos o no entre ninguno.
            connection.executescript(
                "BEGIN;\n"
                + script
                + "\nINSERT INTO schema_migrations (version, name, applied_at) VALUES ("
                + f"'{version}', '{path.name}', '{datetime.now(timezone.utc).isoformat()}');\n"
                + "COMMIT;"
            )
            applied_now.append(path.name)
    finally:
        connection.close()
    return applied_now
