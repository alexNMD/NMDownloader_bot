import time

from celery import Task
from celery.result import AsyncResult
from celery.signals import task_revoked

from celery_app import app

from services.download import DownloadHandler


# Base Class for task
# https://docs.celeryproject.org/en/latest/userguide/tasks.html#custom-task-cls-app-wide
class TaskBase(Task):
    """
        Force usage of message and meta in exception
        Declare Task with (Base=TaskBase)
    """

    # def update_state(self, message, meta, state="RUNNING"):
    #     meta['message'] = message
    #     super().update_state(state=state, meta=meta)

    # def success(self, message, meta):
    #     meta['message'] = message
    #     meta['http_code'] = 200
    #     return meta
    def revoke(self, *args, **kwargs):
        super().revoke(*args, **kwargs)


@task_revoked.connect
def task_revoked_handler(sender=None, request=None, **kwargs):
    _task_id = request.id
    print(kwargs)

    _result = AsyncResult(_task_id)
    _meta = _result.info


    if _meta and 'file_path' in _meta:
        DownloadHandler.remove_file(_meta['file_path'])


@app.task(bind=True)
def start_download(self, url, message_id, channel_id):
    download = DownloadHandler(url, message_id, channel_id)
    download.check()

    self.update_state(
        state='PROGRESS',
        meta=dict(file_path=download.file_path)
    )

    download.start()

    return dict(
        file_name=download.file_name,
        file_path=download.file_path
    )
