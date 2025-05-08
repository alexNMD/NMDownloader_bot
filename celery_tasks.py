from apps.celery_app import app
from services.download_handler import DownloadHandler

@app.task(bind=True)
def download_task(self, url, message_id, channel_id) -> dict:
    download = DownloadHandler(url, message_id, channel_id, task=self)

    download.check()

    download.start()

    return dict(
        file_name=download.file_name,
        file_path=download.file_path
    )
