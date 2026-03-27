"""
Tests para el módulo de proveedores:
- Crear proveedor
- Listar proveedores (solo los del usuario)
- Soft delete de proveedor
- Validaciones de RIF, teléfono, etc.
"""

import json
import pytest

from contratos.models import Proveedor
from .conftest import obtener_tokens


pytestmark = pytest.mark.django_db

PROVEEDOR_VALIDO = {
    "correo_proveedor": "proveedor@test.com",
    "nombre_proveedor": "Empresa Test C.A.",
    "rif_proveedor": "J-12345678-0",
    "tipo_persona": "J",
    "estado": "Miranda",
    "municipio": "Baruta",
    "parroquia": "El Cafetal",
    "direccion_fiscal": "Calle Principal, Edificio Test",
    "telefono_proveedor": "02121234567",
    "nombre_rep_legal": "Juan Pérez",
    "cedula_rep_legal": "V-12345678",
    "area_especialidad": "Bienes",
    "anos_experiencia": 5,
    "patrimonio_reportado": "1500000.50",
    "nivel_contratacion": "ALTA",
}


class TestCrearProveedor:
    """Tests para POST /api/proveedores"""

    def test_crear_proveedor_exitoso(self, client, usuario):
        """Se puede crear un proveedor con datos válidos."""
        token, _ = obtener_tokens(client)
        response = client.post(
            "/api/proveedores",
            data=json.dumps(PROVEEDOR_VALIDO),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200
        assert Proveedor.objects.filter(creado_por=usuario).count() == 1

    def test_crear_proveedor_rif_invalido(self, client, usuario):
        """Un RIF con formato incorrecto debe ser rechazado."""
        token, _ = obtener_tokens(client)
        payload = {**PROVEEDOR_VALIDO, "rif_proveedor": "INVALIDO"}
        response = client.post(
            "/api/proveedores",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 422

    def test_patrimonio_con_coma(self, client, usuario):
        """El patrimonio acepta comas como separador decimal."""
        token, _ = obtener_tokens(client)
        payload = {**PROVEEDOR_VALIDO, "patrimonio_reportado": "1500000,50"}
        response = client.post(
            "/api/proveedores",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200


class TestListarProveedores:
    """Tests para GET /api/proveedores"""

    def test_listar_solo_propios(self, client, usuario, usuario_b):
        """Cada usuario solo ve sus propios proveedores."""
        # Crear proveedor para usuario A
        Proveedor.objects.create(
            creado_por=usuario, **{k: v for k, v in PROVEEDOR_VALIDO.items()}
        )
        # Crear proveedor para usuario B
        Proveedor.objects.create(
            creado_por=usuario_b,
            **{
                **{k: v for k, v in PROVEEDOR_VALIDO.items()},
                "rif_proveedor": "J-99999999-0",
            },
        )

        token, _ = obtener_tokens(client)
        response = client.get("/api/proveedores", HTTP_AUTHORIZATION=f"Bearer {token}")
        data = response.json()

        assert data["total"] == 1  # Solo ve 1, no 2

    def test_busqueda_por_nombre(self, client, usuario):
        """La búsqueda filtra por nombre del proveedor."""
        Proveedor.objects.create(
            creado_por=usuario, **{k: v for k, v in PROVEEDOR_VALIDO.items()}
        )
        token, _ = obtener_tokens(client)
        response = client.get(
            "/api/proveedores?q=Empresa",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.json()["total"] == 1

        response = client.get(
            "/api/proveedores?q=NoExiste",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.json()["total"] == 0


class TestSoftDeleteProveedor:
    """Tests para DELETE /api/proveedores/{id}"""

    def test_soft_delete_exitoso(self, client, usuario):
        """Al eliminar un proveedor, se marca como inactivo."""
        proveedor = Proveedor.objects.create(
            creado_por=usuario, **{k: v for k, v in PROVEEDOR_VALIDO.items()}
        )
        token, _ = obtener_tokens(client)
        response = client.delete(
            f"/api/proveedores/{proveedor.id}",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200

        proveedor.refresh_from_db()
        assert proveedor.activo is False

    def test_proveedor_eliminado_no_aparece_en_lista(self, client, usuario):
        """Un proveedor con activo=False no aparece en el listado."""
        proveedor = Proveedor.objects.create(
            creado_por=usuario, **{k: v for k, v in PROVEEDOR_VALIDO.items()}
        )
        proveedor.activo = False
        proveedor.save()

        token, _ = obtener_tokens(client)
        response = client.get("/api/proveedores", HTTP_AUTHORIZATION=f"Bearer {token}")
        assert response.json()["total"] == 0

    def test_no_puede_eliminar_proveedor_ajeno(self, client, usuario, usuario_b):
        """Un usuario no puede eliminar proveedores de otro usuario."""
        proveedor = Proveedor.objects.create(
            creado_por=usuario_b, **{k: v for k, v in PROVEEDOR_VALIDO.items()}
        )
        token, _ = obtener_tokens(client)  # Token de usuario A
        response = client.delete(
            f"/api/proveedores/{proveedor.id}",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 404  # No encontrado (no es suyo)
