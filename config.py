import logging
import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", default="DEV")
DISCORD_TOKEN = os.getenv("DOWNLOAD_DISCORD_TOKEN")
DOWNLOAD_TOKEN = os.getenv("DOWNLOAD_TOKEN")
BOT_MESSAGES_CHANNEL_ID = int(os.getenv("BOT_MESSAGES_CHANNEL_ID"))
NAS_PATH = os.getenv("DOWNLOAD_PATH")
REFRESH_RATE = int(os.getenv("REFRESH_RATE", default="10"))  # Default => 10 seconds
LIMIT = int(os.getenv("CONCURRENCY", default="4"))  # Default => 4 threads
LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")
CHUNK_SIZE = 1024 * 64  # 64 KB

PREFIX = "!"
ADMINS = (
    [admin.strip() for admin in os.getenv("DISCORD_ADMINS").split(",")]
    if os.getenv("DISCORD_ADMINS")
    else []
)

## LOGGER settings
logger = logging.getLogger(__name__)
logging.basicConfig(level=LOG_LEVEL, format="[{asctime}] [{levelname}] : {message}", style="{")
gunicorn_logger = logging.getLogger("gunicorn.error")
gunicorn_logger.setLevel(LOG_LEVEL)

BROKER_URL = os.getenv("BROKER_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

BASE_URL_1FICHIER = "https://api.1fichier.com/v1"
BASE_URL_DISCORD = "https://discord.com/api/v10"
