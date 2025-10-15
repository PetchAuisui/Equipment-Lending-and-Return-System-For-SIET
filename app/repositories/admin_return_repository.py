from app.db.db import SessionLocal
from app.db.models import Equipment, RentReturn, User
from sqlalchemy.orm import joinedload

class AdminReturnRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_pending_returns(self, status_id: int):
        return (
            self.db.query(RentReturn)
            .join(RentReturn.equipment)
            .join(RentReturn.user)
            .filter(RentReturn.status_id == status_id)
            .all()
        )

    def get_by_id(self, rent_id):
        """ดึงข้อมูลรายการเดียว (เชื่อมกับ Equipment)"""
        return (
            self.db.query(RentReturn)
            .options(joinedload(RentReturn.equipment))
            .filter(RentReturn.rent_id == rent_id)
            .first()
        )

    def get_detail(self, rent_id):
        """ดึงรายละเอียดเต็มสำหรับหน้า return_detail"""
        return (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment).joinedload("equipment_images"),
                joinedload(RentReturn.user),
                joinedload(RentReturn.status),
            )
            .filter(RentReturn.rent_id == rent_id)
            .first()
        )

    def commit(self):
        """commit การเปลี่ยนแปลงทั้งหมด"""
        try:
            print("💾 COMMITTING CHANGES ...")
            self.db.commit()  # ✅ ใช้ self.db.commit() ไม่ใช่ db.session.commit()
            print("✅ COMMIT SUCCESS")
        except Exception as e:
            self.db.rollback()
            print(f"❌ COMMIT FAILED: {e}")

    def close(self):
        self.db.close()
