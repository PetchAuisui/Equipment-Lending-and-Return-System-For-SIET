from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment
from sqlalchemy.orm import joinedload

class AdminReturnRepository:
    """Repository สำหรับจัดการข้อมูลการคืนอุปกรณ์"""
    def __init__(self):
        self.db = SessionLocal()

    def get_pending_returns(self, status_id: int):
        """ดึงรายการอุปกรณ์ที่รอคืน"""
        return (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment).joinedload(Equipment.equipment_images),
                joinedload(RentReturn.user)
            )
            .filter(RentReturn.status_id == status_id)
            .all()
        )

    def get_by_id(self, rent_id: int):
        """ดึงข้อมูลการยืมคืนตาม rent_id"""
        return (
            self.db.query(RentReturn)
            .options(joinedload(RentReturn.equipment))
            .filter(RentReturn.rent_id == rent_id)
            .first()
        )

    def get_detail(self, rent_id: int):
        """ดึงรายละเอียดเต็มของการคืน"""
        return (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment).joinedload(Equipment.equipment_images),
                joinedload(RentReturn.user),
                joinedload(RentReturn.status)
            )
            .filter(RentReturn.rent_id == rent_id)
            .first()
        )

    def commit(self):
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"❌ Commit error: {e}")
            raise

    def close(self):
        self.db.close()
