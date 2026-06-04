# Import Celery pour qu'il soit chargé automatiquement au démarrage Django
from .celery import app as celery_app

__all__ = ('celery_app',)
