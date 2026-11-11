"""Plataforma Básica de Selección de Practicantes: aplicación Flask.

La misma aplicación sirve la API (``/api/v1``) y el frontend estático
(``frontend/``), así el navegador ve un solo origen y no hace falta CORS.
"""

import logging
import mimetypes

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from werkzeug.security import generate_password_hash

from .auth.routes import bp as auth_bp
from .auth.tokens import MIN_SECRET_LENGTH
from .config import FRONTEND_DIR, MIGRATIONS_DIR, REPO_DIR, Settings
from .db import close_db, connect, migrate
from .demo import load_demo_data
from .errors import register_error_handlers
from .interns.routes import bp as interns_bp
from .interns.storage import CvStorage

log = logging.getLogger(__name__)

# En Windows el registro a veces asocia .js a text/plain, y el navegador se
# niega a cargar un módulo con ese tipo. Se fija aquí para cualquier equipo.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")


def create_app(settings: Settings | None = None) -> Flask:
    if settings is None:
        # En local se lee el .env de la raíz del repositorio.
        load_dotenv(REPO_DIR / ".env")
        settings = Settings.from_env()
    _check_secrets(settings)

    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.config["SETTINGS"] = settings
    # Solo el hash: el texto de la contraseña no se vuelve a usar (RF-13).
    app.config["ANALYST_PASSWORD_HASH"] = generate_password_hash(settings.analyst_password)
    # Un poco más que el máximo de la hoja de vida, para que la validación
    # responda con el mensaje de RF-02 y no con un error genérico.
    app.config["MAX_CONTENT_LENGTH"] = (settings.max_cv_mb + 2) * 1024 * 1024
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    migrate(settings.db_path, MIGRATIONS_DIR)
    if settings.demo_data:
        db = connect(settings.db_path)
        try:
            loaded = load_demo_data(db, CvStorage(settings.upload_dir))
            if loaded:
                log.info("DEMO_DATA: se cargaron %s practicantes de ejemplo", loaded)
        finally:
            db.close()

    app.teardown_appcontext(close_db)
    register_error_handlers(app)
    app.register_blueprint(interns_bp)
    app.register_blueprint(auth_bp)

    @app.get("/api/v1/health")
    def health():
        return jsonify(status="UP")

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


def _check_secrets(settings: Settings) -> None:
    """Sin contraseña del analista o con una clave JWT corta, el backend no arranca."""
    if not settings.analyst_username or not settings.analyst_password:
        raise RuntimeError("Faltan ANALYST_USERNAME o ANALYST_PASSWORD en el .env (ver .env.example)")
    if len(settings.jwt_secret) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET debe tener al menos {MIN_SECRET_LENGTH} caracteres (ver .env.example)"
        )
