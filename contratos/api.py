from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja.errors import ValidationError
from django.http import JsonResponse

from .routers.auth import router as auth_router
from .routers.perfil import router as perfil_router
from .routers.proveedores import router as proveedores_router
from .routers.compliance import router as compliance_router
from .routers.manual import router as manual_router

# Inicializamos la API
api = NinjaExtraAPI(title="Sistema de Contrataciones")

# --- DICCIONARIO DE TRADUCCIONES (Pydantic → Español) ---
TRADUCCIONES = {
    "Field required": "Este campo es obligatorio",
    "field required": "Este campo es obligatorio",
    "value is not a valid email address": "El correo electrónico no es válido",
    "Value error, ": "",
    "Input should be a valid string": "Este campo debe ser texto",
    "Input should be a valid integer": "Este campo debe ser un número entero",
    "Input should be a valid number": "Este campo debe ser un número",
    "String should have at least": "El texto debe tener al menos",
    "ensure this value has at least": "Este valor debe tener al menos",
    "ensure this value has at most": "Este valor debe tener como máximo",
    "value is not a valid integer": "El valor debe ser un número entero",
    "value is not a valid float": "El valor debe ser un número decimal",
    "none is not an allowed value": "Este campo no puede estar vacío",
    "Input should be": "El valor debe ser",
}


def traducir_mensaje(mensaje: str) -> str:
    """Traduce un mensaje de error de Pydantic al español."""
    for ingles, espanol in TRADUCCIONES.items():
        if ingles in mensaje:
            mensaje = mensaje.replace(ingles, espanol)
    return mensaje


# --- HANDLER GLOBAL: Errores de validación en español ---
@api.exception_handler(ValidationError)
def errores_validacion_en_espanol(request, exc):
    """
    Intercepta los errores de validación de Pydantic/Ninja
    y los devuelve en español con un formato limpio.
    """
    errores = []
    for error in exc.errors:
        # Obtener el nombre del campo
        campo = error.get("loc", ["general"])[-1]
        if isinstance(campo, int):
            campo = (
                error.get("loc", ["general"])[-2]
                if len(error.get("loc", [])) > 1
                else "general"
            )

        # Obtener y traducir el mensaje
        mensaje = error.get("msg", "Error de validación")
        mensaje = traducir_mensaje(mensaje)

        errores.append({"campo": str(campo), "mensaje": mensaje})

    return JsonResponse({"errores": errores}, status=422)


# JWT Login/Refresh (auto-registrado por NinjaJWT)
api.register_controllers(NinjaJWTDefaultController)

# --- Routers organizados por dominio ---
api.add_router("", auth_router)
api.add_router("", perfil_router)
api.add_router("", proveedores_router)
api.add_router("", compliance_router)
api.add_router("", manual_router)
