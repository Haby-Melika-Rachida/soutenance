"""
Configuration Django — Environnement de tests (CI/CD).
Base de données in-memory, emails désactivés.
"""
from .base import *  # noqa: F401, F403
import environ

env = environ.Env()

DEBUG = False

# Override DB avec la variable d'env injectée par GitHub Actions
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='reconciliation_test'),
        'USER': env('POSTGRES_USER', default='postgres'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='postgres'),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

# Pas d'emails en tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery en mode synchrone pour les tests (pas besoin de Redis)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Clé secrète de test
SECRET_KEY = 'django-test-secret-key-not-used-in-production'
ALLOWED_HOSTS = ['*']
