from flask import request, Blueprint, jsonify

from libs.lib_task import get_task_result, revoke_task
from tasks.download_tasks import download_task
from services.download_handler import DownloadHandler
from config import gunicorn_logger

download_bp = Blueprint("download", __name__, url_prefix="/download")

@download_bp.post("/")
def launch() -> dict[str, object]:
    data = request.get_json()
    if not (url := data.get('url')):
        return jsonify(dict(message='URL is mandatory')), 400

    task = download_task.delay(
        url=url
    )
    gunicorn_logger.info(f'Task sent: {task.id}')

    return jsonify(
        dict(uuid=task.id)
    )

@download_bp.delete("/<uuid>")
def stop(uuid) -> dict[str, object]:
    result_dict = get_task_result(uuid)
    if not isinstance(result_dict['meta'], dict):
        return jsonify(dict(message='Unable to retrieve file path')), 400
    if not (download := result_dict.get('meta', {}).get('download')):
        return jsonify(dict(message='Unable to retrieve file path')), 400

    revoke_task(uuid)
    download.cancel()

    return jsonify(
        dict(message="Download stopped")
    )
