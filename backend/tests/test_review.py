"""Panel del analista: RF-06 a RF-08, RF-10, RF-11, RF-13, RF-14, RF-16 a RF-18."""

from helpers import register_valid


def decide(client, auth, intern_id, body):
    return client.patch(f"/api/v1/interns/{intern_id}/status", json=body, headers=auth)


def test_cp14_list_and_download_require_a_session(client):
    assert client.get("/api/v1/interns").status_code == 401
    assert client.get("/api/v1/interns/1/cv").status_code == 401
    assert client.get("/api/v1/interns/summary").status_code == 401


def test_cp09_list_is_newest_first(client, auth):
    register_valid(client, "primero@correo.com")
    register_valid(client, "segundo@correo.com")
    newest = register_valid(client, "tercero@correo.com")
    response = client.get("/api/v1/interns", headers=auth)
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 3
    assert body[0]["id"] == newest


def test_cp10_empty_list(client, auth):
    assert client.get("/api/v1/interns", headers=auth).get_json() == []


def test_cp11_detail_has_all_the_data_but_not_the_server_file_name(client, auth):
    intern_id = register_valid(client, "detalle@correo.com")
    body = client.get(f"/api/v1/interns/{intern_id}", headers=auth).get_json()
    assert body["email"] == "detalle@correo.com"
    assert body["university"] == "Universidad Nacional de Colombia"
    assert body["career"] == "Ingeniería de Sistemas"
    assert body["semester"] == 8
    assert "cvFileName" not in body
    assert client.get("/api/v1/interns/9999", headers=auth).status_code == 404


def test_cp12_mark_viable_is_saved_with_the_decision_date(client, auth):
    intern_id = register_valid(client, "viable@correo.com")
    response = decide(client, auth, intern_id, {"status": "VIABLE"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "VIABLE"
    assert response.get_json()["reviewedAt"]
    assert client.get(f"/api/v1/interns/{intern_id}", headers=auth).get_json()["status"] == "VIABLE"


def test_cp13_unknown_status_is_rejected(client, auth):
    intern_id = register_valid(client, "invalido@correo.com")
    response = decide(client, auth, intern_id, {"status": "MAYBE"})
    assert response.status_code == 400
    assert "status" in response.get_json()["errors"]
    assert client.get(f"/api/v1/interns/{intern_id}", headers=auth).get_json()["status"] == "PENDING"


def test_cp23_change_decision_with_a_note(client, auth):
    intern_id = register_valid(client, "cambio@correo.com")
    decide(client, auth, intern_id, {"status": "VIABLE", "note": "Buen perfil"})
    body = decide(client, auth, intern_id, {"status": "NOT_VIABLE", "note": "No cumple el semestre mínimo"}).get_json()
    assert body["status"] == "NOT_VIABLE"
    assert body["reviewNote"] == "No cumple el semestre mínimo"
    # Una observación vacía borra la anterior.
    assert decide(client, auth, intern_id, {"status": "VIABLE", "note": ""}).get_json()["reviewNote"] is None


def test_cp24_cannot_go_back_to_pending(client, auth):
    intern_id = register_valid(client, "pendiente@correo.com")
    decide(client, auth, intern_id, {"status": "VIABLE"})
    assert decide(client, auth, intern_id, {"status": "PENDING"}).status_code == 400
    assert client.get(f"/api/v1/interns/{intern_id}", headers=auth).get_json()["status"] == "VIABLE"


def test_rf17_note_has_at_most_500_characters(client, auth):
    intern_id = register_valid(client, "nota@correo.com")
    response = decide(client, auth, intern_id, {"status": "VIABLE", "note": "a" * 501})
    assert response.status_code == 400
    assert "note" in response.get_json()["errors"]


def test_cp22_filter_by_status_and_counts(client, auth):
    register_valid(client, "p1@correo.com")
    register_valid(client, "p2@correo.com")
    viable = register_valid(client, "v1@correo.com")
    decide(client, auth, viable, {"status": "VIABLE"})

    assert len(client.get("/api/v1/interns?status=PENDING", headers=auth).get_json()) == 2
    assert client.get("/api/v1/interns/summary", headers=auth).get_json() == {
        "total": 3, "pending": 2, "viable": 1, "notViable": 0,
    }
    assert client.get("/api/v1/interns?status=OTRO", headers=auth).status_code == 400


def test_cp16_download_the_cv_with_the_intern_name(client, auth):
    intern_id = register_valid(client, "descarga@correo.com")
    response = client.get(f"/api/v1/interns/{intern_id}/cv", headers=auth)
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF-")
    disposition = response.headers["Content-Disposition"]
    assert "attachment" in disposition
    assert "CV%20-%20Laura%20G%C3%B3mez.pdf" in disposition
