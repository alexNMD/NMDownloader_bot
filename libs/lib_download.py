import re
from enum import Enum

import requests

from config import logger, DOWNLOAD_TOKEN, BASE_URL_1FICHIER

class DownloadStatus(Enum):
    RUNNING = 'e8f30b'
    DONE = '0dba2f'
    ERROR = 'f63106'
    CANCELED = '510666'

class DownloadException(Exception):
    def __init__(self, download, message):
        super().__init__(message)
        logger.error(message)
        download._update_status(DownloadStatus.ERROR, message)

def compute_url_from_1fichier(link):
    _url = link.split("&")[0]
    token_response = requests.post(
            f"{BASE_URL_1FICHIER}/download/get_token.cgi",
            json={"url": _url},
            headers={
                "Authorization": f"Bearer {DOWNLOAD_TOKEN}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
    if not token_response.ok:
        logger.error(f'get_token failed: {link} - {token_response.content}.')
        raise Exception(f'get_token failed: {link} - {token_response.content}.')

    download_dct = token_response.json()
    ready_url = download_dct.get('url')
    logger.info(f"Ready to download: {ready_url}")

    return ready_url

def extract_filename(url):
    _content_disposition = requests.head(url, timeout=10).headers.get("Content-Disposition")
    _filename_regex = r'filename\*?=(?:UTF-8\'\')?"?([^;\n"]+)"?'

    if _match := re.search(_filename_regex, _content_disposition):
        return _match.group(1)
    return url.split('/')[-1]
