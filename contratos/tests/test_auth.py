"""
Tests para el módulo de autenticación:
- Registro de usuario
- Soft delete (desactivación de cuenta)
- Login bloqueado para usuarios inactivos
"""

import json
import pytest
from django.contrib.auth.models import User
from contratos.models import PerfilUsuario


pytestmark = pytest.mark.django_db


class TestRegistro:
    """Tests para POST /api/auth/register"""

    def test_registro_exitoso(self, client):
        """El registro crea un usuario inactivo con perfil."""
        payload = {
            "email": "nuevo@test.com",
            "password": "ClaveSegura123!",
            "confirm_password": "ClaveSegura123!",
            "first_name": "Nuevo",
            "last_name": "Usuario",
            "telefono": "04141234567",
        }
        response = client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200

        # Verificar que el usuario se creó inactivo
        user = User.objects.get(email="nuevo@test.com")
        assert user.is_active is False
        assert user.first_name == "Nuevo"

        # Verificar que se creó el perfil
        perfil = PerfilUsuario.objects.get(user=user)
        assert perfil.telefono == "04141234567"

    def test_registro_email_duplicado(self, client, usuario):
        """No se puede registrar con un email que ya existe."""
        payload = {
            "email": "test@test.com",  # Ya existe (fixture usuario)
            "password": "ClaveSegura123!",
            "confirm_password": "ClaveSegura123!",
            "first_name": "Dup",
            "last_name": "Licado",
            "telefono": "04141234567",
        }
        response = client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_registro_passwords_no_coinciden(self, client):
        """El registro falla si las contraseñas no coinciden."""
        payload = {
            "email": "nuevo2@test.com",
            "password": "ClaveSegura123!",
            "confirm_password": "OtraClave456!",
            "first_name": "Test",
            "last_name": "Fail",
            "telefono": "04141234567",
        }
        response = client.post(
            "/api/auth/register",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 422


class TestSoftDeleteUsuario:
    """Tests para DELETE /api/auth/delete-account (soft delete)"""

    def test_soft_delete_desactiva_cuenta(self, client, usuario):
        """Al eliminar cuenta, el usuario se desactiva pero no se borra."""
        from .conftest import obtener_tokens

        token, _ = obtener_tokens(client)
        response = client.delete(
            "/api/auth/delete-account",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200

        # El usuario sigue existiendo pero está inactivo
        usuario.refresh_from_db()
        assert usuario.is_active is False

    def test_soft_delete_no_borra_datos(self, client, usuario):
        """Después del soft delete, el perfil sigue existiendo."""
        from .conftest import obtener_tokens

        token, _ = obtener_tokens(client)
        client.delete(
            "/api/auth/delete-account",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        # El perfil asociado no se eliminó
        assert PerfilUsuario.objects.filter(user=usuario).exists()

    def test_login_bloqueado_despues_de_soft_delete(self, client, usuario):
        """Un usuario desactivado no puede obtener tokens JWT."""
        from .conftest import obtener_tokens

        # Primero hacemos soft delete
        token, _ = obtener_tokens(client)
        client.delete(
            "/api/auth/delete-account",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        # Intentar login de nuevo debe fallar
        token2, _ = obtener_tokens(client)
        assert token2 is None
