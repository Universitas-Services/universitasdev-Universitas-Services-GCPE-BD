from django.db import models
from django.contrib.auth.models import User


# ==============================================================================
# 1. PERFIL DE USUARIO
# ==============================================================================
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    cargo = models.CharField(max_length=150, verbose_name="Cargo del Usuario")
    nombre_institucion_ente = models.CharField(
        max_length=255, verbose_name="Institución"
    )

    def __str__(self):
        return f"{self.user.username} - {self.cargo}"


# ==============================================================================
# 2. CONFIGURACIÓN DEL MANUAL
# ==============================================================================
class ManualConfiguracion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_institucion_ente = models.CharField(max_length=255)
    siglas_institucion_ente = models.CharField(max_length=50)
    nombre_unidad_admin_financiera = models.CharField(max_length=255)
    nombre_unidad_sistemas_tecnologia = models.CharField(max_length=255)

    def __str__(self):
        return self.siglas_institucion_ente


# ==============================================================================
# 3. REGISTRO DE PROVEEDORES
# ==============================================================================
class Proveedor(models.Model):
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_registro = models.DateField(auto_now_add=True)

    # Identificación
    correo_proveedor = models.EmailField()
    nombre_proveedor = models.CharField(max_length=255, verbose_name="Razón Social")
    rif_proveedor = models.CharField(max_length=20, verbose_name="RIF")

    TIPO_PERSONA_CHOICES = [("N", "Natural"), ("J", "Jurídica")]
    tipo_persona = models.CharField(max_length=1, choices=TIPO_PERSONA_CHOICES)
    tipo_entidad_juridica = models.CharField(max_length=50, blank=True, null=True)

    # Ubicación
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    direccion_fiscal = models.TextField()

    # Contacto
    telefono_proveedor = models.CharField(max_length=20)
    nombre_rep_legal = models.CharField(max_length=255)
    cedula_rep_legal = models.CharField(max_length=20)

    # Validaciones (SI/NO se mantienen aquí porque son checks simples)
    tiene_rnc = models.BooleanField(default=False)
    tiene_solvencia_laboral = models.BooleanField(default=False)
    tiene_licencia_municipal = models.BooleanField(default=False)

    # Capacidad
    actividad_comercial_principal = models.BooleanField(default=False)
    AREA_CHOICES = [("Bienes", "Bienes"), ("Obras", "Obras"), ("Servicio", "Servicio")]
    area_especialidad = models.CharField(max_length=50, choices=AREA_CHOICES)
    anos_experiencia = models.PositiveIntegerField(default=0)
    fecha_estado_financiero = models.DateField(null=True, blank=True)
    patrimonio_reportado = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )

    NIVEL_CHOICES = [("ALTA", "Alta"), ("MEDIA", "Media"), ("BAJA", "Baja")]
    nivel_contratacion = models.CharField(max_length=10, choices=NIVEL_CHOICES)

    def __str__(self):
        return f"{self.nombre_proveedor} ({self.rif_proveedor})"


# ==============================================================================
# 4. COMPLIANCE (AUDITORÍA) - AQUÍ ESTÁ EL CAMBIO CLAVE
# ==============================================================================

# Opciones disponibles para el dropdown
OPCIONES_RESPUESTA = [
    ("SI", "SI"),
    ("NO", "NO"),
    ("NA", "NO APLICA"),
]


class ComplianceExpediente(models.Model):
    usuario_revisor = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Cabecera del Reporte
    nombre_organo_entidad = models.CharField(max_length=255)
    nombre_unidad_revisora = models.CharField(max_length=255)
    nomenclatura = models.CharField(max_length=100, verbose_name="Código Documento")
    fecha_revision = models.DateField()
    persona_contacto = models.CharField(max_length=255, verbose_name="Elaborado Por")
    nombre_completo_revisor = models.CharField(max_length=255)

    # --- LAS 24 PREGUNTAS (Ahora son CharField con opciones) ---
    caaue1_incluye_actividades_previas = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue2_incluye_acta_inicio = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue3_incluye_pliego_condiciones = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue4_publicacion_llamado_snc = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue5_publicacion_llamado_ente = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue6_incluye_registro_adquirientes = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue7_incluye_modificaciones = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue8_incluye_acta_recepcion_sobres = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue9_incluye_acta_apertura_sobres = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue10_incluye_ofertas = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue11_incluye_garantias_sostenimiento = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue12_incluye_certificado_rnc = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue13_incluye_certificado_snc = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue14_incluye_solvencias = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue15_incluye_informe_recomendacion = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue16_incluye_adjudicacion = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue17_incluye_notificacion = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue18_incluye_garantias_contratacion = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue19_incluye_contrato_u_orden = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue20_incluye_resp_social = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue21_identificacion_nomenclatura = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue22_expediente_foliado = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue23_identificacion_tomos = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )
    caaue24_archivo_custodia = models.CharField(
        max_length=2, choices=OPCIONES_RESPUESTA, default="NA"
    )

    def __str__(self):
        return f"Auditoría {self.nomenclatura}"
