import os
from celery import Celery
from datetime import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'checking_HTTP_LONG': { 
        'task': 'app_camera.tasks.checking_HTTP_LONG_connection_with_macroscope',
        'schedule': timedelta(seconds=7),
    }
}