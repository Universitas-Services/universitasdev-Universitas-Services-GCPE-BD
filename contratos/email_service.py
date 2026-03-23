"""
Servicio centralizado de envío de correos electrónicos.
Usa la API HTTP de Resend (no SMTP, porque Render bloquea
los puertos SMTP 25/465/587).
"""

import os
import base64
import resend
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def _get_frontend_url():
    """Obtiene la URL del frontend desde las variables de entorno."""
    return os.environ.get(
        "FRONTEND_URL", "https://universitas-services-gcpe-hd31lcjin.vercel.app"
    )


def _get_backend_url():
    """Obtiene la URL del backend desde las variables de entorno."""
    return os.environ.get("BACKEND_URL", "http://localhost:8000")


def _get_from_email():
    """Obtiene el email remitente."""
    return os.environ.get("DEFAULT_FROM_EMAIL", "onboarding@resend.dev")


def _init_resend():
    """Configura la API key de Resend."""
    resend.api_key = os.environ.get("RESEND_API_KEY", "dummy-key")


def enviar_correo_activacion(user):
    """
    Envía un correo con un link para activar la cuenta.
    El link apunta directamente al endpoint del backend.
    """
    _init_resend()

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    backend_url = _get_backend_url()
    activation_link = f"{backend_url}/api/auth/activate/{uid}/{token}"

    html_content = render_to_string(
        "emails/activacion_cuenta.html",
        {
            "nombre": user.first_name or user.email,
            "activation_link": activation_link,
        },
    )

    resend.Emails.send(
        {
            "from": _get_from_email(),
            "to": [user.email],
            "subject": "Activa tu cuenta - Universitas",
            "html": html_content,
        }
    )


def enviar_correo_codigo_reset(user, codigo):
    """
    Envía un correo HTML con el código OTP de 6 dígitos
    para restablecer la contraseña.
    """
    _init_resend()

    html_content = render_to_string(
        "emails/reset_password_otp.html",
        {
            "nombre": user.first_name or user.email,
            "codigo": codigo,
        },
    )

    resend.Emails.send(
        {
            "from": _get_from_email(),
            "to": [user.email],
            "subject": "Código de verificación - Universitas",
            "html": html_content,
        }
    )


def enviar_correo_con_pdf(
    user, asunto, mensaje_tipo, pdf_bytes, nombre_archivo, destinatario_email=None
):
    """
    Envía un correo con un archivo PDF adjunto.
    Usado para enviar Manual y reportes de Compliance.
    Si se pasa destinatario_email, se envía a ese correo en vez del usuario.
    """
    _init_resend()

    email_destino = destinatario_email or user.email

    html_content = render_to_string(
        "emails/envio_documento.html",
        {
            "nombre": user.first_name or user.email,
            "tipo_documento": mensaje_tipo,
            "nombre_archivo": nombre_archivo,
        },
    )

    # Resend espera el contenido del adjunto en base64
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

    resend.Emails.send(
        {
            "from": _get_from_email(),
            "to": [email_destino],
            "subject": asunto,
            "html": html_content,
            "attachments": [
                {
                    "filename": nombre_archivo,
                    "content": pdf_b64,
                }
            ],
        }
    )
