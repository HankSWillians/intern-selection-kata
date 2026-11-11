"""Reglas del registro y de la revisión de practicantes."""

import sqlite3
from pathlib import PurePath

from .. import clock
from ..errors import ApiError
from . import repository
from .storage import CvStorage
from .validation import validate

MAX_NOTE_LENGTH = 500
DUPLICATE_EMAIL = "Ya existe un registro con este correo"


def register(db: sqlite3.Connection, storage: CvStorage, form, files, max_cv_mb: int) -> sqlite3.Row:
    """RF-09, RF-12, RF-15: valida, guarda el PDF y crea el registro en estado Pendiente."""
    data, errors = validate(form, files, max_cv_mb)
    if errors:
        raise ApiError.validation(errors)
    if repository.exists_by_email(db, data.email):
        raise _duplicate_email()

    file_name = storage.store(data.cv)
    now = clock.now().isoformat()
    try:
        intern_id = repository.insert(db, {
            "full_name": data.full_name,
            "email": data.email,
            "phone": data.phone,
            "university": data.university,
            "career": data.career,
            "semester": data.semester,
            "cv_file_name": file_name,
            "cv_original_name": _original_name(data.cv.filename),
            "data_consent_at": now,
            "created_at": now,
        })
    except sqlite3.IntegrityError:
        # Dos registros con el mismo correo casi al mismo tiempo: gana el primero.
        storage.delete(file_name)
        raise _duplicate_email()
    except Exception:
        storage.delete(file_name)
        raise
    return repository.find_by_id(db, intern_id)


def get(db: sqlite3.Connection, intern_id: int) -> sqlite3.Row:
    row = repository.find_by_id(db, intern_id)
    if row is None:
        raise ApiError.not_found()
    return row


def parse_filter(raw: str | None) -> str | None:
    """Filtro de la lista (RF-16): vacío = todos."""
    if raw is None or not raw.strip():
        return None
    status = raw.strip().upper()
    if status not in repository.STATUSES:
        raise ApiError.validation({"status": "Estado inválido"})
    return status


def decide(db: sqlite3.Connection, intern_id: int, raw_status, raw_note) -> sqlite3.Row:
    """RF-11, RF-17, RF-18: solo Viable o No viable; nunca se vuelve a Pendiente.

    La observación nueva reemplaza a la anterior, y vacía la borra.
    """
    status = raw_status.strip().upper() if isinstance(raw_status, str) else None
    if status not in repository.STATUSES:
        raise ApiError.validation({"status": "Estado inválido: usa VIABLE o NOT_VIABLE"})
    if status == "PENDING":
        raise ApiError.validation({"status": "Un practicante revisado no puede volver a Pendiente"})

    note = raw_note.strip() if isinstance(raw_note, str) and raw_note.strip() else None
    if note is not None and len(note) > MAX_NOTE_LENGTH:
        raise ApiError.validation(
            {"note": f"La observación no puede tener más de {MAX_NOTE_LENGTH} caracteres"}
        )

    get(db, intern_id)
    repository.update_decision(db, intern_id, status, note, clock.now())
    return get(db, intern_id)


def _duplicate_email() -> ApiError:
    return ApiError(409, "Correo duplicado", DUPLICATE_EMAIL, {"email": DUPLICATE_EMAIL})


def _original_name(name: str | None) -> str:
    """Solo informativo: sin rutas y recortado."""
    base = PurePath((name or "").replace("\\", "/")).name
    return (base or "hoja-de-vida.pdf")[:200]
