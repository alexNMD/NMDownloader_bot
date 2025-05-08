import logging
from flask import Flask

from config import LOG_LEVEL
from routes import register_routes

flask_app = Flask(__name__)

logger = logging.getLogger('celery')
logger.setLevel(LOG_LEVEL)

register_routes(flask_app)
