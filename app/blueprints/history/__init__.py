# app/blueprints/history/__init__.py
from flask import Blueprint

history_bp = Blueprint("history", __name__, url_prefix="/me")

admin_history_bp = Blueprint("admin_history", __name__, url_prefix="/admin/history")



from . import routes  # noqa
