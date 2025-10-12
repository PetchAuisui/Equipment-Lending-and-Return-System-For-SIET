# app/blueprints/history/__init__.py
from flask import Blueprint

history_bp = Blueprint("history", __name__, url_prefix="/me")

from . import routes  # noqa
