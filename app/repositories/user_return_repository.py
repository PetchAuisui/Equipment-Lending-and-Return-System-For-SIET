# app/repositories/user_return_repository.py

from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, StatusRent
from datetime import datetime

class UserReturnRepository:
    def get_rent_return_by_id(self, rent_id: int):
        """ดึงข้อมูลการยืม-คืน พร้อมข้อมูลอุปกรณ์, รูปภาพ, สถานะ"""
        session = SessionLocal()
        try:
            rent_return = (
                session.query(RentReturn)
                .options(
                    joinedload(RentReturn.equipment).joinedload(Equipment.equipment_images),
                    joinedload(RentReturn.status)
                )
                .filter(RentReturn.rent_id == rent_id)
                .first()
            )
            return rent_return
        finally:
            session.close()

    def confirm_return(self, rent_id: int):
        """อัปเดต status_id เป็น 3 และตั้ง return_date เป็นปัจจุบัน"""
        session = SessionLocal()
        try:
            rent = session.query(RentReturn).filter(RentReturn.rent_id == rent_id).first()
            if rent:
                rent.status_id = 3
                rent.return_date = datetime.utcnow()
                session.commit()
            return rent
        finally:
            session.close()
