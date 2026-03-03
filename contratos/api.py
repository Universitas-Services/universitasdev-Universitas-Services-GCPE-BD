from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from .routers.auth import router as auth_router
from .routers.perfil import router as perfil_router
from .routers.proveedores import router as proveedores_router
from .routers.compliance import router as compliance_router
from .routers.manual import router as manual_router

# Inicializamos la API
api = NinjaExtraAPI(title="Sistema de Contrataciones")

# JWT Login/Refresh (auto-registrado por NinjaJWT)
api.register_controllers(NinjaJWTDefaultController)

# --- Routers organizados por dominio ---
api.add_router("", auth_router)
api.add_router("", perfil_router)
api.add_router("", proveedores_router)
api.add_router("", compliance_router)
api.add_router("", manual_router)
