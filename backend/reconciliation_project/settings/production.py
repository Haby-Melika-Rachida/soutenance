"""
Configuration Django — Environnement de production.
Sécurité renforcée, debug désactivé, CORS restreint.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# CORS — uniquement le frontend servi par Nginx
CORS_ALLOWED_ORIGINS = [
    'https://rapprochement.liceli.internal',
]
CORS_ALLOW_CREDENTIALS = True

# Sécurité HTTP
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
