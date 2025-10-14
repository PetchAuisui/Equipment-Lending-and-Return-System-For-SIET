from datetime import datetime
from app.repositories.admin_return_repository import AdminReturnRepository

class AdminReturnService:
    """Business Logic สำหรับการคืนอุปกรณ์"""

    def __init__(self):
        self.repo = AdminReturnRepository()

    def list_pending_returns(self):
        """ดึงข้อมูลอุปกรณ์ที่รอคืน (status_id = 3)"""
        rent_list = self.repo.get_pending_returns(status_id=3)
        data = []
        for r in rent_list:
            data.append({
                "rent_id": r.rent_id,
                "equipment_code": r.equipment.code,
                "equipment_name": r.equipment.name,
                "return_date": r.return_date.strftime("%d/%m/%Y") if r.return_date else "-",
                "user_code": r.user.student_id or r.user.employee_id,
                "user_name": r.user.name,
                "image": r.equipment.equipment_images[0].image_path if r.equipment.equipment_images else None
            })
        self.repo.close()
        return data

    def confirm_return(self, rent_id):
        """อัปเดตสถานะการคืน"""
        rent = self.repo.get_by_id(rent_id)
        if not rent:
            return {"status": "error", "message": "ไม่พบข้อมูลการยืมนี้"}

        rent.status_id = 4  # สมมติว่า 4 = คืนแล้ว
        rent.return_date = datetime.utcnow()
        self.repo.update()
        self.repo.close()
        return {"status": "success", "message": f"คืนอุปกรณ์หมายเลข {rent_id} เรียบร้อยแล้ว"}
