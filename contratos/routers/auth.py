import random
import uuid

from ninja import Router
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils import timezone
from django.http import HttpResponseRedirect
from datetime import timedelta
import os

from ..models import PerfilUsuario, CodigoResetPassword
from ..schemas import (
    UserRegisterSchema,
    PasswordResetRequestSchema,
    VerificarCodigoResetSchema,
    ResetPasswordConTokenSchema,
)
from ..email_service import enviar_correo_activacion, enviar_correo_codigo_reset

router = Router(tags=["🔐 Autenticación"])

# Tiempo de expiración del código OTP (5 minutos)
OTP_EXPIRACION_MINUTOS = 5


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


# ==============================================================================
# RECUPERACIÓN DE CONTRASEÑA CON OTP (3 PASOS)
# ==============================================================================


# --- PASO 1: Enviar código OTP al correo ---
@router.post("/auth/password-reset", auth=None)
def enviar_codigo_reset(request, payload: PasswordResetRequestSchema):
    """
    Paso 1: Envía un código OTP de 6 dígitos al correo del usuario.
    Si el correo no existe, responde igual (por seguridad).
    Invalida cualquier código OTP anterior del mismo usuario.
    """
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        # No revelamos si el email existe o no
        return {
            "message": "Si el correo existe, se ha enviado un código de verificación."
        }

    # Invalidar códigos OTP anteriores de este usuario
    CodigoResetPassword.objects.filter(user=user, usado=False).update(usado=True)

    # Generar código OTP de 6 dígitos
    codigo = str(random.randint(100000, 999999))

    # Guardar en BD
    CodigoResetPassword.objects.create(user=user, codigo=codigo)

    # Enviar correo con el código
    enviar_correo_codigo_reset(user, codigo)

    return {"message": "Si el correo existe, se ha enviado un código de verificación."}


# --- PASO 2: Verificar código OTP ---
@router.post("/auth/verify-reset-code", auth=None)
def verificar_codigo_reset(request, payload: VerificarCodigoResetSchema):
    """
    Paso 2: Verifica que el código OTP sea correcto y no haya expirado.
    Si es válido, genera un reset_token (UUID) que se usará en el paso 3.
    """
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        raise HttpError(400, "Código inválido o expirado.")

    # Buscar el último código OTP no usado para este usuario
    registro_otp = CodigoResetPassword.objects.filter(user=user, usado=False).first()

    if not registro_otp:
        raise HttpError(400, "Código inválido o expirado.")

    # Verificar que no haya expirado (10 minutos)
    tiempo_limite = registro_otp.creado_en + timedelta(minutes=OTP_EXPIRACION_MINUTOS)
    if timezone.now() > tiempo_limite:
        registro_otp.usado = True
        registro_otp.save()
        raise HttpError(400, "El código ha expirado. Solicita uno nuevo.")

    # Verificar que el código coincida
    if registro_otp.codigo != payload.codigo:
        raise HttpError(400, "Código inválido o expirado.")

    # Generar reset_token (UUID) para autorizar el cambio de contraseña
    reset_token = str(uuid.uuid4())
    registro_otp.token_reset = reset_token
    registro_otp.save()

    return {
        "reset_token": reset_token,
        "message": "Código verificado correctamente.",
    }


# --- PASO 3: Cambiar contraseña con reset_token ---
@router.post("/auth/reset-password", auth=None)
def resetear_password(request, payload: ResetPasswordConTokenSchema):
    """
    Paso 3: Cambia la contraseña del usuario usando el reset_token
    obtenido en el paso 2. El token se invalida después de usarse.
    """
    # Buscar el registro OTP por reset_token, que no esté usado
    registro_otp = CodigoResetPassword.objects.filter(
        token_reset=payload.reset_token, usado=False
    ).first()

    if not registro_otp:
        raise HttpError(400, "Token inválido o expirado.")

    # Verificar que no haya expirado
    tiempo_limite = registro_otp.creado_en + timedelta(minutes=OTP_EXPIRACION_MINUTOS)
    if timezone.now() > tiempo_limite:
        registro_otp.usado = True
        registro_otp.save()
        raise HttpError(400, "El token ha expirado. Solicita un nuevo código.")

    # Cambiar la contraseña
    user = registro_otp.user
    user.set_password(payload.new_password)
    user.save()

    # Marcar el código como usado
    registro_otp.usado = True
    registro_otp.save()

    return {"message": "Contraseña actualizada exitosamente."}


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
