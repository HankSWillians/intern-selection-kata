"""Flujos completos en el navegador: los casos que antes eran manuales."""

from playwright.sync_api import Page, expect

SUCCESS = "¡Registro exitoso! Tu información quedó en manos del equipo de selección."


def fill_valid_form(page: Page, email: str) -> None:
    page.fill("#f-fullName", "Camila Rodríguez")
    page.fill("#f-email", email)
    page.fill("#f-phone", "311 555 0101")
    page.select_option("#f-university", "Universidad EAN")
    page.select_option("#f-career", "Ingeniería de Software")
    page.select_option("#f-semester", "7")
    page.set_input_files("#f-cv", files=[{"name": "cv.pdf", "mimeType": "application/pdf",
                                          "buffer": b"%PDF-1.4 prueba"}])
    page.check("#f-dataConsent")


def test_cp02_cp17_empty_form_shows_errors_and_is_not_sent(page: Page, live_server):
    page.goto(live_server)
    page.click("[data-submit]")
    expect(page.locator("#e-fullName")).to_have_text("Escribe tu nombre completo")
    expect(page.locator("#e-cv")).to_have_text("Adjunta tu hoja de vida")
    expect(page.locator("#e-dataConsent")).to_have_text("Debes aceptar el tratamiento de tus datos personales")
    expect(page.locator("#f-fullName")).to_be_focused()
    expect(page.locator("[data-success]")).to_be_hidden()


def test_cp05_cp18_cp20_field_rules_in_the_browser(page: Page, live_server):
    page.goto(live_server)
    page.fill("#f-phone", "2001234567")
    page.set_input_files("#f-cv", files=[{"name": "hoja.docx", "mimeType": "application/msword", "buffer": b"x"}])
    page.select_option("#f-career", "Otra")
    page.click("[data-submit]")
    expect(page.locator("#e-phone")).to_have_text("Escribe un celular colombiano de 10 dígitos que empiece por 3")
    expect(page.locator("#e-cv")).to_have_text("Solo se permiten archivos PDF")
    expect(page.locator("#e-careerOther")).to_have_text("Escribe el nombre de tu carrera")


def test_cp01_cp07_register_then_duplicate(page: Page, live_server):
    page.goto(live_server)
    fill_valid_form(page, "camila@correo.com")
    page.click("[data-submit]")
    expect(page.locator("[data-success]")).to_have_text(SUCCESS)
    expect(page.locator("#f-fullName")).to_have_value("")

    fill_valid_form(page, "CAMILA@correo.com")
    page.click("[data-submit]")
    expect(page.locator("#e-email")).to_have_text("Ya existe un registro con este correo")
    expect(page.locator("#f-fullName")).to_have_value("Camila Rodríguez")


def test_cp14_cp15_panel_requires_login(page: Page, live_server):
    page.goto(f"{live_server}/panel.html")
    page.wait_for_url("**/login.html?volver=*")
    page.fill("#username", "analista")
    page.fill("#password", "otra")
    page.click("[data-submit]")
    expect(page.locator("[data-error]")).to_have_text("Usuario o contraseña incorrectos")


def test_cp09_cp12_cp22_decide_from_the_list_and_filter(logged_in: Page):
    page = logged_in
    expect(page.locator("[data-rows] tr")).to_have_count(4)
    expect(page.locator("a.tab", has_text="Pendientes")).to_contain_text("2")

    row = page.locator("tr", has_text="Andrés Felipe Torres")
    row.locator('[data-decide="VIABLE"]').click()
    expect(page.locator("[data-toast]")).to_have_text("Decisión guardada")
    expect(page.locator("tr", has_text="Andrés Felipe Torres").locator(".badge")).to_have_text("Viable")

    page.click("a.tab:has-text('Pendientes')")
    expect(page.locator("[data-rows] tr")).to_have_count(1)
    page.reload()
    expect(page.locator("[data-rows] tr")).to_have_count(1)


def test_cp10_empty_tab_message(logged_in: Page):
    page = logged_in
    for name in ("Laura Gómez Rincón", "Andrés Felipe Torres"):
        page.locator("tr", has_text=name).locator('[data-decide="VIABLE"]').click()
        expect(page.locator("tr", has_text=name).locator(".badge")).to_have_text("Viable")
    page.click("a.tab:has-text('Pendientes')")
    expect(page.locator("[data-empty]")).to_have_text("No hay practicantes pendientes")


def test_cp11_cp16_cp23_detail_note_and_download(logged_in: Page):
    page = logged_in
    page.click("a.name:has-text('Laura Gómez Rincón')")
    expect(page.locator("[data-name]")).to_have_text("Laura Gómez Rincón")
    expect(page.locator("[data-phone]")).to_have_text("300 123 4567")

    page.fill("#note", "No cumple el semestre mínimo")
    page.click('[data-decide="NOT_VIABLE"]')
    expect(page.locator("[data-feedback]")).to_have_text("Decisión guardada")
    expect(page.locator("[data-badge] .badge")).to_have_text("No viable")
    page.reload()
    expect(page.locator("#note")).to_have_value("No cumple el semestre mínimo")

    with page.expect_download() as download:
        page.click("[data-download]")
    assert download.value.suggested_filename == "CV - Laura Gómez Rincón.pdf"


def test_session_expired_goes_back_to_login(logged_in: Page):
    page = logged_in
    page.evaluate("sessionStorage.setItem('intern-selection.token', 'token-alterado')")
    page.reload()
    page.wait_for_url("**/login.html?expirada=1*")
    expect(page.locator("[data-expired]")).to_be_visible()
