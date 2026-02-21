from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import get_object_or_404
from typing import List
from django.db import transaction
from .models import PerfilUsuario

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from ninja.errors import HttpError

# Imports para recuperación de contraseña
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
import os  # Para leer el FRONTEND_URL del sistema

# Importaciones locales
from .models import Proveedor, ComplianceExpediente
from .schemas import (
    ProveedorSchema,
    ProveedorOut,
    ComplianceSchema,
    ComplianceOut,
    ManualSchema,
    UserProfileSchema,
    UserRegisterSchema,
    PasswordResetRequestSchema,  # <--- NUEVO
)
from .services import generar_data_para_pdf

# Inicializamos la API
api = NinjaExtraAPI(title="Sistema de Contrataciones")

# --- MÓDULO DE AUTENTICACIÓN (LOGIN) ---
# Esto crea las rutas /api/auth/token (para login) y /api/auth/refresh
api.register_controllers(NinjaJWTDefaultController)

# --- ENDPOINTS DE PROVEEDORES ---


@api.post("/proveedores", auth=JWTAuth())
def crear_proveedor(request, payload: ProveedorSchema):
    # SEGURIDAD REAL: Obtenemos el usuario del Token
    usuario_actual = request.auth

    proveedor = Proveedor.objects.create(
        creado_por=usuario_actual, **payload.dict()  # <--- Usamos el usuario real
    )
    return {"id": proveedor.id, "mensaje": "Proveedor creado exitosamente"}


@api.get("/proveedores", response=List[ProveedorOut], auth=JWTAuth())
def listar_proveedores(request):
    return Proveedor.objects.all()


# --- ENDPOINTS DE COMPLIANCE (AUDITORÍA) ---


@api.post("/compliance", response=ComplianceOut, auth=JWTAuth())
def crear_reporte_compliance(request, payload: ComplianceSchema):
    # SEGURIDAD REAL: El auditor es quien está logueado
    usuario_auditor = request.auth

    reporte = ComplianceExpediente.objects.create(
        usuario_revisor=usuario_auditor, **payload.dict()  # <--- Usamos el usuario real
    )
    return reporte


@api.get("/compliance", response=List[ComplianceOut], auth=JWTAuth())
def listar_reportes_compliance(request):
    return ComplianceExpediente.objects.all()


@api.get("/compliance/{id}/pdf", auth=JWTAuth())
def descargar_pdf_compliance(request, id: int):
    # 1. Buscamos el reporte
    reporte = get_object_or_404(ComplianceExpediente, id=id)

    # 2. Generamos la data inteligente (Puntos y textos legales)
    data_context = generar_data_para_pdf(reporte)

    # 3. Renderizamos el HTML
    html_string = render_to_string("reportes/hallazgos.html", data_context)

    # 4. Convertimos a PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # 5. Respuesta de descarga
    response = HttpResponse(pdf_file, content_type="application/pdf")
    nombre_archivo = f"Reporte_Hallazgos_{reporte.nomenclatura}.pdf"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{nombre_archivo}"'  # noqa: E702

    return response


# --- ENDPOINT DE MANUAL DE NORMAS ---


@api.post("/manual/pdf", auth=JWTAuth())
def generar_manual_pdf(request, payload: ManualSchema):
    """
    Recibe los 4 datos de configuración y genera el Manual en PDF.
    No guarda en BD (por ahora), solo genera el documento al vuelo.
    """
    # 1. Preparamos el contexto (Diccionario de variables)
    #    WeasyPrint usará esto para reemplazar {{ nombre_institucion_ente }} en el HTML
    data_context = payload.dict()

    # 2. Renderizamos el HTML
    #    Nota: Crearemos este archivo 'manual_concurso_abierto.html' en el siguiente paso
    html_string = render_to_string(
        "reportes/manual_concurso_abierto.html", data_context
    )

    # 3. Convertimos a PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # 4. Respuesta de descarga
    response = HttpResponse(pdf_file, content_type="application/pdf")
    nombre_archivo = f"Manual_Normas_{payload.siglas_institucion_ente}.pdf"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{nombre_archivo}"'  # noqa: E702

    return response


# --- ENDPOINT DE PERFIL DE USUARIO ---
@api.get("/me", response=UserProfileSchema, auth=JWTAuth())
def obtener_perfil(request):
    """
    Devuelve los datos del usuario logueado basándose en su Token.
    """
    return request.auth


#  El Endpoint de Registro
@api.post("/auth/register", response=UserProfileSchema, auth=None)
def registrar_usuario(request, payload: UserRegisterSchema):
    """
    Registro público. Crea Usuario y Perfil (con teléfono).
    """
    # Validar si el correo ya existe
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "El correo electrónico ya está registrado")

    try:
        # Usamos transaction.atomic para que si falla el perfil
        with transaction.atomic():
            # 1. Crear el Usuario Base
            user = User.objects.create(
                username=payload.email,  # <--- Usamos el email como username
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                password=make_password(payload.password),
            )

            # 2. Crear (o actualizar) el Perfil con el Teléfono
            # Usamos update_or_create por seguridad, aunque create bastaría.
            PerfilUsuario.objects.update_or_create(
                user=user, defaults={"telefono": payload.telefono}
            )

            return user

    except Exception as e:
        raise HttpError(500, f"Error al procesar el registro: {str(e)}")


# --- RECUPERACIÓN DE CONTRASEÑA (Paso 1: Enviar Correo) ---
@api.post("/auth/password-reset", auth=None)
def request_password_reset(request, payload: PasswordResetRequestSchema):
    """
    Envía un correo con un link para restablecer la contraseña.
    """
    # 1. Buscar al usuario (Si no existe, no decimos nada por seguridad)
    try:
        user = User.objects.get(email=payload.email)
    except User.DoesNotExist:
        # Retornamos éxito falso para no revelar qué correos existen
        return {"message": "Si el correo existe, se ha enviado un enlace."}

    # 2. Generar el Token y el ID codificado
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # 3. Construir el Link del Frontend
    # El link será tipo: http://localhost:3000/auth/reset-password/MjQ/bx3-12345
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/auth/reset-password/{uid}/{token}"

    # 4. Enviar el correo
    asunto = "Restablecer contraseña - Universitas"
    mensaje = f"""
    Hola{user.first_name}, Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace: {reset_link}

    Si no fuiste tú, ignora este mensaje.
    """

    send_mail(asunto, mensaje, None, [user.email], fail_silently=False)

    return {"message": "Si el correo existe, se ha enviado un enlace."}
