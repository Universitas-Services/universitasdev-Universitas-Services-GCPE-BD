from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string

from ..models import ComplianceExpediente
from ..schemas import ComplianceSchema
from ..services import generar_data_para_pdf
from ..email_service import enviar_correo_con_pdf

router = Router(tags=["📋 Compliance"])


@router.post("/compliance/pdf", auth=JWTAuth())
def generar_compliance_pdf(request, payload: ComplianceSchema):
    """
    Recibe los datos del formulario de compliance y genera el PDF.
    No guarda en BD, solo genera el documento al vuelo.
    """
    from weasyprint import HTML

    # Crear objeto en memoria (sin guardar en BD) para reutilizar generar_data_para_pdf
    reporte = ComplianceExpediente(**payload.dict())

    data_context = generar_data_para_pdf(reporte)
    html_string = render_to_string("reportes/hallazgos.html", data_context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    nombre_archivo = f"Reporte_Hallazgos_{payload.nomenclatura}.pdf"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{nombre_archivo}"'  # noqa: E702

    return response


@router.post("/compliance/enviar-email", auth=JWTAuth())
def enviar_compliance_por_email(request, payload: ComplianceSchema):
    """
    Genera el PDF del reporte de compliance y lo envía por correo
    al email indicado en persona_contacto.
    """
    from weasyprint import HTML

    # Crear objeto en memoria (sin guardar en BD)
    reporte = ComplianceExpediente(**payload.dict())

    data_context = generar_data_para_pdf(reporte)
    html_string = render_to_string("reportes/hallazgos.html", data_context)
    pdf_bytes = HTML(string=html_string).write_pdf()

    nombre_archivo = f"Reporte_Hallazgos_{payload.nomenclatura}.pdf"

    enviar_correo_con_pdf(
        user=request.auth,
        asunto=f"Reporte de Compliance - {payload.nomenclatura}",
        mensaje_tipo="Reporte de Compliance (Hallazgos)",
        pdf_bytes=pdf_bytes,
        nombre_archivo=nombre_archivo,
        destinatario_email=payload.persona_contacto,
    )

    return {"message": f"El reporte ha sido enviado a {payload.persona_contacto}"}
