from celery.result import AsyncResult
from flask import request, Blueprint

from apps.celery_app import celery_app
from apps.flask_app import flask_app
from tasks.download_tasks import download_task
from config import logger


download_task_bp = Blueprint("download", __name__, url_prefix="/download")

@download_task_bp.get("/task/<uuid>")
def get_task_status(uuid: str) -> dict[str, object]:
    result = AsyncResult(uuid, app=celery_app)
    flask_app.logger.debug(result)

    return {
        "successful": result.successful(),
        "meta": result.info
    }

@download_task_bp.post("/task")
def send_task() -> dict[str, object]:
    data = request.get_json()
    task = download_task.delay(
        url=data.get('url')
    )
    flask_app.logger.info(f'Task sent: {task.id}')

    return {
        "uuid": task.id
    }
