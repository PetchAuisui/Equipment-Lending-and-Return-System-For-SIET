# app/repositories/trackstatus_repository.py
from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment

class TrackStatusRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_rent_returns_with_equipment(self):
        """ดึงข้อมูล RentReturn ทั้งหมดพร้อมชื่ออุปกรณ์"""
        results = (
            self.db.query(RentReturn)
            .options(joinedload(RentReturn.equipment))
            .all()
        )

        data = []
        for r in results:
            data.append({
                "rent_id": r.rent_id,
                "equipment_id": r.equipment_id,
                "equipment_name": getattr(r.equipment, "name", None),
                "user_id": r.user_id,
                "start_date": r.start_date,
                "due_date": r.due_date,
            })
        return data

    def close(self):
        self.db.close()
