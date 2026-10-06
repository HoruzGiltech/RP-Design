"""
Configuración de Django para RP Design.

Todos los valores que cambian entre entornos (claves, dominios, base de datos)
se leen de variables de entorno. En local salen del archivo .env de la raíz.
"""
from datetime import timedelta
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# En Docker las variables ya llegan desde docker-compose (env_file).
# Leer el archivo solo hace falta al ejecutar Django fuera de Docker.
env_file = BASE_DIR.parent / ".env"
if env_file.exists():
    env.read_env(env_file)

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Debe terminar en "/". Ejemplo: "panel-rp/"
ADMIN_URL = env("ADMIN_URL")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Librerías
    "rest_framework",
    "corsheaders",
    "adminsortable2",
    "axes",
    # Apps del proyecto
    "core",
    "projects",
    "quotes",
    "site_content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise sirve los archivos estáticos del panel; debe ir justo después de Security
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS debe ir antes de CommonMiddleware para poder responder a tiempo
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Cuenta los intentos fallidos de login; debe ir al final
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# DATABASE_URL tiene el formato postgres://usuario:clave@servidor:puerto/base
DATABASES = {"default": env.db("DATABASE_URL")}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Bloqueo del login del panel tras varios intentos fallidos (django-axes)
AUTHENTICATION_BACKENDS = [
    # Primero axes: rechaza el intento si esa IP está bloqueada
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
# Si cambias este tiempo, cambia también el texto de core/templates/core/lockout.html
AXES_COOLOFF_TIME = timedelta(minutes=30)
# Se bloquea la IP que falla, no el usuario: así nadie puede dejar al cliente
# fuera del panel con solo escribir mal su nombre de usuario muchas veces.
AXES_LOCKOUT_PARAMETERS = ["ip_address"]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "core/lockout.html"
# Sin esto, axes escribe una línea en la consola por cada intento fallido
AXES_VERBOSE = False

# Idioma y hora
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Caracas"
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS y JS del panel)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Se usa la versión sin "manifest" porque la otra falla en los tests
    # si antes no se ejecuta collectstatic.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Archivos que sube el cliente (fotos y videos)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
MAX_IMAGE_MB = env.int("MAX_IMAGE_MB", default=5)
MAX_VIDEO_MB = env.int("MAX_VIDEO_MB", default=50)

# Solo estos sitios pueden llamar a la API desde el navegador (el frontend)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

REST_FRAMEWORK = {
    # La API solo habla JSON
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    # La API pública no usa sesiones ni cookies, por eso no necesita CSRF
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # Límite de peticiones por IP. Cada vista indica cuál usa con "throttle_scope".
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {
        "public": env("THROTTLE_PUBLIC", default="120/min"),
        "quotes": env("THROTTLE_QUOTES", default="5/hour"),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Producción
# ---------------------------------------------------------------------------
# Todo esto se activa solo con DJANGO_DEBUG=False. En local no aplica,
# porque obligaría a usar HTTPS en localhost.
if not DEBUG:
    if SECRET_KEY == "cambia-esto":
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY sigue con el valor de ejemplo. Genera una clave nueva "
            "antes de publicar el sitio."
        )

    # El backend está detrás de un proxy (Railway, Cloudflare) que recibe el HTTPS
    # y le avisa a Django con esta cabecera.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

    # Las cookies del panel solo viajan por HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS: el navegador recuerda durante un año que este sitio solo se abre con HTTPS
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Dominios desde los que se aceptan formularios del panel (con https://)
    CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
