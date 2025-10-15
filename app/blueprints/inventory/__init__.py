
from datetime import datetime
from flask import Blueprint
inventory_bp = Blueprint("inventory", __name__)
from . import routes  # noqa

# ✅ ฟังก์ชันนี้จะทำให้ Jinja ใช้ now() ได้ในทุก template
@inventory_bp.app_context_processor
def inject_now():
    return {'now': datetime.now}
