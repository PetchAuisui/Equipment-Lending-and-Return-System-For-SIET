from flask import Blueprint
tracking_bp = Blueprint("tracking", __name__)
from . import routes  # noqa
