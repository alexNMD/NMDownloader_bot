from apps.celery_app import app
from services.download_handler import DownloadHandler

@app.task(bind=True)
def download_task(self, url, message_id, channel_id) -> dict:
    download = DownloadHandler(url, message_id, channel_id)
    download.check()

    self.update_state(
        state='PROGRESS',
        meta=download.__dict__
    )

    download.start()

    return download.__dict__
