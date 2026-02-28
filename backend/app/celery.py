from celery import Celery
from app.core.config import settings

app = Celery(
    "sc-kura",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_RESULT_BACKEND
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC"
)

app.autodiscover_tasks(["app.tasks"])