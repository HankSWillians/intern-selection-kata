"""Emisión y validación de los JWT del analista (HS256, RF-13)."""

from datetime import datetime, timedelta, timezone

import jwt

MIN_SECRET_LENGTH = 32


def issue(username: str, secret: str, ttl_hours: int) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=ttl_hours)
    token = jwt.encode({"sub": username, "iat": now, "exp": expires_at}, secret, algorithm="HS256")
    return token, expires_at


def validate(token: str, secret: str) -> str | None:
    """Devuelve el usuario del token, o ``None`` si la firma no coincide o ya venció."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["sub", "exp"]})
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
