from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import get_object_or_404
from typing import List


# Importaciones locales
from .models import Proveedor, ComplianceExpediente
from .schemas import ProveedorSchema, ComplianceSchema, ComplianceOut, ManualSchema
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


@api.get("/proveedores", response=List[ProveedorSchema], auth=JWTAuth())
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
