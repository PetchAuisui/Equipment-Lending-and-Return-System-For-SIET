from datetime import datetime
from flask import session
from app.repositories.admin_return_repository import AdminReturnRepository
from app.db.models import Equipment

class AdminReturnService:
    """Business Logic สำหรับการคืนอุปกรณ์"""

    def __init__(self):
        self.repo = AdminReturnRepository()

    def list_pending_returns(self):
        """แสดงอุปกรณ์ที่รอคืน"""
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
        """อัปเดตสถานะคืน + ผู้ตรวจสอบ + เปลี่ยนอุปกรณ์เป็น available"""
        rent = self.repo.get_by_id(rent_id)
        if not rent:
            self.repo.close()
            return {"status": "error", "message": "ไม่พบข้อมูลการยืมนี้"}

        # ✅ ตรวจสอบอุปกรณ์
        equipment = rent.equipment
        if not equipment:
            equipment = self.repo.db.query(Equipment).get(rent.equipment_id)

        if not equipment:
            self.repo.close()
            return {"status": "error", "message": "ไม่พบข้อมูลอุปกรณ์ในรายการนี้"}

        # ✅ อัปเดตสถานะใน rent_returns
        rent.status_id = 4  # คืนแล้ว
        rent.return_date = datetime.utcnow()

        # ✅ ดึง user_id จาก session แทน current_user
        user_id = session.get("user_id")
        if user_id:
            rent.check_by = user_id
            print(f"👤 CHECKED BY (session user_id): {user_id}")
        else:
            print("⚠️ ไม่พบ user_id ใน session — check_by จะเป็น None")

        # ✅ อัปเดตสถานะอุปกรณ์
        equipment.status = "available"
        print(f"🟢 DEBUG | RentID: {rent_id} | Equipment: {equipment.name} -> {equipment.status}")

        # ✅ commit จริงใน session เดียวกัน
        self.repo.commit()
        self.repo.close()

        return {"status": "success", "message": f"คืนอุปกรณ์ {equipment.name} สำเร็จ ✅"}

    def get_return_detail(self, rent_id: int):
        """ดึงรายละเอียดรายการเดียว"""
        r = self.repo.get_detail(rent_id)
        if not r:
            self.repo.close()
            return None

        data = {
            "rent_id": r.rent_id,
            "equipment_id": r.equipment_id,
            "equipment_code": r.equipment.code,
            "equipment_name": r.equipment.name,
            "brand": r.equipment.brand,
            "buy_date": (r.equipment.buy_date.strftime("%d/%m/%Y") if r.equipment.buy_date else "-"),
            "start_date": r.start_date.strftime("%d/%m/%Y") if r.start_date else "-",
            "due_date": r.due_date.strftime("%d/%m/%Y") if r.due_date else "-",
            "return_date": r.return_date.strftime("%d/%m/%Y") if r.return_date else "-",
            "user_id": r.user.user_id,
            "user_code": r.user.student_id or r.user.employee_id or "-",
            "user_name": r.user.name,
            "phone": r.user.phone or "-",
            "status_id": r.status_id,
            "image": (r.equipment.equipment_images[0].image_path
                      if getattr(r.equipment, "equipment_images", []) else None),
        }
        self.repo.close()
        return data
