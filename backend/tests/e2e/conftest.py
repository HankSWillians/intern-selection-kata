"""Pruebas del navegador (Playwright): levantan la aplicación real en un hilo,
con base y carpeta temporales y los 4 practicantes de demostración."""

import os
import threading

import pytest
from werkzeug.serving import make_server

from app import create_app
from helpers import ANALYST, PASSWORD, make_settings


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # En equipos sin el Chromium de Playwright se puede usar otro con esta variable.
    path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    return {**browser_type_launch_args, **({"executable_path": path} if path else {})}


@pytest.fixture
def live_server(tmp_path):
    app = create_app(make_settings(tmp_path, demo_data=True))
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def logged_in(page, live_server):
    page.goto(f"{live_server}/login.html")
    page.fill("#username", ANALYST)
    page.fill("#password", PASSWORD)
    page.click("[data-submit]")
    page.wait_for_url("**/panel.html")
    page.wait_for_selector("[data-rows] tr")
    return page
