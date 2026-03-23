# Register your models here.

from django.contrib import admin
from .models import (
    PerfilUsuario,
    ManualConfiguracion,
    Proveedor,
    ComplianceExpediente,
    CodigoResetPassword,
)


# 1. Configuración para el Perfil de Usuario
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "cargo", "nombre_institucion_ente", "telefono")
    search_fields = ("user__username", "cargo")


# 2. Configuración para Manuales
@admin.register(ManualConfiguracion)
class ManualConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("nombre_institucion_ente", "siglas_institucion_ente", "usuario")


# 3. Configuración para Proveedores (¡La más importante!)
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista
    list_display = (
        "nombre_proveedor",
        "rif_proveedor",
        "correo_proveedor",
        "nivel_contratacion",
        "fecha_registro",
    )
    # Barra de búsqueda para encontrar rápido por RIF o Nombre
    search_fields = ("nombre_proveedor", "rif_proveedor", "correo_proveedor")
    # Filtros laterales
    list_filter = ("nivel_contratacion", "tipo_persona", "estado")


# 4. Configuración para Reportes/Compliance
@admin.register(ComplianceExpediente)
class ComplianceExpedienteAdmin(admin.ModelAdmin):
    list_display = (
        "nomenclatura",
        "nombre_organo_entidad",
        "fecha_revision",
        "usuario_revisor",
    )
    search_fields = ("nomenclatura", "nombre_organo_entidad")
    list_filter = ("fecha_revision",)


# 5. Configuración para Códigos OTP de Reset de Contraseña
@admin.register(CodigoResetPassword)
class CodigoResetPasswordAdmin(admin.ModelAdmin):
    list_display = ("user", "codigo", "creado_en", "usado")
    search_fields = ("user__email", "codigo")
    list_filter = ("usado", "creado_en")
