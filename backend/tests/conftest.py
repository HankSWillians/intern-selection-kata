"""Cada prueba usa su propia base SQLite y su propia carpeta de archivos."""

from pathlib import Path

import pytest

from app import create_app
from app.config import Settings

ANALYST = "analista"
PASSWORD = "clave-de-pruebas"


def make_settings(tmp_path: Path, **overrides) -> Settings:
    values = dict(
        db_path=tmp_path / "data" / "test.db",
        upload_dir=tmp_path / "uploads",
        max_cv_mb=5,
        analyst_username=ANALYST,
        analyst_password=PASSWORD,
        jwt_secret="clave-jwt-de-pruebas-solo-para-tests-0123456789",
        jwt_ttl_hours=8,
        demo_data=False,
    )
    values.update(overrides)
    return Settings(**values)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return make_settings(tmp_path)


@pytest.fixture
def app(settings: Settings):
    app = create_app(settings)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
