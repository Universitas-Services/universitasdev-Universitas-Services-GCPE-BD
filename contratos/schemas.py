from ninja import ModelSchema, Schema
from pydantic import field_validator, EmailStr
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List
import re
from .models import Proveedor, ComplianceExpediente, ManualConfiguracion


class ProveedorSchema(ModelSchema):
    class Meta:
        model = Proveedor
        fields = "__all__"  # Traemos todo para evitar problemas de exclusion
        exclude = ["creado_por", "fecha_registro"]

    @field_validator("rif_proveedor", check_fields=False)
    def validar_rif(cls, v):
        if not v:
            return v
        patron = r"^[VEJPGvejpg]-\d{8}-\d$"
        if not re.match(patron, v):
            raise ValueError("El RIF debe tener el formato correcto (Ej: J-12345678-0)")
        return v.upper()

    @field_validator("telefono_proveedor", check_fields=False)
    def validar_telefono(cls, v):
        if not v:
            return v
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        if len(v) not in [10, 11]:
            raise ValueError("El teléfono debe tener 10 u 11 dígitos.")
        return v

    @field_validator("correo_proveedor", check_fields=False)
    def validar_correo(cls, v):
        if not v:
            return v
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron, v):
            raise ValueError("Email inválido.")
        return v.lower()

    @field_validator("anos_experiencia", check_fields=False)
    def validar_experiencia(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("Los años de experiencia no pueden ser negativos.")
        return v

    @field_validator("fecha_estado_financiero", check_fields=False)
    def validar_fechas_pasadas(cls, v):
        if not v:
            return v
        if v > date.today():
            raise ValueError("La fecha no puede ser futura.")
        return v

    @field_validator("nivel_contratacion", check_fields=False)
    def validar_nivel(cls, v):
        if not v:
            return v
        niveles_validos = ["ALTA", "MEDIA", "BAJA"]
        if v.upper() not in niveles_validos:
            raise ValueError(f'Nivel inválido. Opciones: {", ".join(niveles_validos)}')
        return v.upper()

    @field_validator("patrimonio_reportado", mode="before", check_fields=False)
    def validar_patrimonio(cls, v):
        if v is None or v == "":
            return 0
        v_str = str(v).strip()
        # Si tiene coma, la tratamos como separador decimal
        # Ej: "1500000,50" -> "1500000.50"
        v_str = v_str.replace(",", ".")
        try:
            valor = Decimal(v_str)
            if valor < 0:
                raise ValueError("El patrimonio no puede ser negativo.")
            return valor
        except (InvalidOperation, ValueError) as e:
            if "negativo" in str(e):
                raise
            raise ValueError(
                "Formato de patrimonio inválido. Use números con . o , para decimales."
            )


# NUEVO: Esquema solo para SALIDA (Listar)
class ProveedorOut(ModelSchema):
    class Meta:
        model = Proveedor
        fields = "__all__"
        # Quitamos los validadores porque al leer de la BD no queremos que falle
        # si un dato antiguo está "feo".


# Esquema de respuesta paginada para listar proveedores
class ProveedorPaginadoOut(Schema):
    items: List[ProveedorOut]
    total: int
    page: int
    page_size: int
    pages: int


# ... (El resto de clases ComplianceSchema, etc. igual)
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


class UserProfileSchema(Schema):
    """Devuelve datos del usuario + su perfil extendido"""

    username: str
    email: str
    first_name: str
    last_name: str
    telefono: str = None
    nombre_institucion_ente: str = None
    cargo: str = None

    @staticmethod
    def resolve_telefono(obj):
        perfil = getattr(obj, "perfil", None)
        return perfil.telefono if perfil else None

    @staticmethod
    def resolve_nombre_institucion_ente(obj):
        perfil = getattr(obj, "perfil", None)
        return perfil.nombre_institucion_ente if perfil else None

    @staticmethod
    def resolve_cargo(obj):
        perfil = getattr(obj, "perfil", None)
        return perfil.cargo if perfil else None


class UserRegisterSchema(Schema):
    # --- Paso 1: Credenciales ---
    email: EmailStr
    password: str
    confirm_password: str

    # --- Paso 2: Datos Personales ---
    first_name: str  # Nombre
    last_name: str  # Apellido
    telefono: str  # Teléfono (Nuevo)

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v


# --- SCHEMAS DE GESTIÓN DE PERFIL ---


class UpdateProfileSchema(Schema):
    """Para actualizar datos del perfil"""

    email: EmailStr = None
    first_name: str = None
    last_name: str = None
    telefono: str = None
    nombre_institucion_ente: str = None
    cargo: str = None

    @field_validator("telefono", check_fields=False)
    def validar_telefono(cls, v):
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        if len(v) not in [10, 11]:
            raise ValueError("El teléfono debe tener 10 u 11 dígitos.")
        return v


class ChangePasswordSchema(Schema):
    """Para cambiar la contraseña"""

    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v


# --- SCHEMAS DE RECUPERACIÓN DE CONTRASEÑA ---


class PasswordResetRequestSchema(Schema):
    email: EmailStr


class VerificarCodigoResetSchema(Schema):
    """Paso 2: Verificar el código OTP enviado al correo"""

    email: EmailStr
    codigo: str


class ResetPasswordConTokenSchema(Schema):
    """Paso 3: Cambiar la contraseña usando el reset_token del paso 2"""

    reset_token: str
    new_password: str
    confirm_password: str

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v
