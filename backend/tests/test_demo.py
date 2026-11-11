"""Datos de demostración: RF-19."""

from app import create_app
from helpers import make_settings


def test_rf19_demo_data_loads_once(tmp_path):
    settings = make_settings(tmp_path, demo_data=True)
    client = create_app(settings).test_client()
    token = client.post("/api/v1/auth/login", json={"username": "analista", "password": "clave-de-pruebas"}).get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/interns/summary", headers=headers).get_json() == {
        "total": 4, "pending": 2, "viable": 1, "notViable": 1,
    }
    # Al reiniciar no se duplican.
    create_app(settings)
    assert client.get("/api/v1/interns/summary", headers=headers).get_json()["total"] == 4
    # Las hojas de vida de ejemplo se pueden descargar.
    first = client.get("/api/v1/interns", headers=headers).get_json()[0]
    assert client.get(f"/api/v1/interns/{first['id']}/cv", headers=headers).data.startswith(b"%PDF-")
