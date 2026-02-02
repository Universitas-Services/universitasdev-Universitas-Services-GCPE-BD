from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from contratos.api import router as contratos_router  # <--- Importamos esto

api = NinjaAPI(
    title="API de Contrataciones",
    version="1.0.0",
    description="Sistema de gestión de compliance y proveedores",
)

# Registramos el router bajo el prefijo /contratos
api.add_router("/contratos/", contratos_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
