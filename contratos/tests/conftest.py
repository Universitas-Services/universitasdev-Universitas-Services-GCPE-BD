"""
Helpers compartidos para los tests.
Crea un usuario activo con perfil listo para usar con la API.
"""

import pytest
from django.contrib.auth.models import User
from contratos.models import PerfilUsuario


@pytest.fixture
def usuario(db):
    """Crea un usuario activo con perfil para usar en tests."""
    user = User.objects.create_user(
        username="test@test.com",
        email="test@test.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    PerfilUsuario.objects.create(
        user=user,
        telefono="04141234567",
        cargo="Analista",
        nombre_institucion_ente="Institución Test",
    )
    return user


@pytest.fixture
def usuario_b(db):
    """Segundo usuario para tests de ownership."""
    user = User.objects.create_user(
        username="otro@test.com",
        email="otro@test.com",
        password="TestPass123!",
        first_name="Otro",
        last_name="Usuario",
        is_active=True,
    )
    PerfilUsuario.objects.create(user=user, telefono="04149999999", cargo="Director")
    return user


@pytest.fixture
def client():
    """Cliente HTTP de Django para hacer requests."""
    from django.test import Client

    return Client()


def obtener_tokens(client, email="test@test.com", password="TestPass123!"):
    """Helper para obtener tokens JWT de login."""
    import json

    response = client.post(
        "/api/token/pair",
        data=json.dumps({"username": email, "password": password}),
        content_type="application/json",
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access"), data.get("refresh")
    return None, None
