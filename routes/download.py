from flask import request, Blueprint, jsonify

from libs.lib_task import get_download_task, revoke_task
from services.download_handler import DownloadHandler
from tasks.download_tasks import download_task
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

@download_bp.get("/<uuid>")
def status(uuid) -> dict[str, object]:
    download_meta = get_download_task(uuid, json_readable=True)

    return jsonify(download_meta)

@download_bp.delete("/<uuid>")
def stop(uuid) -> dict[str, object]:
    download_meta = get_download_task(uuid)
    if not isinstance(download_meta['download'], DownloadHandler):
        return jsonify(dict(message='Unable to retrieve download')), 400

    revoke_task(uuid)
    download_meta['download'].cancel()

    return jsonify(
        dict(message="Download stopped")
    )
