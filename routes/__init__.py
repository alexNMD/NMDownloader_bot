"""Routes"""

from .download_task import download_task_bp

def register_routes(app):
    app.register_blueprint(download_task_bp)
