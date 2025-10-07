from app.repositories.equipment_repository import EquipmentRepository
from app.models import Equipment

class EquipmentService:
    def __init__(self):
        self.repo = EquipmentRepository()

    def get_all_equipment(self):
        return self.repo.get_all()

    def get_equipment(self, equipment_id):
        return self.repo.get_by_id(equipment_id)

    def create_equipment(self, data):
        eq = Equipment(
            name=data.get("name"),
            code=data.get("code"),
            category=data.get("category"),
            brand=data.get("brand"),
            detail=data.get("detail"),
            buy_date=data.get("buy_date"),
            status=data.get("status", "available"),
        )
        return self.repo.add(eq)

    def update_equipment(self, equipment_id, data):
        eq = self.repo.get_by_id(equipment_id)
        if not eq:
            return None
        return self.repo.update(eq, data)

    def delete_equipment(self, equipment_id):
        eq = self.repo.get_by_id(equipment_id)
        if not eq:
            return None
        self.repo.delete(eq)
        return True
