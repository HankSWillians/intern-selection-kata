"""Hora de Bogotá. Colombia no tiene horario de verano, así que basta un
desplazamiento fijo de UTC−5 (y no hace falta el paquete tzdata en Windows)."""

from datetime import datetime, timedelta, timezone

BOGOTA = timezone(timedelta(hours=-5), "America/Bogota")


def now() -> datetime:
    return datetime.now(BOGOTA)
