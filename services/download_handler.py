import os
import io
import re
import time
import pickle
from urllib.parse import urlparse

import requests

from apps.celery_app import logger
from config import (
    NAS_PATH,
    DISCORD_TOKEN,
    REFRESH_RATE,
    BOT_MESSAGES_CHANNEL_ID,
    CHUNK_SIZE,
)
from services.discord_api import DiscordAPI
from services.files import FilesHandlerService
from libs.lib_files import (
    organize_episode,
    dest_file_exists,
    is_json_serializable,
)
from libs.lib_progressbar import get_progress_bar
from libs.lib_download import (
    compute_url_from_1fichier,
    extract_filename,
    DownloadException,
    DownloadRevokeException,
    DownloadStatus,
)

discord_api = DiscordAPI(DISCORD_TOKEN)


class DownloadHandler:
    def __init__(self, url, task, message_id=None, channel_id=None):
        self.task = task
        self.status_message_id = None
        self.message_id = message_id
        self.channel_id = channel_id or BOT_MESSAGES_CHANNEL_ID
        self.url = self._compute_url(url)
        try:
            self.file_name = extract_filename(self.url)
        except Exception as error:
            raise DownloadException(self, "Unable to retrieve filename") from error
        self.type_dl = (
            "series"
            if re.search(r"[Ss]\d{1,2}([Ee]\d{1,2})?", self.file_name)
            else "films"
        )
        self.base_download_path = f"{NAS_PATH}/{self.type_dl}"
        self.file_path = os.path.join(self.base_download_path, self.file_name)
        self.download_start_time = None
        self.total_size = None
        self.finished = False

    def check(self):
        if not os.path.exists(self.base_download_path):
            raise DownloadException(self, f"{self.base_download_path} doesn't exists")

        if dest_file_exists(self.file_path):
            raise DownloadException(self, "Already exists")

        return True

    def start(self):
        try:
            with requests.get(self.url, stream=True, timeout=3600) as response:
                if response.ok:
                    self.total_size = int(response.headers.get("Content-Length", 0))
                    self.download_start_time = time.time()
                    with open(self.file_path, "wb") as file:
                        with io.BufferedWriter(
                            file, buffer_size=CHUNK_SIZE
                        ) as file_buffer:
                            self._update_status(DownloadStatus.STARTED)
                            self._handle_chunks(file_buffer, response)
                    self._finish()
        except FileNotFoundError as error:
            raise DownloadException(self, error) from error
        except Exception as error:
            self._remove()
            raise DownloadException(self, error) from error

    def cancel(self):
        self._remove()
        raise DownloadRevokeException(self)

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if is_json_serializable(value)
        }

    def _update_status(
        self, status: DownloadStatus, additionnal: str = str(), meta_data=None
    ) -> None:
        title = f"Download {status.name}"
        _base_content = (
            f"[{self.type_dl}] {self.file_name} \n"
            if (hasattr(self, "type_dl") and hasattr(self, "file_name"))
            else ""
        )
        content = _base_content + additionnal

        self._update_task_meta(meta_data)
        self._do_notification(status, title, content)

    def _do_notification(self, status: DownloadStatus, title, content) -> None:
        logger.debug(title, content)

        if self.status_message_id:
            discord_api.edit_embed(
                self.channel_id, self.status_message_id, title, content, status.value
            )
            return

        self.status_message_id = (
            discord_api.reply_with_embed(
                self.channel_id, self.message_id, title, content, status.value
            )
            if self.message_id
            else discord_api.send_embed(self.channel_id, title, content, status.value)
        )

    def _update_task_meta(self, additionnal_meta=None) -> None:
        _additionnal_meta = (
            additionnal_meta if isinstance(additionnal_meta, dict) else {}
        )
        meta = dict(
            download=pickle.dumps(self),
        ) | dict(stats=_additionnal_meta)

        self.task.update_state(meta=meta)

    def _finish(self) -> None:
        _files = [self.file_path]
        _files_handler = FilesHandlerService(self.file_path)
        if _files_handler.is_compressed:
            self._update_status(
                DownloadStatus.RUNNING, additionnal="Extraction in progress..."
            )
            _files = _files_handler.handle_archive() or []

        if self.type_dl in ["series"]:
            for _file in _files:
                self.file_path = organize_episode(_file)

        self._update_status(DownloadStatus.DONE)
        self.finished = True

    def _compute_url(self, url) -> str:
        download_providers = {"1fichier.com": compute_url_from_1fichier}
        _netloc = urlparse(url).netloc

        try:
            return download_providers.get(_netloc, lambda url: url)(url)
        except Exception as error:
            raise DownloadException(self, str(error))

    def _handle_chunks(self, file_buffer, response) -> None:
        downloaded_size = 0
        _count_refresh = 0

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if not chunk:
                break

            file_buffer.write(chunk)

            downloaded_size += len(chunk)
            _elapsed_time = time.time() - self.download_start_time
            _refresh_interval_count = int(_elapsed_time / REFRESH_RATE)

            if _refresh_interval_count > _count_refresh:
                _count_refresh += 1
                download_speed = downloaded_size / _elapsed_time
                self._update_status(
                    DownloadStatus.RUNNING,
                    additionnal=self._compute_progress(
                        downloaded_size, self.total_size, download_speed
                    ),
                    meta_data=dict(
                        progress=downloaded_size,
                        total=self.total_size,
                        speed=download_speed,
                    ),
                )

    def _remove(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            logger.info(f"file removed: {self.file_path}")

    @classmethod
    def _compute_progress(cls, progress, total, speed) -> str:
        _remaining_time_seconds = (total - progress) / speed
        _less_than_one_minute = _remaining_time_seconds < 60

        progress_bar = get_progress_bar(progress, total)
        remaining_time = (
            _remaining_time_seconds
            if _less_than_one_minute
            else _remaining_time_seconds / 60
        )
        time_unit = "sec" if _less_than_one_minute else "min"
        speed_in_mb = speed / (1024 * 1024)

        return f"{progress_bar} [ETA {remaining_time:.0f} {time_unit} @ {speed_in_mb:.2f} MB/s]"
