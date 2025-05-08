from apps.celery_app import celery_app
from services.download_handler import DownloadHandler

@celery_app.task(bind=True)
def download_task(self, url, message_id=None, channel_id=None) -> dict:
    download = DownloadHandler(
        url=url,
        task=self,
        message_id=message_id,
        channel_id=channel_id
    )

    download.check()

    download.start()

    return dict(
        file_name=download.file_name,
        file_path=download.file_path,
        total_size=download.total_size,
        type=download.type_dl
    )
