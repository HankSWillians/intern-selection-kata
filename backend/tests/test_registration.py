"""Registro del practicante: RF-01 a RF-05, RF-09, RF-12 y RF-15."""

import io
import sqlite3

import pytest

from helpers import pdf, register, register_valid, valid_fields


def count_interns(settings) -> int:
    with sqlite3.connect(settings.db_path) as db:
        return db.execute("SELECT count(*) FROM interns").fetchone()[0]


def test_cp01_valid_registration_is_pending_and_stores_the_pdf(client, settings):
    response = register(client, valid_fields("laura@correo.com"), pdf())
    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "PENDING"
    assert body["fullName"] == "Laura Gómez"
    assert body["phone"] == "+573001234567"
    assert body["dataConsentAt"]
    assert response.headers["Location"] == f"/api/v1/interns/{body['id']}"

    with sqlite3.connect(settings.db_path) as db:
        file_name = db.execute("SELECT cv_file_name FROM interns").fetchone()[0]
    assert (settings.upload_dir / file_name).exists()
    assert file_name.endswith(".pdf") and "hoja-de-vida" not in file_name


def test_cp02_cp08_missing_name_is_rejected_and_nothing_is_saved(client, settings):
    fields = valid_fields("sin.nombre@correo.com")
    del fields["fullName"]
    response = register(client, fields, pdf())
    assert response.status_code == 400
    assert response.mimetype == "application/problem+json"
    assert response.get_json()["errors"]["fullName"] == "Escribe tu nombre completo"
    assert count_interns(settings) == 0
    assert list(settings.upload_dir.iterdir()) == []


def test_cp03_invalid_email(client):
    response = register(client, valid_fields("laura@"), pdf())
    assert response.status_code == 400
    assert response.get_json()["errors"]["email"] == "Escribe un correo válido"


@pytest.mark.parametrize("semester", ["0", "13", "abc"])
def test_cp04_semester_out_of_range(client, semester):
    fields = valid_fields("semestre@correo.com")
    fields["semester"] = semester
    response = register(client, fields, pdf())
    assert response.status_code == 400
    assert response.get_json()["errors"]["semester"] == "El semestre debe estar entre 1 y 12"


def test_cp05_non_pdf_file(client):
    response = register(client, valid_fields("docx@correo.com"), (io.BytesIO(b"PK contenido"), "hoja.docx"))
    assert response.status_code == 400
    assert response.get_json()["errors"]["cv"] == "Solo se permiten archivos PDF"


def test_cp06_pdf_over_5_mb(client, settings):
    response = register(client, valid_fields("pesado@correo.com"), pdf("hoja.pdf", 6 * 1024 * 1024))
    assert response.status_code == 400
    assert response.get_json()["errors"]["cv"] == "La hoja de vida no puede pesar más de 5 MB"
    assert count_interns(settings) == 0


def test_cp06_request_over_the_server_limit_answers_413(client):
    response = register(client, valid_fields("enorme@correo.com"), pdf("hoja.pdf", 8 * 1024 * 1024))
    assert response.status_code == 413
    assert response.get_json()["errors"]["cv"] == "La hoja de vida no puede pesar más de 5 MB"


def test_cp07_duplicated_email_even_with_other_case(client, settings):
    register_valid(client, "laura@correo.com")
    response = register(client, valid_fields("Laura@Correo.com"), pdf())
    assert response.status_code == 409
    assert response.get_json()["errors"]["email"] == "Ya existe un registro con este correo"
    assert count_interns(settings) == 1


def test_cp17_data_consent_is_required(client):
    fields = valid_fields("consentimiento@correo.com")
    del fields["dataConsent"]
    response = register(client, fields, pdf())
    assert response.status_code == 400
    assert response.get_json()["errors"]["dataConsent"] == "Debes aceptar el tratamiento de tus datos personales"


@pytest.mark.parametrize("phone", ["2001234567", "30012345"])
def test_cp18_phone_must_be_a_colombian_mobile(client, phone):
    fields = valid_fields("celular@correo.com")
    fields["phone"] = phone
    response = register(client, fields, pdf())
    assert response.status_code == 400
    assert response.get_json()["errors"]["phone"] == "Escribe un celular colombiano de 10 dígitos que empiece por 3"


def test_cp19_other_university_stores_the_written_name(client):
    fields = valid_fields("otra@correo.com")
    fields["university"] = "Otra"
    fields["universityOther"] = "Universidad de Cundinamarca"
    response = register(client, fields, pdf())
    assert response.status_code == 201
    assert response.get_json()["university"] == "Universidad de Cundinamarca"


def test_cp20_other_career_requires_the_name(client):
    fields = valid_fields("otra.carrera@correo.com")
    fields["career"] = "Otra"
    response = register(client, fields, pdf())
    assert response.status_code == 400
    assert response.get_json()["errors"]["careerOther"] == "Escribe el nombre de tu carrera"


def test_cp21_text_file_renamed_to_pdf_is_rejected(client):
    response = register(client, valid_fields("falso@correo.com"), (io.BytesIO(b"esto no es un PDF"), "hoja.pdf"))
    assert response.status_code == 400
    assert response.get_json()["errors"]["cv"] == "Solo se permiten archivos PDF"


def test_rf03_cv_is_required(client):
    response = register(client, valid_fields("sin.cv@correo.com"))
    assert response.status_code == 400
    assert response.get_json()["errors"]["cv"] == "Adjunta tu hoja de vida"


def test_names_with_accents_apostrophe_and_hyphen_are_valid(client):
    fields = valid_fields("maria@correo.com")
    fields["fullName"] = "  María José   Núñez-O'Neil "
    response = register(client, fields, pdf())
    assert response.status_code == 201
    assert response.get_json()["fullName"] == "María José Núñez-O'Neil"


def test_name_with_digits_is_rejected(client):
    fields = valid_fields("digitos@correo.com")
    fields["fullName"] = "Laura 123"
    assert register(client, fields, pdf()).get_json()["errors"]["fullName"] == "El nombre solo puede tener letras"
