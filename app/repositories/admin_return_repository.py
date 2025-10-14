from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, User

class AdminReturnRepository:
    """Repository สำหรับดึงและอัปเดตข้อมูลในตาราง rent_returns"""

    def __init__(self):
        self.session = SessionLocal()

    def get_pending_returns(self, status_id=3):
        """ดึงรายการอุปกรณ์ที่รอคืน"""
        rent_list = (
            self.session.query(RentReturn)
            .join(Equipment, RentReturn.equipment_id == Equipment.equipment_id)
            .join(User, RentReturn.user_id == User.user_id)
            .filter(RentReturn.status_id == status_id)
            .all()
        )
        return rent_list

    def get_by_id(self, rent_id):
        return self.session.query(RentReturn).get(rent_id)

    def update(self):
        self.session.commit()

    def close(self):
        self.session.close()
