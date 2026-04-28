import math
import uuid
from typing import List, Dict, Any

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from ninja import Router, Schema
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.contrib.auth.models import User
from ..models import Proveedor, ComplianceExpediente, ManualConfiguracion, NotaCRM
from ..schemas import (
    UsuarioAdminPaginadoOut,
    ProveedorPaginadoOut,
    CompliancePaginadoOut,
    ManualPaginadoOut,
    NotaCRMIn,
    NotaCRMOut,
    NotaCRMPaginadaOut,
)
from ..services import generar_data_para_pdf
from ..email_service import enviar_correo_con_pdf

router = Router(tags=["📈 Administrador (Dashboard)"])

# --- SCHEMAS DE SALIDA ---


class KPIMetrics(Schema):
    total_usuarios: int
    total_proveedores: int
    auditorias_compliance: int
    generacion_manuales: int


class SpecialtyData(Schema):
    label: str
    valor: int


class ActivityData(Schema):
    mes: str
    usuarios: int


class DashboardDataOut(Schema):
    kpis: KPIMetrics
    charts: Dict[str, List[Any]]


@router.get("/dashboard", response=DashboardDataOut, auth=JWTAuth())
def get_dashboard_data(request):
    """
    Retorna toda la información necesaria para el Dashboard administrativo:
    KPIs y datos para gráficos de especialidad y registros recientes.
    """
    user = request.auth

    # Validar que el usuario tenga permisos administrativos
    if not user.is_staff and not user.is_superuser:
        raise HttpError(
            403, "No tienes permisos de administrador para ver estas métricas"
        )

    # 1. CÁLCULO DE KPIs
    kpis = {
        "total_usuarios": User.objects.count(),
        "total_proveedores": Proveedor.objects.count(),
        "auditorias_compliance": User.objects.filter(complianceexpediente__isnull=False)
        .distinct()
        .count(),
        "generacion_manuales": User.objects.filter(manualconfiguracion__isnull=False)
        .distinct()
        .count(),
    }

    # 2. GRÁFICO: ÁREA DE ESPECIALIDAD
    # Mapeamos "Servicio" a "Servicios" para que coincida con la interfaz del usuario
    especialidades_raw = Proveedor.objects.values("area_especialidad").annotate(
        total=Count("id")
    )

    # Inicializamos con 0 para asegurar que siempre aparezcan las 3 categorías
    especialidad_dict = {"Bienes": 0, "Obras": 0, "Servicios": 0}
    for item in especialidades_raw:
        label = item["area_especialidad"]
        if label == "Servicio":
            label = "Servicios"
        if label in especialidad_dict:
            especialidad_dict[label] += item["total"]

    chart_especialidad = [
        {"label": k, "valor": v} for k, v in especialidad_dict.items()
    ]

    # 3. GRÁFICO: ACTIVIDAD RECIENTE (Últimos 6 meses)
    # Obtenemos registros agrupados por mes
    seis_meses_atras = timezone.now() - timezone.timedelta(days=180)
    registros_mensuales = (
        User.objects.filter(date_joined__gte=seis_meses_atras)
        .annotate(mes_registro=TruncMonth("date_joined"))
        .values("mes_registro")
        .annotate(cantidad=Count("id"))
        .order_by("mes_registro")
    )

    # Formatear meses para el frontend (Ene, Feb, etc.)
    MESES_MAP = {
        1: "Ene",
        2: "Feb",
        3: "Mar",
        4: "Abr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dic",
    }

    chart_actividad = []
    for reg in registros_mensuales:
        if reg["mes_registro"]:
            mes_nombre = MESES_MAP.get(
                reg["mes_registro"].month, str(reg["mes_registro"].month)
            )
            chart_actividad.append({"mes": mes_nombre, "usuarios": reg["cantidad"]})

    return {
        "kpis": kpis,
        "charts": {
            "especialidad": chart_especialidad,
            "actividad_reciente": chart_actividad,
        },
    }


# --- NUEVOS ENDPOINTS ADMINISTRATIVOS ---


@router.get("/usuarios", response=UsuarioAdminPaginadoOut, auth=JWTAuth())
def listar_usuarios(request, q: str = None, page: int = 1, page_size: int = 10):
    """
    Lista usuarios con paginación y búsqueda por nombre o email.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = User.objects.all()
    if q:
        queryset = queryset.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset.order_by("-date_joined")[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get(
    "/usuarios/{user_id}/proveedores", response=ProveedorPaginadoOut, auth=JWTAuth()
)
def listar_proveedores_usuario(
    request, user_id: int, q: str = None, page: int = 1, page_size: int = 10
):
    """
    Lista proveedores de un usuario específico.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = Proveedor.objects.filter(creado_por_id=user_id, activo=True)
    if q:
        queryset = queryset.filter(
            Q(nombre_proveedor__icontains=q)
            | Q(rif_proveedor__icontains=q)
            | Q(area_especialidad__icontains=q)
        )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset.order_by("-fecha_registro")[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.get(
    "/usuarios/{user_id}/compliance", response=CompliancePaginadoOut, auth=JWTAuth()
)
def listar_compliance_usuario(
    request, user_id: int, q: str = None, page: int = 1, page_size: int = 10
):
    """
    Lista auditorías de compliance de un usuario específico.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = ComplianceExpediente.objects.filter(usuario_revisor_id=user_id)
    if q:
        queryset = queryset.filter(
            Q(nomenclatura__icontains=q) | Q(nombre_organo_entidad__icontains=q)
        )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset.order_by("-fecha_creacion")[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post("/compliance/{compliance_id}/reenviar", auth=JWTAuth())
def reenviar_compliance(request, compliance_id: uuid.UUID):
    """
    Regenera y reenvía el reporte de compliance por correo.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    reporte = get_object_or_404(ComplianceExpediente, id=compliance_id)

    from weasyprint import HTML

    data_context = generar_data_para_pdf(reporte)
    html_string = render_to_string("reportes/hallazgos.html", data_context)
    pdf_bytes = HTML(string=html_string).write_pdf()

    nombre_archivo = f"Reporte_Hallazgos_{reporte.nomenclatura}.pdf"

    enviar_correo_con_pdf(
        user=user,
        asunto=f"Reporte de Compliance - {reporte.nomenclatura}",
        mensaje_tipo="Reporte de Compliance (Hallazgos)",
        pdf_bytes=pdf_bytes,
        nombre_archivo=nombre_archivo,
        destinatario_email=reporte.persona_contacto,
    )

    return {"message": f"El reporte ha sido reenviado a {reporte.persona_contacto}"}


@router.get("/usuarios/{user_id}/manuales", response=ManualPaginadoOut, auth=JWTAuth())
def listar_manuales_usuario(
    request, user_id: int, q: str = None, page: int = 1, page_size: int = 10
):
    """
    Lista configuraciones de manuales de un usuario específico.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = ManualConfiguracion.objects.filter(usuario_id=user_id)
    if q:
        queryset = queryset.filter(
            Q(nombre_institucion_ente__icontains=q)
            | Q(siglas_institucion_ente__icontains=q)
        )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset.order_by("-id")[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post("/manuales/{manual_id}/reenviar", auth=JWTAuth())
def reenviar_manual(request, manual_id: uuid.UUID):
    """
    Regenera y reenvía el manual por correo.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    manual = get_object_or_404(ManualConfiguracion, id=manual_id)

    data_context = {
        "nombre_institucion_ente": manual.nombre_institucion_ente,
        "siglas_institucion_ente": manual.siglas_institucion_ente,
        "nombre_unidad_admin_financiera": manual.nombre_unidad_admin_financiera,
        "nombre_unidad_sistemas_tecnologia": manual.nombre_unidad_sistemas_tecnologia,
        "correo_electronico_manual": manual.correo_electronico_manual,
    }

    from weasyprint import HTML

    html_string = render_to_string(
        "reportes/manual_concurso_abierto.html", data_context
    )
    pdf_bytes = HTML(string=html_string).write_pdf()

    nombre_archivo = f"Manual_Normas_{manual.siglas_institucion_ente}.pdf"

    enviar_correo_con_pdf(
        user=user,
        asunto=f"Manual de Normas - {manual.siglas_institucion_ente}",
        mensaje_tipo="Manual de Normas de Contrataciones",
        pdf_bytes=pdf_bytes,
        nombre_archivo=nombre_archivo,
        destinatario_email=manual.correo_electronico_manual,
    )

    return {
        "message": f"El manual ha sido reenviado a {manual.correo_electronico_manual}"
    }


# --- CRUD NOTAS CRM ---


@router.get("/notas", response=NotaCRMPaginadaOut, auth=JWTAuth())
def listar_todas_las_notas(request, q: str = None, page: int = 1, page_size: int = 10):
    """
    Lista TODAS las notas del sistema (útil para una vista global de CRM).
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = NotaCRM.objects.select_related("autor", "usuario_objetivo").all()
    if q:
        queryset = queryset.filter(
            Q(contenido__icontains=q)
            | Q(etiqueta__icontains=q)
            | Q(usuario_objetivo__username__icontains=q)
        )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.post("/usuarios/{user_id}/notas", response=NotaCRMOut, auth=JWTAuth())
def crear_nota(request, user_id: int, payload: NotaCRMIn):
    """
    Crea una nueva nota para un usuario específico.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    usuario_objetivo = get_object_or_404(User, id=user_id)
    nota = NotaCRM.objects.create(
        usuario_objetivo=usuario_objetivo,
        autor=user,
        contenido=payload.contenido,
        etiqueta=payload.etiqueta,
    )
    return nota


@router.get("/usuarios/{user_id}/notas", response=NotaCRMPaginadaOut, auth=JWTAuth())
def listar_notas_usuario(request, user_id: int, page: int = 1, page_size: int = 10):
    """
    Lista las notas asociadas a un usuario específico.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    queryset = NotaCRM.objects.select_related("autor", "usuario_objetivo").filter(
        usuario_objetivo_id=user_id
    )

    total = queryset.count()
    page_size = max(1, min(page_size, 100))
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))
    offset = (page - 1) * page_size
    items = list(queryset[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


@router.put("/notas/{nota_id}", response=NotaCRMOut, auth=JWTAuth())
def actualizar_nota(request, nota_id: uuid.UUID, payload: NotaCRMIn):
    """
    Actualiza el contenido o la etiqueta de una nota existente.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    nota = get_object_or_404(NotaCRM, id=nota_id)
    nota.contenido = payload.contenido
    nota.etiqueta = payload.etiqueta
    nota.save()
    return nota


@router.delete("/notas/{nota_id}", auth=JWTAuth())
def eliminar_nota(request, nota_id: uuid.UUID):
    """
    Elimina una nota existente.
    """
    user = request.auth
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "No tienes permisos de administrador")

    nota = get_object_or_404(NotaCRM, id=nota_id)
    nota.delete()
    return {"message": "Nota eliminada correctamente"}
