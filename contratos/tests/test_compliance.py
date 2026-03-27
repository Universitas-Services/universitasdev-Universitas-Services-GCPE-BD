"""
Tests para el módulo de compliance:
- Crear reporte
- Listar reportes (solo del usuario)
- Verificación de ownership en descarga de PDF
"""

import json
import pytest

from contratos.models import ComplianceExpediente
from .conftest import obtener_tokens


pytestmark = pytest.mark.django_db

COMPLIANCE_VALIDO = {
    "nombre_organo_entidad": "Órgano de Control Test",
    "nombre_unidad_revisora": "Unidad Revisora Test",
    "nomenclatura": "AUD-2026-001",
    "fecha_revision": "2026-03-15",
    "persona_contacto": "María García",
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


class TestCrearCompliance:
    """Tests para POST /api/compliance"""

    def test_crear_reporte_exitoso(self, client, usuario):
        """Se puede crear un reporte de compliance con datos válidos."""
        token, _ = obtener_tokens(client)
        response = client.post(
            "/api/compliance",
            data=json.dumps(COMPLIANCE_VALIDO),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200
        assert ComplianceExpediente.objects.filter(usuario_revisor=usuario).count() == 1


class TestListarCompliance:
    """Tests para GET /api/compliance"""

    def test_listar_solo_propios(self, client, usuario, usuario_b):
        """Cada usuario solo ve sus propios reportes."""
        ComplianceExpediente.objects.create(
            usuario_revisor=usuario, **COMPLIANCE_VALIDO
        )
        ComplianceExpediente.objects.create(
            usuario_revisor=usuario_b,
            **{**COMPLIANCE_VALIDO, "nomenclatura": "AUD-2026-002"},
        )

        token, _ = obtener_tokens(client)
        response = client.get(
            "/api/compliance",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        data = response.json()
        assert len(data) == 1  # Solo ve 1, no 2


class TestOwnershipCompliance:
    """Tests para verificación de ownership en descarga de PDF"""

    def test_no_puede_descargar_pdf_ajeno(self, client, usuario, usuario_b):
        """Un usuario no puede descargar el PDF de un reporte de otro usuario."""
        reporte = ComplianceExpediente.objects.create(
            usuario_revisor=usuario_b, **COMPLIANCE_VALIDO
        )
        token, _ = obtener_tokens(client)  # Token de usuario A
        try:
            response = client.get(
                f"/api/compliance/{reporte.id}/pdf",
                HTTP_AUTHORIZATION=f"Bearer {token}",
            )
            # Si WeasyPrint está disponible, debe dar 404 (no es suyo)
            assert response.status_code == 404
        except OSError:
            # WeasyPrint no disponible (falta libgobject en Windows)
            # La verificación de ownership ocurre ANTES del import de WeasyPrint,
            # así que si llega al import de WeasyPrint, significa que NO dio 404,
            # lo cual indicaría un fallo de ownership. Pero get_object_or_404
            # lanza 404 antes del import, así que no debería llegar aquí.
            pytest.fail(
                "El ownership check debió devolver 404 antes de importar WeasyPrint"
            )

    def test_no_puede_enviar_email_pdf_ajeno(self, client, usuario, usuario_b):
        """Un usuario no puede enviar por email el PDF de un reporte ajeno."""
        reporte = ComplianceExpediente.objects.create(
            usuario_revisor=usuario_b, **COMPLIANCE_VALIDO
        )
        token, _ = obtener_tokens(client)  # Token de usuario A
        response = client.post(
            f"/api/compliance/{reporte.id}/enviar-email",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 404
