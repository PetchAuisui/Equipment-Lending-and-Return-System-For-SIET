# repositories/equipment_repository.py
from app.models.equipment import Equipment
from app.db.db import SessionLocal

class EquipmentRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all(self):
        return self.db.query(Equipment).filter(Equipment.is_active == True).all()

    def get_by_id(self, equipment_id):
        return self.db.query(Equipment).get(equipment_id)

    def add(self, equipment):
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def delete(self, equipment):
        self.db.delete(equipment)
        self.db.commit()
