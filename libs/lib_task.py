import pickle
from celery.result import AsyncResult

from apps.celery_app import celery_app
from services.download_handler import DownloadHandler

def get_task_result(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery_app)
    meta_info = str(result.info) if isinstance(result.info, Exception) else result.info
    return dict(
        successful=result.successful(),
        status=result.status,
        meta=meta_info
    )

def get_download_task(task_id: str, json_readable=False):
    result = AsyncResult(task_id, app=celery_app)
    try:
        download = pickle.loads(result.info['download'])
    except TypeError:
        download = str(result.info)

    return dict(
        download=download.to_dict() if json_readable else download,
        stats=result.info.get('stats', {})
    ) if isinstance(download, DownloadHandler) else get_task_result(task_id)
