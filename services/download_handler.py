import math
import os
import re
import time
from urllib.parse import urlparse

import requests

from apps.celery_app import logger
from config import NAS_PATH, DISCORD_TOKEN, REFRESH_RATE, BOT_MESSAGES_CHANNEL_ID
from services.discord_api import DiscordAPI
from libs.lib_files import organize_episode, dest_file_exists
from libs.lib_progressbar import get_progress_bar
from libs.lib_download import compute_url_from_1fichier, DownloadException, extract_filename

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
                        if re.search(r'S\d{2}E\d{2}', self.file_name) else "films"  # Ex: S03E15
        self.base_download_path = f"{NAS_PATH}/{self.type_dl}"
        self.file_path = f"{self.base_download_path}/{self.file_name}"
        self.total_size = None
        self.task = task

    def check(self):
        if not os.path.exists(self.base_download_path):
            error = f'{self.base_download_path} doesn\'t exists'
            raise DownloadException(self, error)

        if dest_file_exists(self.file_path):
            error = 'Already exists'
            raise DownloadException(self, error)

        return True

    def start(self):
        try:
            with (requests.get(self.url, stream=True, timeout=3600) as response):
                if response.ok:
                    self.total_size = int(response.headers.get('Content-Length', 0))
                    _downloaded_size = 0
                    _count_refresh = 0
                    _download_start_time = time.time()
                    with open(self.file_path, 'wb') as file:
                        self._update_status('Started')
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
                                    "In Progress",
                                    additionnal=self.__compute_progress(_downloaded_size, self.total_size, _download_speed),
                                    meta_data=dict(
                                        progress=_downloaded_size,
                                        total=self.total_size,
                                        speed=_download_speed
                                    )
                                )
                        # end read file
                    self.__finish()
        except Exception as error:
            raise DownloadException(self, error) from error

    def remove_file(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            logger.debug(f"file removed: {self.file_path}")

    def _update_status(self, status, additionnal=None, meta_data=None) -> None:
        status_message = f"[{self.type_dl}] Download {status}: {self.file_name}" \
            if hasattr(self, 'type_dl') and hasattr(self, 'file_name') else f"Download {status}"
        if additionnal:
            status_message += f"\n{additionnal}"

        self.__update_task_meta(meta_data)
        self.__do_notification(status_message)

    def __do_notification(self, message) -> None:
        logger.debug(message)
        if self.status_message_id:
            discord_api.edit_message(
                self.channel_id,
                self.status_message_id,
                message
            )
            return
        if self.message_id:
            self.status_message_id = discord_api.reply_to_message(
                self.channel_id,
                self.message_id,
                message
            )
            return

        discord_api.send_message(
                self.channel_id,
                message
        )

    def __update_task_meta(self, additionnal=None) -> None:
        _additionnal = additionnal if isinstance(additionnal, dict) else {}
        meta = {
                **dict(
                    url=self.url,
                    filename=self.file_name,
                    filepath=self.file_path,
                    type=self.type_dl
                ),
                **_additionnal
            }
            
        self.task.update_state(
            state='IN_PROGRESS',
            meta=meta
        )

    def __finish(self) -> None:
        self._update_status('Done')
        if self.type_dl in ['series']:
            self.file_path = organize_episode(self.file_path)


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
