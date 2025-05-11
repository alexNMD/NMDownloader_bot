from flask import Blueprint, jsonify

from libs.lib_task import get_task_result, revoke_task
from config import gunicorn_logger

task_bp = Blueprint("task", __name__, url_prefix="/task")

@task_bp.get("/<uuid>")
def get_status(uuid: str) -> dict[str, object]:
    result_dict = get_task_result(uuid)
    gunicorn_logger.debug(result_dict)

    return jsonify(result_dict)

@task_bp.delete("/<uuid>")
def revoke(uuid: str) -> dict[str, object]:
    revoke_task(uuid)

    return jsonify(dict(message='Task revoked'))
