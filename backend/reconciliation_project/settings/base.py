"""
Configuration Django de base — commune à tous les environnements.
Les fichiers development.py et production.py héritent de ce module.
"""
import os
from pathlib import Path
import environ

# ───────────────────────────────────────────────
# RÉPERTOIRES
# ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chargement des variables d'environnement depuis .env
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

# ───────────────────────────────────────────────
# SÉCURITÉ
# ───────────────────────────────────────────────
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ───────────────────────────────────────────────
# APPLICATIONS INSTALLÉES
# ───────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
]

LOCAL_APPS = [
    'apps.core',
    'apps.connectors',
    'apps.matching',
    'apps.batch',
    'apps.reports',
    'apps.notifications',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ───────────────────────────────────────────────
# MIDDLEWARE
# ───────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reconciliation_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'reconciliation_project.wsgi.application'

# ───────────────────────────────────────────────
# BASE DE DONNÉES — PostgreSQL 15
# ───────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='reconciliation_db'),
        'USER': env('POSTGRES_USER', default='reconciliation_user'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST', default='db'),
        'PORT': env('POSTGRES_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# ───────────────────────────────────────────────
# AUTHENTIFICATION
# ───────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ───────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ───────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# ───────────────────────────────────────────────
# JWT — Tokens d'authentification
# ───────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ───────────────────────────────────────────────
# CELERY — Configuration du broker et du scheduler
# ───────────────────────────────────────────────
CELERY_BROKER_URL = env('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Ouagadougou'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ───────────────────────────────────────────────
# BATCH NOCTURNE — Paramètres par défaut
# (configurables depuis l'interface admin sans redéploiement — CT-07)
# ───────────────────────────────────────────────
BATCH_SCHEDULE_HOUR = env.int('BATCH_SCHEDULE_HOUR', default=2)
BATCH_SCHEDULE_MINUTE = env.int('BATCH_SCHEDULE_MINUTE', default=0)
MATCHING_DATE_TOLERANCE_DAYS = env.int('MATCHING_DATE_TOLERANCE_DAYS', default=0)

# ───────────────────────────────────────────────
# CONNECTEURS API EXTERNES
# ───────────────────────────────────────────────
API_AUTH_BASE_URL = env('API_AUTH_BASE_URL', default='')
API_AUTH_SERVICE_ID = env('API_AUTH_SERVICE_ID', default='')
API_AUTH_SERVICE_KEY = env('API_AUTH_SERVICE_KEY', default='')
API_MOBILE_BASE_URL = env('API_MOBILE_BASE_URL', default='')
API_CORE_BASE_URL = env('API_CORE_BASE_URL', default='')
API_PI_BASE_URL = env('API_PI_BASE_URL', default='')
API_MAX_RETRIES = env.int('API_MAX_RETRIES', default=3)
API_RETRY_WAIT_FIXED = env.int('API_RETRY_WAIT_FIXED', default=2)
API_TIMEOUT_SECONDS = env.int('API_TIMEOUT_SECONDS', default=30)

# ───────────────────────────────────────────────
# NOTIFICATIONS EMAIL
# ───────────────────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('EMAIL_DEFAULT_FROM', default='rapprochement@liceli.com')
NOTIFICATION_RECIPIENTS = env.list('NOTIFICATION_RECIPIENTS', default=[])

# ───────────────────────────────────────────────
# INTERNATIONALISATION
# ───────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Ouagadougou'
USE_I18N = True
USE_TZ = True

# ───────────────────────────────────────────────
# FICHIERS STATIQUES
# ───────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.Utilisateur'

# ───────────────────────────────────────────────
# LOGGING
# ───────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
