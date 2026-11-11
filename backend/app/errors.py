"""Errores de la API en formato Problem Details (RFC 9457, RNF-12).

Los errores por campo van en ``errors``, con el mismo texto que muestra el
formulario.
"""

from flask import Flask, current_app, jsonify, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge


class ApiError(Exception):
    def __init__(self, status: int, title: str, detail: str, errors: dict[str, str] | None = None):
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.errors = errors or {}

    @classmethod
    def validation(cls, errors: dict[str, str]) -> "ApiError":
        return cls(400, "Datos inválidos", "Revisa los campos marcados.", errors)

    @classmethod
    def not_found(cls) -> "ApiError":
        return cls(404, "No encontrado", "No existe el practicante solicitado.")

    @classmethod
    def unauthorized(cls, detail: str = "Inicia sesión para continuar.") -> "ApiError":
        return cls(401, "No autorizado", detail)


def problem(status: int, title: str, detail: str, errors: dict[str, str] | None = None):
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail}
    if errors:
        body["errors"] = errors
    response = jsonify(body)
    response.status_code = status
    response.mimetype = "application/problem+json"
    return response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return problem(error.status, error.title, error.detail, error.errors)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(_error: RequestEntityTooLarge):
        max_mb = current_app.config["SETTINGS"].max_cv_mb
        message = f"La hoja de vida no puede pesar más de {max_mb} MB"
        return problem(413, "Archivo muy grande", message, {"cv": message})

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        # Solo la API responde en JSON; las páginas usan las respuestas normales.
        if request.path.startswith("/api/"):
            return problem(error.code or 500, error.name, error.description or error.name)
        return error
