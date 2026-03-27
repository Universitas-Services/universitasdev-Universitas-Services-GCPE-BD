"""
Tests para el módulo de perfil:
- Obtener perfil con /me
- Actualizar perfil
- Cambiar contraseña
"""

import json
import pytest

from .conftest import obtener_tokens


pytestmark = pytest.mark.django_db


class TestObtenerPerfil:
    """Tests para GET /api/me"""

    def test_obtener_perfil_autenticado(self, client, usuario):
        """Un usuario autenticado puede ver su perfil."""
        token, _ = obtener_tokens(client)
        response = client.get("/api/me", HTTP_AUTHORIZATION=f"Bearer {token}")
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == "test@test.com"
        assert data["first_name"] == "Test"
        assert data["cargo"] == "Analista"

    def test_perfil_sin_token_falla(self, client):
        """Sin token JWT, /me devuelve 401."""
        response = client.get("/api/me")
        assert response.status_code == 401


class TestActualizarPerfil:
    """Tests para PUT /api/perfil"""

    def test_actualizar_nombre(self, client, usuario):
        """Se puede actualizar el nombre del usuario."""
        token, _ = obtener_tokens(client)
        response = client.put(
            "/api/perfil",
            data=json.dumps({"first_name": "NuevoNombre"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200

        usuario.refresh_from_db()
        assert usuario.first_name == "NuevoNombre"

    def test_actualizar_telefono_invalido(self, client, usuario):
        """Un teléfono con letras debe ser rechazado."""
        token, _ = obtener_tokens(client)
        response = client.put(
            "/api/perfil",
            data=json.dumps({"telefono": "abc1234567"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 422

    def test_actualizar_email_duplicado(self, client, usuario, usuario_b):
        """No se puede cambiar a un email que ya usa otro usuario."""
        token, _ = obtener_tokens(client)
        response = client.put(
            "/api/perfil",
            data=json.dumps({"email": "otro@test.com"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 400


class TestCambiarContrasena:
    """Tests para POST /api/auth/change-password"""

    def test_cambiar_contrasena_exitoso(self, client, usuario):
        """Con la contraseña actual correcta, se puede cambiar."""
        token, _ = obtener_tokens(client)
        response = client.post(
            "/api/auth/change-password",
            data=json.dumps(
                {
                    "current_password": "TestPass123!",
                    "new_password": "NuevaClave456!",
                    "confirm_password": "NuevaClave456!",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 200

    def test_cambiar_contrasena_actual_incorrecta(self, client, usuario):
        """Si la contraseña actual es incorrecta, falla."""
        token, _ = obtener_tokens(client)
        response = client.post(
            "/api/auth/change-password",
            data=json.dumps(
                {
                    "current_password": "IncorrectaABC!",
                    "new_password": "NuevaClave456!",
                    "confirm_password": "NuevaClave456!",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == 400
