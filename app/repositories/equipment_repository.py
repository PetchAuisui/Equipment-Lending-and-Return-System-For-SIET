# app/repositories/equipment_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import exists, and_
from app.db.db import SessionLocal
from app.db.models import Equipment, EquipmentImage, StockMovement

# รองรับชื่อความสัมพันธ์รูปทั้งสองแบบ
IMAGES_REL = getattr(Equipment, "images", None) or getattr(Equipment, "equipment_images")

class EquipmentRepository:
    def __init__(self, session: Optional[Session] = None):
        self.db = session or SessionLocal()

    # ---------- Query ----------
    def list(self, q: str = "", category: str = "") -> List[Equipment]:
        query = (
            self.db.query(Equipment)
            .options(joinedload(IMAGES_REL))  # preload ความสัมพันธ์รูป
            .filter(
                # กรองออกอุปกรณ์ที่มี movement [DELETED] (soft-delete แบบไม่แตะ schema)
                ~exists().where(
                    and_(
                        StockMovement.equipment_id == Equipment.equipment_id,
                        StockMovement.history.ilike("%[DELETED]%"),
                    )
                )
            )
        )
        if q:
            like = f"%{q}%"
            query = query.filter((Equipment.name.ilike(like)) | (Equipment.code.ilike(like)))
        if category:
            query = query.filter(Equipment.category == category)
        return query.order_by(Equipment.created_at.desc()).all()

    def get(self, equipment_id: int) -> Optional[Equipment]:
        return (
            self.db.query(Equipment)
            .options(joinedload(IMAGES_REL))
            .filter(
                Equipment.equipment_id == equipment_id,
                ~exists().where(
                    and_(
                        StockMovement.equipment_id == Equipment.equipment_id,
                        StockMovement.history.ilike("%[DELETED]%"),
                    )
                )
            )
            .first()
        )

    def code_exists(self, code: str) -> bool:
        # อนุญาตให้รหัสซ้ำกับรายการที่ถูกลบไปแล้วได้ไหม?
        # ถ้าไม่อนุญาต ก็เช็คทั้งหมด; ถ้าอนุญาต ให้กรอง NOT DELETED เหมือน list()
        return (
            self.db.query(Equipment)
            .filter(Equipment.code == code)
            .first()
            is not None
        )

    # ---------- Create / Update ----------
    def add_equipment(self, equipment: Equipment) -> Equipment:
        self.db.add(equipment)
        self.db.flush()  # ให้ได้ equipment_id
        return equipment

    def add_image(self, equipment_id: int, image_path: str) -> EquipmentImage:
        img = EquipmentImage(equipment_id=equipment_id, image_path=image_path)
        self.db.add(img)
        return img

    def add_movement(self, equipment_id: int, actor_id: Optional[int], history: str) -> StockMovement:
        mv = StockMovement(equipment_id=equipment_id, actor_id=actor_id, history=history)
        self.db.add(mv)
        return mv

    # เดิมเคยตั้งค่า is_active=False; ตอนนี้ไม่ใช้แล้ว (คง method ไว้แต่ไม่ทำอะไรเพื่อความเข้ากันได้)
    def soft_delete_equipment(self, equipment: Equipment):
        return  # no-op (ไม่แตะ schema)

    def delete_image_row(self, image: EquipmentImage):
        self.db.delete(image)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def close(self):
        self.db.close()
