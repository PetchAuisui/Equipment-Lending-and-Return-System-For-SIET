# app/models/__init__.py
from app.db.db import Base

# ✅ Import ให้ครบ และเรียงลำดับให้ User มาก่อน Rent
from .user import User
from .renewal import Renewal
from .audit import Audit
from .returns import Return
from .class_ import Class
from .equipment import Equipment
from .equipment_images import EquipmentImage
from .status_rents import StatusRent
from .notification import Notification
from .rent import Rent  # ✅ ให้ import หลังสุด

__all__ = [
    "Base",
    "User",
    "Audit",
    "Class",
    "Equipment",
    "EquipmentImage",
    "Rent",
    "Return",
    "Renewal",
    "Notification",
]
