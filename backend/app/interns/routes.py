"""API de practicantes (specs, sección 8)."""

from flask import Blueprint, current_app, jsonify, request, send_file

from ..auth.decorators import require_auth
from ..db import get_db
from ..errors import ApiError
from . import repository, service
from .storage import CvStorage

bp = Blueprint("interns", __name__, url_prefix="/api/v1/interns")


def _storage() -> CvStorage:
    return CvStorage(current_app.config["SETTINGS"].upload_dir)


@bp.post("")
def register():
    """RF-09: registro público con la hoja de vida."""
    row = service.register(get_db(), _storage(), request.form, request.files,
                           current_app.config["SETTINGS"].max_cv_mb)
    response = jsonify(repository.to_json(row))
    response.status_code = 201
    response.headers["Location"] = f"/api/v1/interns/{row['id']}"
    return response


@bp.get("")
@require_auth
def list_interns():
    """RF-10, RF-16: lista, opcionalmente filtrada por estado."""
    status = service.parse_filter(request.args.get("status"))
    return jsonify([repository.to_json(row) for row in repository.find_all(get_db(), status)])


@bp.get("/summary")
@require_auth
def summary():
    """RF-16: cantidades para las pestañas del panel."""
    counts = repository.count_by_status(get_db())
    return jsonify(
        total=sum(counts.values()),
        pending=counts["PENDING"],
        viable=counts["VIABLE"],
        notViable=counts["NOT_VIABLE"],
    )


@bp.get("/<int:intern_id>")
@require_auth
def detail(intern_id: int):
    """RF-07."""
    return jsonify(repository.to_json(service.get(get_db(), intern_id)))


@bp.patch("/<int:intern_id>/status")
@require_auth
def decide(intern_id: int):
    """RF-11, RF-17, RF-18."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ApiError.validation({"status": "Envía un JSON con status y note"})
    row = service.decide(get_db(), intern_id, body.get("status"), body.get("note"))
    return jsonify(repository.to_json(row))


@bp.get("/<int:intern_id>/cv")
@require_auth
def download_cv(intern_id: int):
    """RF-14: descarga con el nombre «CV - nombre completo.pdf»."""
    row = service.get(get_db(), intern_id)
    path = _storage().path(row["cv_file_name"])
    if not path.exists():
        raise ApiError(404, "No encontrado", "La hoja de vida de este practicante no está en el servidor.")
    return send_file(path, mimetype="application/pdf", as_attachment=True,
                     download_name=f"CV - {row['full_name']}.pdf")
