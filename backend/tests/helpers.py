"""Ayudas compartidas por las pruebas de la API y del navegador."""

import io
from pathlib import Path

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


def valid_fields(email: str) -> dict:
    """Datos válidos del formulario; cada prueba cambia lo que necesita."""
    return {
        "fullName": "Laura Gómez",
        "email": email,
        "phone": "300 123 4567",
        "university": "Universidad Nacional de Colombia",
        "career": "Ingeniería de Sistemas",
        "semester": "8",
        "dataConsent": "true",
    }


def pdf(name: str = "hoja-de-vida.pdf", size: int = 200 * 1024) -> tuple[io.BytesIO, str]:
    header = b"%PDF-1.4\n"
    return io.BytesIO(header + b"0" * max(size - len(header), 0)), name


def register(client, fields: dict, cv=None):
    data = dict(fields)
    if cv is not None:
        data["cv"] = cv
    return client.post("/api/v1/interns", data=data, content_type="multipart/form-data")


def register_valid(client, email: str) -> int:
    response = register(client, valid_fields(email), pdf())
    assert response.status_code == 201, response.get_json()
    return response.get_json()["id"]


def login(client) -> str:
    response = client.post("/api/v1/auth/login", json={"username": ANALYST, "password": PASSWORD})
    assert response.status_code == 200
    return response.get_json()["token"]
