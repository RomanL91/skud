import os

from celery import Celery

from core.settings import CELERY_BROKER_URL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")



app = Celery(
    main='core',
    broker_connection_retry_on_startup=True,
    broker=CELERY_BROKER_URL,
    include=['app_camera.tasks'],
    
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


if __name__ == '__main__':
    print('[==INFO==] CELERY STARTED')
    app.start()