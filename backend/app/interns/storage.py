"""Hojas de vida en la carpeta del servidor (RNF-03), con nombre generado y
nunca con el nombre original (RF-02, RNF-06)."""

import uuid
from pathlib import Path

from werkzeug.datastructures import FileStorage


class CvStorage:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def store(self, cv: FileStorage) -> str:
        file_name = f"{uuid.uuid4()}.pdf"
        self.root.mkdir(parents=True, exist_ok=True)
        cv.stream.seek(0)
        cv.save(self.path(file_name))
        return file_name

    def store_bytes(self, content: bytes) -> str:
        """Para los datos de demostración."""
        file_name = f"{uuid.uuid4()}.pdf"
        self.root.mkdir(parents=True, exist_ok=True)
        self.path(file_name).write_bytes(content)
        return file_name

    def delete(self, file_name: str) -> None:
        self.path(file_name).unlink(missing_ok=True)

    def path(self, file_name: str) -> Path:
        """Impide salir de la carpeta aunque el nombre viniera alterado en la base."""
        path = (self.root / file_name).resolve()
        if path.parent != self.root:
            raise ValueError("Nombre de archivo inválido")
        return path
