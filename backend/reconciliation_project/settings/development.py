"""
Configuration Django — Environnement de développement local.
Active le debug, SQLite possible pour les tests rapides.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# En dev : emails affichés dans la console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS permissif en dev (frontend Vue.js sur port 5173)
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (optionnel, à installer si nécessaire)
# INSTALLED_APPS += ['debug_toolbar']
