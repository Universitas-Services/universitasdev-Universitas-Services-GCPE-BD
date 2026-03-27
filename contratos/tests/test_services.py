"""
Tests para services.py:
- generar_data_para_pdf() calcula puntos correctamente
- Lógica del semáforo: SI suma puntos, NO no suma, NA es neutral
"""

import pytest
from datetime import date
from django.contrib.auth.models import User
from contratos.models import ComplianceExpediente
from contratos.services import generar_data_para_pdf, CATALOGO_PREGUNTAS


pytestmark = pytest.mark.django_db


@pytest.fixture
def usuario_servicio(db):
    return User.objects.create_user(
        username="serv@test.com",
        email="serv@test.com",
        password="TestPass123!",
        is_active=True,
    )


def crear_reporte(usuario, respuestas: dict):
    """Crea un reporte con las respuestas dadas (default NA para el resto)."""
    defaults = {campo: "NA" for campo in CATALOGO_PREGUNTAS.keys()}
    defaults.update(respuestas)
    return ComplianceExpediente.objects.create(
        usuario_revisor=usuario,
        nombre_organo_entidad="Test",
        nombre_unidad_revisora="Test",
        nomenclatura="TEST-001",
        fecha_revision=date.today(),
        persona_contacto="Test",
        nombre_completo_revisor="Test",
        **defaults,
    )


class TestGenerarDataParaPdf:
    """Tests para generar_data_para_pdf()"""

    def test_todo_si_puntaje_maximo(self, usuario_servicio):
        """Si todas las respuestas son SI, el puntaje es el máximo posible."""
        respuestas = {campo: "SI" for campo in CATALOGO_PREGUNTAS.keys()}
        reporte = crear_reporte(usuario_servicio, respuestas)
        data = generar_data_para_pdf(reporte)

        total_esperado = sum(info["puntos"] for info in CATALOGO_PREGUNTAS.values())
        assert data["total_puntos"] == total_esperado
        assert data["total_puntos"] == data["maximos_posibles"]

    def test_todo_no_puntaje_cero(self, usuario_servicio):
        """Si todas las respuestas son NO, el puntaje es 0."""
        respuestas = {campo: "NO" for campo in CATALOGO_PREGUNTAS.keys()}
        reporte = crear_reporte(usuario_servicio, respuestas)
        data = generar_data_para_pdf(reporte)

        assert data["total_puntos"] == 0
        assert data["maximos_posibles"] > 0  # Los puntos eran posibles

    def test_todo_na_puntaje_cero_maximo_cero(self, usuario_servicio):
        """Si todas las respuestas son NA, tanto puntos como máximo son 0."""
        respuestas = {campo: "NA" for campo in CATALOGO_PREGUNTAS.keys()}
        reporte = crear_reporte(usuario_servicio, respuestas)
        data = generar_data_para_pdf(reporte)

        assert data["total_puntos"] == 0
        assert data["maximos_posibles"] == 0

    def test_si_agrega_puntos_no_agrega_error(self, usuario_servicio):
        """Una respuesta SI no debe tener condición de error ni criterio legal."""
        respuestas = {"caaue1_incluye_actividades_previas": "SI"}
        reporte = crear_reporte(usuario_servicio, respuestas)
        data = generar_data_para_pdf(reporte)

        item_1 = data["detalles"][0]
        assert item_1["cumple"] == "SI"
        assert item_1["condicion"] == ""
        assert item_1["criterio"] == ""

    def test_no_incluye_error_y_criterio(self, usuario_servicio):
        """Una respuesta NO debe incluir condición de error y criterio legal."""
        respuestas = {"caaue1_incluye_actividades_previas": "NO"}
        reporte = crear_reporte(usuario_servicio, respuestas)
        data = generar_data_para_pdf(reporte)

        item_1 = data["detalles"][0]
        assert item_1["cumple"] == "NO"
        assert item_1["condicion"] != ""
        assert item_1["criterio"] != ""

    def test_cantidad_detalles_es_24(self, usuario_servicio):
        """Siempre se generan exactamente 24 preguntas."""
        reporte = crear_reporte(usuario_servicio, {})
        data = generar_data_para_pdf(reporte)
        assert len(data["detalles"]) == 24
