from app.repositories.equipment_repository import EquipmentRepository

class EquipmentService:
    def __init__(self):
        self.repo = EquipmentRepository()

    def list_all(self):
        return self.repo.get_all()

    def get_detail(self, id):
        return self.repo.get_by_id(id)

    def create_equipment(self, data):
        return self.repo.create(data["name"], data["code"], data.get("status", "available"))

    def update_equipment(self, id, data):
        return self.repo.update(id, data)

    def delete_equipment(self, id):
        return self.repo.soft_delete(id)
