"""Routes"""

from .download import download_bp


def register_routes(app):
    app.register_blueprint(download_bp)
