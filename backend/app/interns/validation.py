"""Validaciones del registro (RF-01 a RF-04, RF-12, RF-15) con los mensajes de
la tabla 3.1 de la spec. Son las mismas que hace el navegador en
``frontend/js/validation.js``.
"""

import re
from dataclasses import dataclass

from werkzeug.datastructures import FileStorage

from ..catalog import CAREERS, OTHER, UNIVERSITIES

EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
CO_MOBILE = re.compile(r"^3\d{9}$")
PDF_SIGNATURE = b"%PDF-"


@dataclass(frozen=True)
class Registration:
    full_name: str
    email: str
    phone: str
    university: str
    career: str
    semester: int
    cv: FileStorage


def _is_name(value: str) -> bool:
    """Letras de cualquier idioma (tildes, ñ), espacios, apóstrofo y guion; empieza con letra."""
    return value[0].isalpha() and all(c.isalpha() or c in " '-" for c in value)


def normalize_spaces(value: str | None) -> str:
    return " ".join((value or "").split())


def normalize_phone(value: str | None) -> str:
    """Acepta espacios, guiones y el indicativo +57 al escribir; deja los 10 dígitos."""
    digits = re.sub(r"[\s\-()]", "", (value or "").strip())
    return digits[3:] if digits.startswith("+57") else digits


def validate(form, files, max_cv_mb: int) -> tuple[Registration | None, dict[str, str]]:
    """Devuelve los datos normalizados o un diccionario campo → mensaje con todos los errores."""
    errors: dict[str, str] = {}

    full_name = normalize_spaces(form.get("fullName"))
    if not full_name:
        errors["fullName"] = "Escribe tu nombre completo"
    elif not 3 <= len(full_name) <= 100:
        errors["fullName"] = "El nombre debe tener entre 3 y 100 caracteres"
    elif not _is_name(full_name):
        errors["fullName"] = "El nombre solo puede tener letras"

    email = (form.get("email") or "").strip().lower()
    if not email:
        errors["email"] = "Escribe tu correo"
    elif len(email) > 254 or not EMAIL.match(email):
        errors["email"] = "Escribe un correo válido"

    phone = normalize_phone(form.get("phone"))
    if not (form.get("phone") or "").strip():
        errors["phone"] = "Escribe tu celular"
    elif not CO_MOBILE.match(phone):
        errors["phone"] = "Escribe un celular colombiano de 10 dígitos que empiece por 3"

    university = _choice(form, "university", "universityOther", UNIVERSITIES,
                         "Elige tu universidad", "Escribe el nombre de tu universidad", errors)
    career = _choice(form, "career", "careerOther", CAREERS,
                     "Elige tu carrera", "Escribe el nombre de tu carrera", errors)

    semester = None
    raw_semester = (form.get("semester") or "").strip()
    if not raw_semester:
        errors["semester"] = "Elige tu semestre"
    else:
        try:
            semester = int(raw_semester)
        except ValueError:
            semester = None
        if semester is None or not 1 <= semester <= 12:
            errors["semester"] = "El semestre debe estar entre 1 y 12"

    cv = files.get("cv")
    cv_error = _cv_error(cv, max_cv_mb)
    if cv_error:
        errors["cv"] = cv_error

    if (form.get("dataConsent") or "").strip().lower() != "true":
        errors["dataConsent"] = "Debes aceptar el tratamiento de tus datos personales"

    if errors:
        return None, errors
    return Registration(full_name, email, "+57" + phone, university, career, semester, cv), {}


def _choice(form, field, other_field, options, missing, other_message, errors) -> str | None:
    value = (form.get(field) or "").strip()
    if not value or value not in options:
        errors[field] = missing
        return None
    if value != OTHER:
        return value
    written = normalize_spaces(form.get(other_field))
    if not 3 <= len(written) <= 100:
        errors[other_field] = other_message
        return None
    return written


def _cv_error(cv: FileStorage | None, max_cv_mb: int) -> str | None:
    if cv is None or not cv.filename:
        return "Adjunta tu hoja de vida"
    size = _size(cv)
    if size == 0:
        return "Adjunta tu hoja de vida"
    # RF-02: además de la extensión, el contenido debe empezar con %PDF-.
    if not cv.filename.lower().endswith(".pdf") or not _has_pdf_signature(cv):
        return "Solo se permiten archivos PDF"
    if size > max_cv_mb * 1024 * 1024:
        return f"La hoja de vida no puede pesar más de {max_cv_mb} MB"
    return None


def _size(cv: FileStorage) -> int:
    stream = cv.stream
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)
    return size


def _has_pdf_signature(cv: FileStorage) -> bool:
    head = cv.stream.read(len(PDF_SIGNATURE))
    cv.stream.seek(0)
    return head == PDF_SIGNATURE
