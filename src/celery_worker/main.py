from celery import Celery

from celery_worker.settings.celery import settings

app = Celery(settings.name)

app.config_from_object(settings)
