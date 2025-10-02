from celery import Celery

from src.config.app import settings

celery_app = Celery(
    "Auth-System",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["celery_app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
