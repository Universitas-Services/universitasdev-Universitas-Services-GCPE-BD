from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import List

from ..models import Proveedor
from ..schemas import ProveedorSchema, ProveedorOut

router = Router(tags=["🏢 Proveedores"])


@router.post("/proveedores", auth=JWTAuth())
def crear_proveedor(request, payload: ProveedorSchema):
    """
    Crea un nuevo proveedor asociado al usuario logueado.
    """
    usuario_actual = request.auth
    proveedor = Proveedor.objects.create(creado_por=usuario_actual, **payload.dict())
    return {"id": proveedor.id, "mensaje": "Proveedor creado exitosamente"}


@router.get("/proveedores", response=List[ProveedorOut], auth=JWTAuth())
def listar_proveedores(request):
    """
    Lista los proveedores creados por el usuario logueado.
    """
    return Proveedor.objects.filter(creado_por=request.auth)
