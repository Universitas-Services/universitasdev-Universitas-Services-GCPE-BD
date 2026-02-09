from ninja import ModelSchema
from pydantic import field_validator
from datetime import date
import re
from .models import Proveedor, ComplianceExpediente, ManualConfiguracion


# Esquema para PROVEEDORES
class ProveedorOut(ModelSchema):
    class Meta:  # <--- ANTES ERA 'Config', AHORA ES 'Meta'
        model = Proveedor
        exclude = ["creado_por", "fecha_registro"]

    # 1. RIF: Formato estricto venezolano (Letra-8Digitos-1Digito)
    @field_validator("rif_proveedor")
    def validar_rif(cls, v):
        if not v:
            return v
        # Regex: Empieza con V,E,J,P,G (mayus/minus), guion, 8 nums, guion, 1 num
        patron = r"^[VEJPGvejpg]-\d{8}-\d$"
        if not re.match(patron, v):
            raise ValueError("El RIF debe tener el formato correcto (Ej: J-12345678-0)")
        return v.upper()  # Lo guardamos siempre en mayúsculas

    # 2. TELÉFONO: Solo números y 10 u 11 dígitos (ajustado a celulares Vzla)
    @field_validator("telefono")
    def validar_telefono(cls, v):
        if not v:
            return v
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        if len(v) not in [10, 11]:  # Aceptamos 0414... (11) o sin el 0 inicial (10)
            raise ValueError("El teléfono debe tener 10 u 11 dígitos.")
        return v

    # 3. CORREO: Formato Email
    @field_validator("correo_proveedor")
    def validar_correo(cls, v):
        if not v:
            return v
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, v):
            raise ValueError("Email inválido.")
        return v.lower()  # Guardar siempre en minúsculas

    # 4. AÑOS DE EXPERIENCIA: No puede ser negativo
    @field_validator("años_experiencia")
    def validar_experiencia(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("Los años de experiencia no pueden ser negativos.")
        return v

    # 5. FECHAS: No pueden ser futuras (Ej: Estado Financiero)
    @field_validator("fecha_estado_financiero")
    def validar_fechas_pasadas(cls, v):
        if not v:
            return v
        if v > date.today():
            raise ValueError("La fecha no puede ser futura.")
        return v

    # 6. NIVEL CONTRATACIÓN: Solo valores permitidos
    @field_validator("nivel_contratacion")
    def validar_nivel(cls, v):
        if not v:
            return v
        niveles_validos = ["ALTA", "MEDIA", "BAJA"]
        if v.upper() not in niveles_validos:
            raise ValueError(f'Nivel inválido. Opciones: {", ".join(niveles_validos)}')
        return v


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


# Esquema para generar el MANUAL
class ManualSchema(ModelSchema):
    class Meta:
        model = ManualConfiguracion
        fields = [
            "nombre_institucion_ente",
            "siglas_institucion_ente",
            "nombre_unidad_admin_financiera",
            "nombre_unidad_sistemas_tecnologia",
        ]
