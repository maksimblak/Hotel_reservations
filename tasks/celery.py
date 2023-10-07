from celery import Celery
from config import settings

# Создание экземпляра Celery для обработки фоновых задач
celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["tasks.tasks"]
)
