from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, StatusRent

class TrackStatusRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_rent_returns_with_equipment(self):
        """ดึงข้อมูล RentReturn ทั้งหมดพร้อมข้อมูลอุปกรณ์และสถานะ"""
        results = (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment),  # โหลดอุปกรณ์
                joinedload(RentReturn.status)      # โหลดสถานะ
            )
            .all()
        )

        data = []
        for r in results:
            data.append({
                # ✅ RentReturn
                "rent_id": r.rent_id,
                "equipment_id": r.equipment_id,
                "user_id": r.user_id,
                "subject_id": r.subject_id,
                "start_date": r.start_date,
                "due_date": r.due_date,
                "teacher_confirmed": r.teacher_confirmed,
                "reason": r.reason,
                "return_date": r.return_date,
                "check_by": r.check_by,
                "status_id": r.status_id,
                "created_at": r.created_at,

                # ✅ Equipment
                "equipment": {
                    "equipment_id": getattr(r.equipment, "equipment_id", None),
                    "name": getattr(r.equipment, "name", None),
                    "code": getattr(r.equipment, "code", None),
                    "category": getattr(r.equipment, "category", None),
                    "confirm": getattr(r.equipment, "confirm", None),
                    "detail": getattr(r.equipment, "detail", None),
                    "brand": getattr(r.equipment, "brand", None),
                    "buy_date": getattr(r.equipment, "buy_date", None),
                    "status": getattr(r.equipment, "status", None),
                    "created_at": getattr(r.equipment, "created_at", None),
                },

                # ✅ StatusRent
                "status": {
                    "status_id": getattr(r.status, "status_id", None),
                    "name": getattr(r.status, "name", None),
                    "color_code": getattr(r.status, "color_code", None),
                }
            })
        return data

    def close(self):
        self.db.close()
