from celery import Celery

from src.config.app import settings

celery_app = Celery(
    "Auth-System",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
