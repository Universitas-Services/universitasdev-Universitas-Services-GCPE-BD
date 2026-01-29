from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from contratos.api import router as contratos_router  # <--- IMPORTANTE: Importar tu router

# 1. Creamos la instancia de la API
api = NinjaAPI(
    title="API de Contrataciones",
    version="1.0.0",
    description="Sistema de gestión de compliance y proveedores"
)

# 2. Registramos el router de tu app 'contratos'
api.add_router("/contratos/", contratos_router)

# 3. Agregamos la ruta al sistema
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),  # <--- ESTA LÍNEA ES LA QUE TE FALTA
]