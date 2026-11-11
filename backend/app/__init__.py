"""Plataforma Básica de Selección de Practicantes: aplicación Flask.

La misma aplicación sirve la API (``/api/v1``) y el frontend estático
(``frontend/``), así el navegador ve un solo origen y no hace falta CORS.
"""

from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

from .config import FRONTEND_DIR, MIGRATIONS_DIR, REPO_DIR, Settings
from .db import close_db, migrate


def create_app(settings: Settings | None = None) -> Flask:
    if settings is None:
        # En local se lee el .env de la raíz del repositorio.
        load_dotenv(REPO_DIR / ".env")
        settings = Settings.from_env()

    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.config["SETTINGS"] = settings
    # Un poco más que el máximo de la hoja de vida, para que la validación
    # responda con el mensaje de RF-02 y no con un error genérico.
    app.config["MAX_CONTENT_LENGTH"] = (settings.max_cv_mb + 2) * 1024 * 1024
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    migrate(settings.db_path, MIGRATIONS_DIR)
    app.teardown_appcontext(close_db)

    @app.get("/api/v1/health")
    def health():
        return jsonify(status="UP")

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app
