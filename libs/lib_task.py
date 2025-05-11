from celery.result import AsyncResult

from apps.celery_app import celery_app
from config import logger

def get_task_result(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    meta_info = str(result.info) if isinstance(result.info, Exception) else result.info
    return dict(
        successful=result.successful(),
        status=result.status,
        meta=meta_info
    )

def revoke_task(task_id: str) -> None:
    celery_app.control.revoke(task_id=task_id, terminate=True)
    logger.info(f'Task {task_id} Revoked')
