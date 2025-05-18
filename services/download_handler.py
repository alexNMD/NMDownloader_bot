import math
import os
import re
import time
import pickle
from urllib.parse import urlparse

import requests

from apps.celery_app import logger
from config import NAS_PATH, DISCORD_TOKEN, REFRESH_RATE, BOT_MESSAGES_CHANNEL_ID
from services.discord_api import DiscordAPI
from libs.lib_files import (
    organize_episode,
    dest_file_exists,
    is_json_serializable,
    handle_archive,
    is_compressed
)
from libs.lib_progressbar import get_progress_bar
from libs.lib_download import (
    compute_url_from_1fichier,
    extract_filename,
    DownloadException,
    DownloadRevokeException,
    DownloadStatus
)

discord_api = DiscordAPI(DISCORD_TOKEN)

class DownloadHandler:
    def __init__(self, url, task, message_id=None, channel_id=None):
        self.status_message_id = None
        self.url = self.__compute_url(url)
        self.message_id = message_id
        self.channel_id = channel_id or BOT_MESSAGES_CHANNEL_ID
        try:
            self.file_name = extract_filename(self.url)
        except Exception as error:
            raise DownloadException(self, 'Unable to retrieve filename') from error
        self.type_dl = "series" \
            if re.search(r'[Ss]\d{1,2}([Ee]\d{1,2})?', self.file_name) \
            else "films"
        self.base_download_path = f"{NAS_PATH}/{self.type_dl}"
        self.file_path = f"{self.base_download_path}/{self.file_name}"
        self.total_size = None
        self.task = task
        self.finished = False

    def check(self):
        if not os.path.exists(self.base_download_path):
            raise DownloadException(self, f'{self.base_download_path} doesn\'t exists')

        if dest_file_exists(self.file_path):
            raise DownloadException(self, 'Already exists')

        return True

    def start(self):
        try:
            with requests.get(self.url, stream=True, timeout=3600) as response:
                if response.ok:
                    self.total_size = int(response.headers.get('Content-Length', 0))
                    _downloaded_size = 0
                    _count_refresh = 0
                    _download_start_time = time.time()
                    with open(self.file_path, 'wb') as file:
                        self._update_status(DownloadStatus.STARTED)
                        # start read file
                        for chunk in response.iter_content(chunk_size=8192):
                            if not chunk:
                                break
                            file.write(chunk)
                            _downloaded_size += len(chunk)  # bytes
                            elapsed_time = time.time() - _download_start_time  # seconds
                            if math.trunc(elapsed_time / REFRESH_RATE) > _count_refresh:
                                _count_refresh += 1
                                _download_speed = _downloaded_size / elapsed_time  # bytes

                                self._update_status(
                                    DownloadStatus.RUNNING,
                                    additionnal=self.__compute_progress(
                                        _downloaded_size, self.total_size, _download_speed
                                    ),
                                    meta_data=dict(
                                        progress=_downloaded_size,
                                        speed=_download_speed
                                    )
                                )
                        # end read file
                    self.__finish()
        except Exception as error:
            raise DownloadException(self, error) from error

    def cancel(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            logger.info(f"file removed: {self.file_path}")

        raise DownloadRevokeException(self)



    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if is_json_serializable(value)}

    def _update_status(self,
                       status: DownloadStatus,
                       additionnal: str=str(), meta_data=None) -> None:
        title = f"Download {status.name}"
        _base_content = f'[{self.type_dl}] {self.file_name} \n' \
            if (self.type_dl and self.file_name) else ''
        content = _base_content + additionnal

        self.__update_task_meta(meta_data)
        self.__do_notification(status, title, content)

    def __do_notification(self, status: DownloadStatus, title, content) -> None:
        logger.debug(title, content)

        if self.status_message_id:
            discord_api.edit_embed(
                self.channel_id,
                self.status_message_id,
                title,
                content,
                status.value
            )
            return

        self.status_message_id = discord_api.reply_with_embed(
                self.channel_id,
                self.message_id,
                title,
                content,
                status.value
            ) if self.message_id \
                else \
                    discord_api.send_embed(
                        self.channel_id,
                        title,
                        content,
                        status.value
                    )


    def __update_task_meta(self, additionnal_meta=None) -> None:
        _additionnal_meta = additionnal_meta if isinstance(additionnal_meta, dict) else {}
        meta = dict(
            download=pickle.dumps(self),
        ) | dict (
            stats=_additionnal_meta
        )

        self.task.update_state(
            state='IN_PROGRESS',
            meta=meta
        )

    def __finish(self) -> None:
        if is_compressed(self.file_path):
            self._update_status(DownloadStatus.RUNNING, additionnal="Extraction in progress...")
            handle_archive(self.file_path)
        else:
            if self.type_dl in ['series']:
                self.file_path = organize_episode(self.file_path)

        self._update_status(DownloadStatus.DONE)
        self.finished = True


    @staticmethod
    def __compute_url(url) -> str:
        download_providers = {
            "1fichier.com": compute_url_from_1fichier
        }
        _netloc = urlparse(url).netloc

        return download_providers.get(_netloc, lambda url:url)(url)

    @classmethod
    def __compute_progress(cls, progress, total, speed) -> str:
        _remaining_time_seconds = (total - progress) / speed
        _less_than_one_minute = _remaining_time_seconds < 60

        progress_bar = get_progress_bar(progress, total)
        remaining_time = \
            _remaining_time_seconds if _less_than_one_minute else _remaining_time_seconds / 60
        time_unit = "sec" if _less_than_one_minute else "min"
        speed_in_mb = speed / (1024 * 1024)

        return f"{progress_bar} [ETA {remaining_time:.0f} {time_unit} @ {speed_in_mb:.2f} MB/s]"
