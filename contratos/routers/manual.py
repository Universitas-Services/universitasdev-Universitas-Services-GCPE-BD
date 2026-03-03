from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from ..schemas import ManualSchema

router = Router(tags=["📖 Manual de Normas"])


@router.post("/manual/pdf", auth=JWTAuth())
def generar_manual_pdf(request, payload: ManualSchema):
    """
    Recibe los 4 datos de configuración y genera el Manual en PDF.
    No guarda en BD, solo genera el documento al vuelo.
    """
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
