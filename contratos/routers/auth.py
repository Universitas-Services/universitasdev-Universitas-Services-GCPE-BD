from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.http import HttpResponseRedirect
import os

from ..models import PerfilUsuario
from ..schemas import (
    UserRegisterSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
)
from ..email_service import enviar_correo_activacion, enviar_correo_reset_password

router = Router(tags=["🔐 Autenticación"])


# --- REGISTRO (con activación por correo) ---
@router.post("/auth/register", auth=None)
def registrar_usuario(request, payload: UserRegisterSchema):
    """
    Registro público. Crea Usuario (inactivo) y Perfil.
    Envía un correo con un link para activar la cuenta.
    El usuario NO podrá iniciar sesión hasta que active su cuenta.
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
                is_active=False,  # <--- NO puede hacer login hasta activar
            )
            PerfilUsuario.objects.update_or_create(
                user=user, defaults={"telefono": payload.telefono}
            )

        # Enviar correo de activación (fuera del atomic para no bloquear)
        enviar_correo_activacion(user)

        return {
            "message": (
                "Registro exitoso. Revisa tu correo"
                " electrónico para activar tu cuenta."
            )
        }
    except HttpError:
        raise
    except Exception as e:
        raise HttpError(500, f"Error al procesar el registro: {str(e)}")


# --- ACTIVAR CUENTA ---
@router.get("/auth/activate/{uidb64}/{token}", auth=None)
def activar_cuenta(request, uidb64: str, token: str):
    """
    Activa la cuenta del usuario usando el link enviado por correo.
    Al activar exitosamente, redirige al login del frontend.
    """
    frontend_url = os.environ.get(
        "FRONTEND_URL", "https://universitas-services-gcpe-hd31lcjin.vercel.app"
    )

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        raise HttpError(400, "Link de activación inválido")

    if user.is_active:
        # Ya estaba activada, redirigir al login
        return HttpResponseRedirect(f"{frontend_url}/login?activated=already")

    if not default_token_generator.check_token(user, token):
        raise HttpError(400, "El link de activación ha expirado o es inválido")

    user.is_active = True
    user.save()

    # Redirigir al login del frontend con parámetro de éxito
    return HttpResponseRedirect(f"{frontend_url}/login?activated=true")


# --- REENVIAR CORREO DE ACTIVACIÓN ---
@router.post("/auth/resend-activation", auth=None)
def reenviar_activacion(request, payload: PasswordResetRequestSchema):
    """
    Reenvía el correo de activación de cuenta.
    Usa el mismo schema de email del password-reset (solo necesita el email).
    """
    try:
        user = User.objects.get(email=payload.email)
        if not user.is_active:
            enviar_correo_activacion(user)
    except User.DoesNotExist:
        pass  # No revelamos si el email existe o no

    return {
        "message": (
            "Si el correo está registrado y la cuenta"
            " no ha sido activada, se ha enviado un"
            " nuevo enlace de activación."
        )
    }


# --- RECUPERACIÓN DE CONTRASEÑA (Paso 1: Enviar Correo HTML) ---
@router.post("/auth/password-reset", auth=None)
def request_password_reset(request, payload: PasswordResetRequestSchema):
    """
    Envía un correo HTML profesional con un link para restablecer la contraseña.
    """
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        return {"message": "Si el correo existe, se ha enviado un enlace."}

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/auth/reset-password/{uid}/{token}"

    # Usar el servicio de email con plantilla HTML
    enviar_correo_reset_password(user, reset_link)

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
