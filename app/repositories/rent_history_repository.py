from __future__ import annotations
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, StatusRent, EquipmentImage

class RentHistoryRepository:
    """
    อ่านประวัติการยืม/คืนของผู้ใช้ตาม user_id
    join: equipments, status_rents, (รูปอุปกรณ์ตัวอย่าง 1 รูป)
    """
    def __init__(self, session: Optional[Session] = None):
        self.session: Session = session or SessionLocal()

    def list_by_user(self, user_id: int) -> List[Dict]:
        # ซับคิวรีหยิบรูปแรกของอุปกรณ์ (ถ้าต้องการโชว์ภาพหน้าการ์ด)
        img_subq = (
            self.session.query(
                EquipmentImage.equipment_id,
                func.min(EquipmentImage.equipment_image_id).label("min_id")
            ).group_by(EquipmentImage.equipment_id).subquery()
        )

        stmt = (
            select(
                RentReturn.rent_id,
                RentReturn.start_date,
                RentReturn.due_date,
                RentReturn.return_date,
                RentReturn.reason,
                Equipment.equipment_id,
                Equipment.name.label("equipment_name"),
                Equipment.code.label("equipment_code"),
                Equipment.category,
                StatusRent.name.label("status_name"),
                StatusRent.color_code.label("status_color"),
                EquipmentImage.image_path.label("cover_image"),
            )
            .join(Equipment, Equipment.equipment_id == RentReturn.equipment_id)
            .join(StatusRent, StatusRent.status_id == RentReturn.status_id)
            .outerjoin(img_subq, img_subq.c.equipment_id == Equipment.equipment_id)
            .outerjoin(EquipmentImage, EquipmentImage.equipment_image_id == img_subq.c.min_id)
            .where(RentReturn.user_id == user_id)
            .order_by(RentReturn.start_date.desc())
        )
        rows = self.session.execute(stmt).all()
        return [dict(r._mapping) for r in rows]
