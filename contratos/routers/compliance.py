from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from typing import List

from ..models import ComplianceExpediente
from ..schemas import ComplianceSchema, ComplianceOut
from ..services import generar_data_para_pdf
from ..email_service import enviar_correo_con_pdf

router = Router(tags=["📋 Compliance"])


@router.post("/compliance", response=ComplianceOut, auth=JWTAuth())
def crear_reporte_compliance(request, payload: ComplianceSchema):
    """
    Crea un nuevo reporte de auditoría de compliance.
    El auditor es el usuario logueado.
    """
    usuario_auditor = request.auth
    reporte = ComplianceExpediente.objects.create(
        usuario_revisor=usuario_auditor, **payload.dict()
    )
    return reporte


@router.get("/compliance", response=List[ComplianceOut], auth=JWTAuth())
def listar_reportes_compliance(request):
    """
    Lista los reportes de compliance del usuario logueado.
    """
    return ComplianceExpediente.objects.filter(usuario_revisor=request.auth)


@router.get("/compliance/{id}/pdf", auth=JWTAuth())
def descargar_pdf_compliance(request, id: int):
    """
    Genera y descarga el reporte de hallazgos en formato PDF.
    """
    reporte = get_object_or_404(
        ComplianceExpediente, id=id, usuario_revisor=request.auth
    )

    from weasyprint import HTML

    data_context = generar_data_para_pdf(reporte)
    html_string = render_to_string("reportes/hallazgos.html", data_context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    nombre_archivo = f"Reporte_Hallazgos_{reporte.nomenclatura}.pdf"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{nombre_archivo}"'  # noqa: E702

    return response


@router.post("/compliance/{id}/enviar-email", auth=JWTAuth())
def enviar_compliance_por_email(request, id: int):
    """
    Genera el PDF del reporte de compliance y lo envía por correo
    al email del usuario logueado.
    """
    reporte = get_object_or_404(
        ComplianceExpediente, id=id, usuario_revisor=request.auth
    )

    from weasyprint import HTML

    # Generar el PDF (misma lógica que descargar_pdf_compliance)
    data_context = generar_data_para_pdf(reporte)
    html_string = render_to_string("reportes/hallazgos.html", data_context)
    pdf_bytes = HTML(string=html_string).write_pdf()

    nombre_archivo = f"Reporte_Hallazgos_{reporte.nomenclatura}.pdf"

    enviar_correo_con_pdf(
        user=request.auth,
        asunto=f"Reporte de Compliance - {reporte.nomenclatura}",
        mensaje_tipo="Reporte de Compliance (Hallazgos)",
        pdf_bytes=pdf_bytes,
        nombre_archivo=nombre_archivo,
    )

    return {"message": f"El reporte ha sido enviado a {request.auth.email}"}
