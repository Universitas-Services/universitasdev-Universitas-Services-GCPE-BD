from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML  # <--- La librería mágica para PDFs
from .services import generar_data_para_pdf # <--- Tu nuevo servicio
from typing import List
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ninja import Router
from .models import Proveedor, ComplianceExpediente
from .schemas import ProveedorSchema, ComplianceSchema

router = Router()

# --- ENDPOINTS DE PROVEEDORES ---

@router.post("/proveedores", response=ProveedorSchema)
def crear_proveedor(request, payload: ProveedorSchema):
    # TRUCO TEMPORAL: Usamos el primer usuario admin que exista
    usuario = User.objects.first()
    
    # Creamos el proveedor usando los datos del payload
    proveedor = Proveedor.objects.create(
        creado_por=usuario,
        **payload.dict()
    )
    return proveedor

@router.get("/proveedores", response=List[ProveedorSchema])
def listar_proveedores(request):
    return Proveedor.objects.all()

# --- ENDPOINTS DE COMPLIANCE (AUDITORÍA) ---

@router.post("/compliance", response=ComplianceSchema)
def crear_reporte_compliance(request, payload: ComplianceSchema):
    usuario = User.objects.first()
    
    reporte = ComplianceExpediente.objects.create(
        usuario_revisor=usuario,
        **payload.dict()
    )
    return reporte

@router.get("/compliance", response=List[ComplianceSchema])
def listar_reportes_compliance(request):
    return ComplianceExpediente.objects.all()

@router.get("/compliance/{id}/pdf")
def descargar_pdf_compliance(request, id: int):
    # a) Buscamos el reporte por ID (si no existe, da error 404 automático)
    reporte = get_object_or_404(ComplianceExpediente, id=id)

    # b) Llamamos a tu servicio para procesar la lógica (Puntos, Textos Legales, etc.)
    data_context = generar_data_para_pdf(reporte)

    # c) Inyectamos los datos en el HTML
    # Django buscará en contratos/templates/reportes/hallazgos.html
    html_string = render_to_string('reportes/hallazgos.html', data_context)

    # d) Generamos el PDF usando WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf()

    # e) Preparamos la respuesta para que el navegador descargue el archivo
    response = HttpResponse(pdf_file, content_type='application/pdf')
    
    # Esto le dice al navegador: "Descárgalo con este nombre"
    nombre_archivo = f"Reporte_Hallazgos_{reporte.nomenclatura}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    return response