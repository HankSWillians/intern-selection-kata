import sqlite3

from app.config import MIGRATIONS_DIR
from app.db import migrate


def test_migrations_create_the_interns_table(app, settings):
    with sqlite3.connect(settings.db_path) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"interns", "schema_migrations"} <= tables


def test_migrations_run_only_once(app, settings):
    assert migrate(settings.db_path, MIGRATIONS_DIR) == []


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "UP"}


def test_serves_the_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Selección de Practicantes" in response.get_data(as_text=True)
