from ninja import ModelSchema
from pydantic import field_validator
from datetime import date
import re
from .models import Proveedor, ComplianceExpediente, ManualConfiguracion


# ==========================================
# ESQUEMA DE PROVEEDORES (CORREGIDO)
# ==========================================
class ProveedorSchema(ModelSchema):
    class Meta:
        model = Proveedor
        exclude = ["creado_por", "fecha_registro"]

    # 1. RIF (Nombre exacto: rif_proveedor)
    @field_validator("rif_proveedor")
    def validar_rif(cls, v):
        if not v:
            return v
        patron = r"^[VEJPGvejpg]-\d{8}-\d$"
        if not re.match(patron, v):
            raise ValueError("El RIF debe tener el formato correcto (Ej: J-12345678-0)")
        return v.upper()

    # 2. TELÉFONO (Nombre exacto: telefono_proveedor)
    @field_validator("telefono_proveedor")
    def validar_telefono(cls, v):
        if not v:
            return v
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        if len(v) not in [10, 11]:
            raise ValueError("El teléfono debe tener 10 u 11 dígitos.")
        return v

    # 3. CORREO (Nombre exacto: correo_proveedor)
    @field_validator("correo_proveedor")
    def validar_correo(cls, v):
        if not v:
            return v
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, v):
            raise ValueError("Email inválido.")
        return v.lower()

    # 4. AÑOS DE EXPERIENCIA (Nombre exacto: anos_experiencia)
    @field_validator("anos_experiencia")
    def validar_experiencia(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("Los años de experiencia no pueden ser negativos.")
        return v

    # 5. FECHAS (Nombre exacto: fecha_estado_financiero)
    @field_validator("fecha_estado_financiero")
    def validar_fechas_pasadas(cls, v):
        if not v:
            return v
        if v > date.today():
            raise ValueError("La fecha no puede ser futura.")
        return v

    # 6. NIVEL (Nombre exacto: nivel_contratacion)
    @field_validator("nivel_contratacion")
    def validar_nivel(cls, v):
        if not v:
            return v
        niveles_validos = ["ALTA", "MEDIA", "BAJA"]
        if v.upper() not in niveles_validos:
            raise ValueError(f'Nivel inválido. Opciones: {", ".join(niveles_validos)}')
        return v.upper()


# ==========================================
# ESQUEMAS DE COMPLIANCE Y MANUAL
# ==========================================
class ComplianceSchema(ModelSchema):
    class Meta:
        model = ComplianceExpediente
        exclude = ["id", "fecha_creacion", "usuario_revisor"]


class ComplianceOut(ModelSchema):
    class Meta:
        model = ComplianceExpediente
        fields = "__all__"


class ManualSchema(ModelSchema):
    class Meta:
        model = ManualConfiguracion
        fields = [
            "nombre_institucion_ente",
            "siglas_institucion_ente",
            "nombre_unidad_admin_financiera",
            "nombre_unidad_sistemas_tecnologia",
        ]
