"""
Servicio centralizado de envío de correos electrónicos.
Maneja: activación de cuenta, reset de contraseña, y envío de documentos PDF.
"""

import os
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings


def _get_frontend_url():
    """Obtiene la URL del frontend desde las variables de entorno."""
    return os.environ.get("FRONTEND_URL", "http://localhost:3000")


def _get_backend_url():
    """Obtiene la URL del backend desde las variables de entorno."""
    return os.environ.get("BACKEND_URL", "http://localhost:8000")


def enviar_correo_activacion(user):
    """
    Envía un correo con un link para activar la cuenta del usuario.
    El link apunta directamente al endpoint del backend.
    Genera un token seguro usando el default_token_generator de Django.
    """
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

    email = EmailMessage(
        subject="Activa tu cuenta - Universitas",
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)


def enviar_correo_reset_password(user, reset_link):
    """
    Envía un correo HTML profesional con el link para restablecer la contraseña.
    """
    html_content = render_to_string(
        "emails/reset_password.html",
        {
            "nombre": user.first_name or user.email,
            "reset_link": reset_link,
        },
    )

    email = EmailMessage(
        subject="Restablecer contraseña - Universitas",
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)


def enviar_correo_con_pdf(user, asunto, mensaje_tipo, pdf_bytes, nombre_archivo):
    """
    Envía un correo con un archivo PDF adjunto.
    Usado para enviar Manual y reportes de Compliance.

    Args:
        user: Usuario destinatario
        asunto: Asunto del correo
        mensaje_tipo: Tipo de documento ("manual" o "compliance")
        pdf_bytes: Bytes del PDF generado
        nombre_archivo: Nombre del archivo adjunto (ej: "Manual_Normas_XYZ.pdf")
    """
    html_content = render_to_string(
        "emails/envio_documento.html",
        {
            "nombre": user.first_name or user.email,
            "tipo_documento": mensaje_tipo,
            "nombre_archivo": nombre_archivo,
        },
    )

    email = EmailMessage(
        subject=asunto,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.attach(nombre_archivo, pdf_bytes, "application/pdf")
    email.send(fail_silently=False)
