from apps.celery_app import app
from services.download_handler import DownloadHandler

@app.task(bind=True)
def download_task(self, url, message_id, channel_id):
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
