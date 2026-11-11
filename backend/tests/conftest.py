"""Cada prueba usa su propia base SQLite y su propia carpeta de archivos."""

from pathlib import Path

import pytest

from app import create_app
from app.config import Settings
from helpers import login, make_settings


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


@pytest.fixture
def auth(client) -> dict:
    """Encabezado con un token válido del analista."""
    return {"Authorization": f"Bearer {login(client)}"}
