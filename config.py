import logging
import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", default="DEV")
DISCORD_TOKEN = os.getenv("DOWNLOAD_DISCORD_TOKEN")
DOWNLOAD_TOKEN = os.getenv('DOWNLOAD_TOKEN')
BOT_MESSAGES_CHANNEL_ID = int(os.getenv("BOT_MESSAGES_CHANNEL_ID"))
NAS_PATH = os.getenv("DOWNLOAD_PATH")
REFRESH_RATE = int(os.getenv("REFRESH_RATE", default='10'))  # Default => 10 seconds
LIMIT = int(os.getenv("CONCURRENCY", default='4'))  # Default => 4 threads
LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")

PREFIX = "!"
ADMINS = [
        admin.strip() for admin in os.getenv("DISCORD_ADMINS").split(',')
    ] if os.getenv("DISCORD_ADMINS") else []

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=LOG_LEVEL,
    format='[{asctime}] [{levelname}] : {message}',
    style='{'
)

BROKER_URL = os.getenv("BROKER_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

BASE_URL_1FICHIER  = os.getenv("BASE_URL_1FICHIER")
