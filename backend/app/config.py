"""Configuración desde variables de entorno (ver .env.example en la raíz)."""

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent
FRONTEND_DIR = REPO_DIR / "frontend"
MIGRATIONS_DIR = BACKEND_DIR / "migrations"


def _path(value: str) -> Path:
    """Las rutas relativas del .env se toman desde backend/, venga de donde venga el comando."""
    path = Path(value)
    return path if path.is_absolute() else (BACKEND_DIR / path).resolve()


def _bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "si", "sí"}


@dataclass(frozen=True)
class Settings:
    db_path: Path
    upload_dir: Path
    max_cv_mb: int
    analyst_username: str
    analyst_password: str
    jwt_secret: str
    jwt_ttl_hours: int
    demo_data: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=_path(os.getenv("DB_PATH", "./var/data/intern-selection.db")),
            upload_dir=_path(os.getenv("UPLOAD_DIR", "./var/uploads")),
            max_cv_mb=int(os.getenv("MAX_CV_SIZE_MB", "5")),
            analyst_username=os.getenv("ANALYST_USERNAME", "analista"),
            analyst_password=os.getenv("ANALYST_PASSWORD", ""),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            jwt_ttl_hours=int(os.getenv("JWT_TTL_HOURS", "8")),
            demo_data=_bool(os.getenv("DEMO_DATA")),
        )
