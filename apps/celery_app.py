import logging

from celery import Celery

from config import BROKER_URL, BACKEND_URL, LIMIT, LOG_LEVEL

celery_app = Celery(
    'tasks',
    broker=BROKER_URL,
    backend=BACKEND_URL,
    worker_concurrency=LIMIT,
    broker_connection_retry_on_startup=False,
    task_serializer='pickle',
    accept_content=['pickle', 'json'],
    worker_send_task_events=True
)

logger = logging.getLogger('celery')
logger.setLevel(LOG_LEVEL)

__import__('celery_tasks')
