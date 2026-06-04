"""
Configuration Celery du module de rapprochement.
"""
import os
from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'reconciliation_project.settings.production'
)

app = Celery('reconciliation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de diagnostic."""
    print(f'Request: {self.request!r}')
