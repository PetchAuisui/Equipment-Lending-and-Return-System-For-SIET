# app/repositories/user_return_repository.py

from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment
from datetime import datetime

class UserReturnRepository:
    def get_rent_return_by_id(self, rent_id: int):
        """ดึงข้อมูลการยืมพร้อมโหลดความสัมพันธ์ที่จำเป็น"""
        db = SessionLocal()
        try:
            rent = (
                db.query(RentReturn)
                .options(
                    joinedload(RentReturn.equipment).joinedload(Equipment.equipment_images),
                    joinedload(RentReturn.status)
                )
                .filter_by(rent_id=rent_id)
                .first()
            )
            return rent
        finally:
            db.close()

    def confirm_return(self, rent_id: int):
        """อัปเดตสถานะการคืนอุปกรณ์"""
        db = SessionLocal()
        try:
            rent_return = db.query(RentReturn).filter_by(rent_id=rent_id).first()
            if not rent_return:
                return False

            # ✅ เปลี่ยนสถานะและบันทึกวันเวลาคืน
            rent_return.status_id = 3
            rent_return.return_date = datetime.now()

            db.add(rent_return)  # << สำคัญ เพื่อให้ session track object
            db.commit()
            db.refresh(rent_return)  # << บังคับ refresh ค่าใหม่จาก DB

            print(f"✅ Updated rent_id={rent_id} to status_id={rent_return.status_id}, return_date={rent_return.return_date}")
            return True

        except Exception as e:
            db.rollback()
            print("❌ Error confirming return:", e)
            return False
        finally:
            db.close()
