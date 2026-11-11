"""Protección de las rutas del panel (RF-13)."""

from functools import wraps

from flask import current_app, g, request

from ..errors import ApiError
from . import tokens


def require_auth(view):
    """Exige ``Authorization: Bearer <token>`` válido; si no, responde 401."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ApiError.unauthorized()
        username = tokens.validate(header[len("Bearer "):], current_app.config["SETTINGS"].jwt_secret)
        if username is None:
            raise ApiError.unauthorized()
        g.analyst = username
        return view(*args, **kwargs)

    return wrapper
