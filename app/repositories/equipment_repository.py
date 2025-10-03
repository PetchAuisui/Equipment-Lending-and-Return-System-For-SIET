# repositories/equipment_repository.py
from app.db.db import SessionLocal
from app.models import Equipment  # ตรวจให้ชัวร์ว่า path นี้ตรงกับโปรเจกต์ของนาย

class EquipmentRepository:
    def __init__(self, session=None):
        self.db = session or SessionLocal()

    def get_by_id(self, equipment_id: int):
        return self.db.get(Equipment, equipment_id)

    def add(self, equipment: Equipment):
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def delete(self, equipment: Equipment):
        self.db.delete(equipment)
        self.db.commit()
