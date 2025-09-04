from flask import Blueprint
pages_bp = Blueprint("pages", __name__)
from . import routes  # noqa
