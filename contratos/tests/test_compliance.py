"""
Tests para el módulo de compliance:
- Generar PDF al vuelo
- Enviar reporte por email
"""

import json
import pytest
from unittest.mock import patch

from .conftest import obtener_tokens


pytestmark = pytest.mark.django_db

COMPLIANCE_VALIDO = {
    "nombre_organo_entidad": "Órgano de Control Test",
    "nombre_unidad_revisora": "Unidad Revisora Test",
    "nomenclatura": "AUD-2026-001",
    "fecha_revision": "2026-03-15",
    "persona_contacto": "test@correo.com",
    "nombre_completo_revisor": "Pedro López",
    "caaue1_incluye_actividades_previas": "SI",
    "caaue2_incluye_acta_inicio": "SI",
    "caaue3_incluye_pliego_condiciones": "NO",
    "caaue4_publicacion_llamado_snc": "NA",
    "caaue5_publicacion_llamado_ente": "SI",
    "caaue6_incluye_registro_adquirientes": "SI",
    "caaue7_incluye_modificaciones": "NA",
    "caaue8_incluye_acta_recepcion_sobres": "SI",
    "caaue9_incluye_acta_apertura_sobres": "NO",
    "caaue10_incluye_ofertas": "SI",
    "caaue11_incluye_garantias_sostenimiento": "SI",
    "caaue12_incluye_certificado_rnc": "NA",
    "caaue13_incluye_certificado_snc": "SI",
    "caaue14_incluye_solvencias": "SI",
    "caaue15_incluye_informe_recomendacion": "NO",
    "caaue16_incluye_adjudicacion": "SI",
    "caaue17_incluye_notificacion": "SI",
    "caaue18_incluye_garantias_contratacion": "NA",
    "caaue19_incluye_contrato_u_orden": "SI",
    "caaue20_incluye_resp_social": "SI",
    "caaue21_identificacion_nomenclatura": "SI",
    "caaue22_expediente_foliado": "SI",
    "caaue23_identificacion_tomos": "NA",
    "caaue24_archivo_custodia": "SI",
}


class TestGenerarCompliancePDF:
    """Tests para POST /api/compliance/pdf"""

    def test_generar_pdf_exitoso(self, client, usuario):
        """Se puede generar un PDF de compliance al vuelo."""
        token, _ = obtener_tokens(client)
        try:
            response = client.post(
                "/api/compliance/pdf",
                data=json.dumps(COMPLIANCE_VALIDO),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
            assert response.status_code == 200
            assert response["Content-Type"] == "application/pdf"
        except OSError:
            # WeasyPrint no disponible en Windows (falta libgobject)
            pytest.skip("WeasyPrint no disponible en este entorno")

    def test_requiere_autenticacion(self, client):
        """El endpoint requiere token JWT."""
        response = client.post(
            "/api/compliance/pdf",
            data=json.dumps(COMPLIANCE_VALIDO),
            content_type="application/json",
        )
        assert response.status_code == 401


class TestEnviarComplianceEmail:
    """Tests para POST /api/compliance/enviar-email"""

    @patch("contratos.routers.compliance.enviar_correo_con_pdf")
    def test_enviar_email_exitoso(self, mock_enviar, client, usuario):
        """Se puede generar y enviar un compliance por email."""
        token, _ = obtener_tokens(client)
        try:
            response = client.post(
                "/api/compliance/enviar-email",
                data=json.dumps(COMPLIANCE_VALIDO),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
            assert response.status_code == 200
            assert "test@correo.com" in response.json()["message"]
            mock_enviar.assert_called_once()
        except OSError:
            pytest.skip("WeasyPrint no disponible en este entorno")

    def test_requiere_autenticacion(self, client):
        """El endpoint requiere token JWT."""
        response = client.post(
            "/api/compliance/enviar-email",
            data=json.dumps(COMPLIANCE_VALIDO),
            content_type="application/json",
        )
        assert response.status_code == 401
