from django.contrib import admin
from django.urls import path
from contratos.api import (
    api,
)  # <--- Importamos la API que YA TIENE la seguridad configurada

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),  # <--- Conectamos esa API a la web
]
