import logging
from flask import Flask

from config import LOG_LEVEL
from routes import register_routes

flask_app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
flask_app.logger.handlers = gunicorn_logger.handlers
flask_app.logger.setLevel(LOG_LEVEL)

register_routes(flask_app)
