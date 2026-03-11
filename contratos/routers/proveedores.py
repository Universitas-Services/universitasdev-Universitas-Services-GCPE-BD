import math
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.db.models import Q

from ..models import Proveedor
from ..schemas import ProveedorSchema, ProveedorPaginadoOut

router = Router(tags=["🏢 Proveedores"])


@router.post("/proveedores", auth=JWTAuth())
def crear_proveedor(request, payload: ProveedorSchema):
    """
    Crea un nuevo proveedor asociado al usuario logueado.
    """
    usuario_actual = request.auth
    proveedor = Proveedor.objects.create(creado_por=usuario_actual, **payload.dict())
    return {"id": proveedor.id, "mensaje": "Proveedor creado exitosamente"}


@router.get("/proveedores", response=ProveedorPaginadoOut, auth=JWTAuth())
def listar_proveedores(request, q: str = None, page: int = 1, page_size: int = 10):
    """
    Lista los proveedores del usuario logueado con paginación y búsqueda.
    - **q**: Busca por nombre, RIF o área de especialidad.
    - **page**: Número de página (default: 1).
    - **page_size**: Cantidad por página (default: 10).
    """
    queryset = Proveedor.objects.filter(creado_por=request.auth)

    # Búsqueda por nombre, RIF o área de especialidad
    if q:
        queryset = queryset.filter(
            Q(nombre_proveedor__icontains=q)
            | Q(rif_proveedor__icontains=q)
            | Q(area_especialidad__icontains=q)
        )

    # Paginación
    total = queryset.count()
    page_size = max(1, min(page_size, 100))  # Limitar entre 1 y 100
    pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, pages))  # Ajustar página al rango válido
    offset = (page - 1) * page_size

    items = list(queryset.order_by("-fecha_registro")[offset : offset + page_size])

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
