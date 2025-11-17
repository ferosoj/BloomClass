"""
Django settings for bloomclass_project project.
"""
from pathlib import Path
import os
import dj_database_url  # ⬅️ Importamos para manejar la URL de la DB
# ----------------------------------------------------------------------
# 1. BASE DIR Y ENVIRON
# ----------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Obtener variables de entorno (Render las proporciona)
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-#$m18gg*+p1ml=3znw+$$-y(#1ml%90m8=(8v)b1y2ask5pqvr' # Valor por defecto solo para desarrollo/testeo
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG será False si Render define la variable 'RENDER'
DEBUG = os.environ.get('RENDER') is None 

# ----------------------------------------------------------------------
# 2. ALLOWED HOSTS
# ----------------------------------------------------------------------

# Se debe permitir el dominio de Render en producción.
if DEBUG:
    ALLOWED_HOSTS = []
else:
    # Render establece esta variable con el dominio principal
    ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')] 
    
# ----------------------------------------------------------------------
# 3. INSTALLED APPS (Añadir Whitenoise)
# ----------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'app',
    # Necesario para servir archivos estáticos de forma eficiente en producción
    'whitenoise.runserver_nostatic', 
]

# ----------------------------------------------------------------------
# 4. MIDDLEWARE (Añadir Whitenoise)
# ----------------------------------------------------------------------

MIDDLEWARE = [
    # Colocar Whitenoise justo después de SecurityMiddleware
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
# ... (resto del middleware se mantiene igual)
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bloomclass_project.urls'

# TEMPLATES (se mantiene igual)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.icono_equipado',
            ],
        },
    },
]

WSGI_APPLICATION = 'bloomclass_project.wsgi.application'


# ----------------------------------------------------------------------
# 5. DATABASE (Configuración Dinámica PostgreSQL/SQLite)
# ----------------------------------------------------------------------

if os.environ.get('DATABASE_URL'):
    # PostgreSQL en producción (usa la variable de entorno de Render)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_check=True,
        )
    }
else:
    # SQLite en desarrollo (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation (se mantiene igual)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization (se mantiene igual)
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ----------------------------------------------------------------------
# 6. STATIC AND MEDIA FILES (Configuración de Producción)
# ----------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directorio donde Whitenoise recogerá los archivos

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
] 

# Configuración de Whitenoise para compresión y caching
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# MEDIA FILES (Render no soporta almacenamiento de archivos de usuario directamente; 
# se recomienda usar AWS S3 o un servicio similar, pero se mantiene la configuración base)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type (se mantiene igual)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/' 

LOGOUT_REDIRECT_URL = '/accounts/login/' 

AUTH_USER_MODEL = 'app.CustomUser'

# EMAIL CONFIGURATION (se mantiene igual, pero estas credenciales deberían ir en variables de entorno)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fernanda.invierno.osorio@gmail.com'
EMAIL_HOST_PASSWORD = 'hidg bars aukp btim'