from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string

from ..schemas import ManualSchema
from ..email_service import enviar_correo_con_pdf

router = Router(tags=["📖 Manual de Normas"])


@router.post("/manual/pdf", auth=JWTAuth())
def generar_manual_pdf(request, payload: ManualSchema):
    """
    Recibe los 4 datos de configuración y genera el Manual en PDF.
    No guarda en BD, solo genera el documento al vuelo.
    """
    from weasyprint import HTML

    data_context = payload.dict()

    html_string = render_to_string(
        "reportes/manual_concurso_abierto.html", data_context
    )

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    nombre_archivo = f"Manual_Normas_{payload.siglas_institucion_ente}.pdf"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{nombre_archivo}"'  # noqa: E702

    return response


@router.post("/manual/enviar-email", auth=JWTAuth())
def enviar_manual_por_email(request, payload: ManualSchema):
    """
    Genera el Manual en PDF y lo envía por correo electrónico
    al correo indicado por el usuario en el formulario.
    """
    data_context = payload.dict()

    from weasyprint import HTML

    html_string = render_to_string(
        "reportes/manual_concurso_abierto.html", data_context
    )
    pdf_bytes = HTML(string=html_string).write_pdf()

    nombre_archivo = f"Manual_Normas_{payload.siglas_institucion_ente}.pdf"

    enviar_correo_con_pdf(
        user=request.auth,
        asunto=f"Manual de Normas - {payload.siglas_institucion_ente}",
        mensaje_tipo="Manual de Normas de Contrataciones",
        pdf_bytes=pdf_bytes,
        nombre_archivo=nombre_archivo,
        destinatario_email=payload.correo_electronico_manual,
    )

    return {
        "message": (f"El manual ha sido enviado a {payload.correo_electronico_manual}")
    }
