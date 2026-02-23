"""
Django settings for contrataciones project.
Optimized for Google Cloud Run & Render DB.
"""

from pathlib import Path
import os
import environ
from datetime import timedelta

# 1. Directorio Base
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Inicialización de Environ
env = environ.Env()
# Intenta leer el .env si existe (útil para local)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# 3. Configuración de Seguridad Base
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

# Evita el Error 400 en Cloud Run permitiendo el acceso
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# --- CONFIGURACIÓN CRÍTICA PARA GOOGLE CLOUD RUN ---
# Estas líneas eliminan los errores 403 Forbidden y 400 Bad Request
if not DEBUG:
    # Confía en el protocolo seguro (HTTPS) que envía el proxy de Google
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    
    # Autoriza la URL de tu servicio para enviar formularios (CSRF)
    CSRF_TRUSTED_ORIGINS = [
        "https://backend-universitas-693924722323.us-central1.run.app"
    ]

# Parche para ejecución asíncrona de Playwright en modo local
if DEBUG:
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


# 4. Definición de Aplicaciones
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # Optimización de estáticos en desarrollo
    "django.contrib.staticfiles",
    "corsheaders",  # Requerido para conectar con el frontend
    "django_q",     # Procesamiento de documentos y correos
    "contratos",    # App principal Universitas
    "ninja",
    "ninja_extra",
    "ninja_jwt",
]

# 5. Middlewares (Orden crítico para seguridad y rendimiento)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # Debe ir arriba para habilitar CORS
    "whitenoise.middleware.WhiteNoiseMiddleware",    # Sirve los CSS/JS en producción
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "contrataciones.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "contrataciones.wsgi.application"


# 6. Base de Datos (Render)
DATABASES = {
    "default": env.db(),
}


# 7. Validación de Contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# 8. Internacionalización
LANGUAGE_CODE = "es-ve" # Configurado para Venezuela
TIME_ZONE = "America/Caracas"
USE_I18N = True
USE_TZ = True


# 9. Archivos Estáticos (WhiteNoise)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Esto permite que el admin se vea perfecto sin configurar Buckets externos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# 10. Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# 11. Optimización de Django Q para 1GB RAM
Q_CLUSTER = {
    "name": "contrataciones",
    "workers": 2,  # Reducido para evitar crashes por memoria en Cloud Run
    "recycle": 500,
    "timeout": 60,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "label": "Django Q",
    "orm": "default",
}


# 12. Configuración JWT (Seguridad de API)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# 13. Configuración de Email (Resend)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.resend.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "resend"
EMAIL_HOST_PASSWORD = env("RESEND_API_KEY", default="dummy-key")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="onboarding@resend.dev")