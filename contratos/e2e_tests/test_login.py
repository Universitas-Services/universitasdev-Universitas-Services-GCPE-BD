
import re
from playwright.sync_api import Page, expect


def test_pagina_admin_funciona(page: Page, live_server):
    # 1. El robot entra a tu servidor local
    page.goto(f"{live_server.url}/admin/login/")

    # 2. Verifica que el título de la pestaña sea correcto
    expect(page).to_have_title(re.compile("Log in | Django site admin"))

    # 3. Verifica que el botón de "Log in" sea visible
    boton = page.get_by_role("button", name="Log in")
    expect(boton).to_be_visible()
