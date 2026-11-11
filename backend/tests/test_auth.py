"""Acceso del analista: RF-13."""

import pytest

from app import create_app
from helpers import make_settings, register_valid


def test_login_returns_a_token_that_opens_the_panel(client, auth):
    assert client.get("/api/v1/interns", headers=auth).status_code == 200


def test_cp15_wrong_password_does_not_say_which_field_failed(client):
    for body in ({"username": "analista", "password": "otra"}, {"username": "otro", "password": "clave-de-pruebas"}):
        response = client.post("/api/v1/auth/login", json=body)
        assert response.status_code == 401
        assert response.get_json()["detail"] == "Usuario o contraseña incorrectos"


def test_cp25_tampered_token_is_rejected(client, auth):
    token = auth["Authorization"].removeprefix("Bearer ")
    tampered = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    assert client.get("/api/v1/interns", headers={"Authorization": f"Bearer {tampered}"}).status_code == 401


def test_expired_token_is_rejected(tmp_path):
    app = create_app(make_settings(tmp_path, jwt_ttl_hours=-1))
    client = app.test_client()
    token = client.post("/api/v1/auth/login", json={"username": "analista", "password": "clave-de-pruebas"}).get_json()["token"]
    assert client.get("/api/v1/interns", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_registration_is_public(client):
    register_valid(client, "publico@correo.com")


@pytest.mark.parametrize("overrides", [{"analyst_password": ""}, {"jwt_secret": "corta"}])
def test_app_does_not_start_without_secrets(tmp_path, overrides):
    with pytest.raises(RuntimeError):
        create_app(make_settings(tmp_path, **overrides))
