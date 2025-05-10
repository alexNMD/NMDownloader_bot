from celery.result import AsyncResult
from flask import request, Blueprint, jsonify

from apps.celery_app import celery_app
from tasks.download_tasks import download_task
from config import gunicorn_logger

download_task_bp = Blueprint("download", __name__, url_prefix="/download")

@download_task_bp.get("/task/<uuid>")
def get_task_status(uuid: str) -> dict[str, object]:
    result = AsyncResult(uuid, app=celery_app)
    meta_info = str(result.info) if isinstance(result.info, Exception) else result.info
    result_dict = dict(
        successful=result.successful(),
        status=result.status,
        meta=meta_info
    )
    gunicorn_logger.debug(result_dict)

    return result_dict

@download_task_bp.post("/task")
def send_task() -> dict[str, object]:
    data = request.get_json()
    task = download_task.delay(
        url=data.get('url')
    )
    gunicorn_logger.info(f'Task sent: {task.id}')

    return jsonify(
        dict(uuid=task.id)
    )
