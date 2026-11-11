"""RF-19: con DEMO_DATA=true se cargan 4 practicantes ficticios para la
presentación. Solo si la tabla está vacía, para no duplicarlos al reiniciar."""

import sqlite3
from datetime import timedelta

from . import clock
from .interns import repository
from .interns.storage import CvStorage

SEEDS = (
    ("Laura Gómez Rincón", "laura.gomez@example.com", "+573001234567",
     "Universidad Nacional de Colombia", "Ingeniería de Sistemas", 8, "PENDING", None, 1),
    ("Andrés Felipe Torres", "andres.torres@example.com", "+573109876543",
     "Pontificia Universidad Javeriana", "Ingeniería de Software", 7, "PENDING", None, 3),
    ("Valentina Ruiz Castaño", "valentina.ruiz@example.com", "+573205551234",
     "Universidad de los Andes", "Ciencia de Datos", 9, "VIABLE",
     "Buen perfil en datos; agendar entrevista técnica.", 26),
    ("Sebastián Morales", "sebastian.morales@example.com", "+573157778899",
     "Universidad Distrital Francisco José de Caldas", "Ingeniería Electrónica", 4, "NOT_VIABLE",
     "Debe cursar al menos el sexto semestre.", 50),
)


def load_demo_data(db: sqlite3.Connection, storage: CvStorage) -> int:
    if repository.count(db) > 0:
        return 0
    now = clock.now()
    for name, email, phone, university, career, semester, status, note, hours_ago in SEEDS:
        created_at = now - timedelta(hours=hours_ago)
        intern_id = repository.insert(db, {
            "full_name": name, "email": email, "phone": phone, "university": university,
            "career": career, "semester": semester,
            "cv_file_name": storage.store_bytes(sample_pdf(name)),
            "cv_original_name": "hoja-de-vida.pdf",
            "data_consent_at": created_at.isoformat(), "created_at": created_at.isoformat(),
        })
        if status != "PENDING":
            repository.update_decision(db, intern_id, status, note, created_at + timedelta(hours=2))
    return len(SEEDS)


def sample_pdf(name: str) -> bytes:
    """PDF mínimo de una página con el nombre del practicante."""
    text = f"Hoja de vida de ejemplo - {name}".replace("(", "").replace(")", "")
    stream = f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    pdf = "%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf.encode("latin-1")))
        pdf += f"{number} 0 obj\n{body}\nendobj\n"
    xref = len(pdf.encode("latin-1"))
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    pdf += "".join(f"{offset:010d} 00000 n \n" for offset in offsets)
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return pdf.encode("latin-1")
