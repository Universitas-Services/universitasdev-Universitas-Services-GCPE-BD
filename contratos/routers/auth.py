from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
import os

from ..models import PerfilUsuario
from ..schemas import (
    UserProfileSchema,
    UserRegisterSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
)

router = Router(tags=["🔐 Autenticación"])


# --- REGISTRO ---
@router.post("/auth/register", response=UserProfileSchema, auth=None)
def registrar_usuario(request, payload: UserRegisterSchema):
    """
    Registro público. Crea Usuario y Perfil (con teléfono).
    """
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "El correo electrónico ya está registrado")

    try:
        with transaction.atomic():
            user = User.objects.create(
                username=payload.email,
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                password=make_password(payload.password),
            )
            PerfilUsuario.objects.update_or_create(
                user=user, defaults={"telefono": payload.telefono}
            )
            return user
    except Exception as e:
        raise HttpError(500, f"Error al procesar el registro: {str(e)}")


# --- RECUPERACIÓN DE CONTRASEÑA (Paso 1: Enviar Correo) ---
@router.post("/auth/password-reset", auth=None)
def request_password_reset(request, payload: PasswordResetRequestSchema):
    """
    Envía un correo con un link para restablecer la contraseña.
    """
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"message": "Si el correo existe, se ha enviado un enlace."}

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/auth/reset-password/{uid}/{token}"

    asunto = "Restablecer contraseña - Universitas"
    mensaje = f"""
    Hola {user.first_name}, Has solicitado restablecer tu contraseña.
    Haz clic en el siguiente enlace: {reset_link}

    Si no fuiste tú, ignora este mensaje.
    """
    send_mail(asunto, mensaje, None, [user.email], fail_silently=False)

    return {"message": "Si el correo existe, se ha enviado un enlace."}


# --- RECUPERACIÓN DE CONTRASEÑA (Paso 2: Confirmar y Cambiar) ---
@router.post("/auth/password-reset-confirm", auth=None)
def confirm_password_reset(request, payload: PasswordResetConfirmSchema):
    """
    Valida el token del correo y cambia la contraseña.
    El frontend envía: uidb64, token, new_password, confirm_password.
    """
    try:
        uid = urlsafe_base64_decode(payload.uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        raise HttpError(400, "Link inválido o expirado")

    if not default_token_generator.check_token(user, payload.token):
        raise HttpError(400, "Token inválido o expirado")

    user.set_password(payload.new_password)
    user.save()
    return {"message": "Contraseña actualizada exitosamente"}


# --- LOGOUT (Invalidar Token) ---
@router.post("/auth/logout", auth=JWTAuth())
def logout(request, refresh_token: str = None):
    """
    Cierra la sesión invalidando el refresh token.
    El frontend debe enviar el refresh_token en el body.
    """
    if not refresh_token:
        raise HttpError(400, "Debe enviar el refresh_token para cerrar sesión")
    try:
        from ninja_jwt.tokens import RefreshToken

        token = RefreshToken(refresh_token)
        token.blacklist()
        return {"message": "Sesión cerrada exitosamente"}
    except Exception:
        raise HttpError(400, "Token inválido o ya expirado")
