from ninja import ModelSchema
from .models import Proveedor, ComplianceExpediente


# Esquema para PROVEEDORES
class ProveedorSchema(ModelSchema):
    class Meta:  # <--- ANTES ERA 'Config', AHORA ES 'Meta'
        model = Proveedor
        exclude = ["creado_por", "fecha_registro"]


# Esquema para CREAR el reporte (Input)
class ComplianceSchema(ModelSchema):
    class Meta:  # <--- ANTES ERA 'Config', AHORA ES 'Meta'
        model = ComplianceExpediente
        exclude = ["id", "fecha_creacion", "usuario_revisor"]


# Esquema para MOSTRAR el reporte (Output)
class ComplianceOut(ModelSchema):
    class Meta:  # <--- ANTES ERA 'Config', AHORA ES 'Meta'
        model = ComplianceExpediente
        fields = "__all__"
