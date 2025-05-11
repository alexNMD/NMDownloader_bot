"""Routes"""

from .download import download_bp
from .task import task_bp

def register_routes(app):
    app.register_blueprint(download_bp)
    app.register_blueprint(task_bp)
