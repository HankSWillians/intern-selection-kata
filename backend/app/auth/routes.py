"""Inicio de sesión del analista (RF-13).

La contraseña del analista viene de ANALYST_PASSWORD y al arrancar se guarda
solo como hash (ver ``create_app``).
"""

import hmac

from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash

from ..errors import ApiError
from . import tokens

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

INVALID_CREDENTIALS = "Usuario o contraseña incorrectos"


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    username = body.get("username") if isinstance(body.get("username"), str) else ""
    password = body.get("password") if isinstance(body.get("password"), str) else ""
    settings = current_app.config["SETTINGS"]

    user_matches = hmac.compare_digest(username.encode(), settings.analyst_username.encode())
    # Se revisa la contraseña aunque el usuario no coincida, para no revelar
    # por el tiempo de respuesta cuál de los dos estaba mal.
    password_matches = bool(password) and check_password_hash(current_app.config["ANALYST_PASSWORD_HASH"], password)
    if not (user_matches and password_matches):
        raise ApiError(401, "Credenciales inválidas", INVALID_CREDENTIALS)

    token, expires_at = tokens.issue(settings.analyst_username, settings.jwt_secret, settings.jwt_ttl_hours)
    return jsonify(token=token, expiresAt=expires_at.isoformat())
