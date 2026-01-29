from ninja import ModelSchema
from .models import Proveedor, ComplianceExpediente, ManualConfiguracion

# --- SCHEMA DE PROVEEDORES ---
class ProveedorSchema(ModelSchema):
    class Meta:
        model = Proveedor
        # Excluimos campos automáticos que no envía el usuario
        exclude = ['id', 'fecha_registro', 'creado_por']

# --- SCHEMA DE CONFIGURACIÓN (MANUAL) ---
class ManualConfiguracionSchema(ModelSchema):
    class Meta:
        model = ManualConfiguracion
        exclude = ['id', 'usuario']

# --- SCHEMA DE COMPLIANCE (AUDITORÍA) ---
class ComplianceSchema(ModelSchema):
    class Meta:
        model = ComplianceExpediente
        exclude = ['id', 'fecha_creacion', 'usuario_revisor']