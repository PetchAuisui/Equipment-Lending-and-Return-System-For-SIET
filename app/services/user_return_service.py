# app/services/user_return_service.py

from app.repositories.user_return_repository import UserReturnRepository

class UserReturnService:
    def __init__(self):
        self.repo = UserReturnRepository()

    def get_user_return_info(self, rent_id: int):
        """ดึงข้อมูลจาก repository แล้วกรองเฉพาะฟิลด์สำคัญ"""
        rent_return = self.repo.get_rent_return_by_id(rent_id)
        if not rent_return:
            return None

        image_path = None
        if rent_return.equipment and rent_return.equipment.equipment_images:
            image_path = rent_return.equipment.equipment_images[0].image_path

        data = {
            "rent_id": rent_return.rent_id,
            "equipment_id": rent_return.equipment_id,
            "equipment_name": rent_return.equipment.name if rent_return.equipment else None,
            "image_path": image_path,
            "start_date": rent_return.start_date,
            "due_date": rent_return.due_date,
        }
        return data

    def confirm_return(self, rent_id: int):
        """เรียก repository เพื่ออัปเดตการคืนอุปกรณ์"""
        return self.repo.confirm_return(rent_id)
