from datetime import datetime, timezone
from sqlalchemy import func
from app.db.db import SessionLocal
from app.db import models as M

class HomeRepository:
    """เข้าถึงข้อมูลสำหรับหน้า Home"""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def get_top_borrowed(self, limit: int = 8):
        """
        อุปกรณ์ที่มีคนยืมมากที่สุด
        ✅ แสดงเฉพาะอุปกรณ์ที่ status = 'available'
        """
        with self._session_factory() as db:
            q = (
                db.query(
                    M.Equipment.equipment_id,
                    M.Equipment.name,
                    M.Equipment.code,
                    func.count(M.RentReturn.rent_id).label("borrow_count"),
                )
                .join(M.RentReturn, M.RentReturn.equipment_id == M.Equipment.equipment_id)
                .filter(func.lower(M.Equipment.status) == "available")  # ✅ กรองเฉพาะ available
                .group_by(M.Equipment.equipment_id, M.Equipment.name, M.Equipment.code)
                .order_by(func.count(M.RentReturn.rent_id).desc(), M.Equipment.name.asc())
                .limit(limit)
            )
            return q.all()

    def get_outstanding_by_user(self, user_id: int, limit: int = 10):
        """
        อุปกรณ์ที่ผู้ใช้นี้ยังไม่คืน
        ✅ return_date IS NULL และ user_id ตรงกับคนที่ล็อกอิน
        """
        with self._session_factory() as db:
            q = (
                db.query(
                    M.RentReturn.rent_id,
                    M.RentReturn.start_date,
                    M.RentReturn.due_date,
                    M.Equipment.name.label("equipment_name"),
                    M.Equipment.code.label("equipment_code"),
                    M.User.name.label("borrower_name"),
                )
                .join(M.Equipment, M.Equipment.equipment_id == M.RentReturn.equipment_id)
                .join(M.User, M.User.user_id == M.RentReturn.user_id)
                .filter(M.RentReturn.user_id == user_id)
                .filter(M.RentReturn.return_date.is_(None))
                .order_by(M.RentReturn.due_date.asc())
                .limit(limit)
            )

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            result = []
            for r in q.all():
                diff = (r.due_date.date() - now.date()).days
                result.append({
                    "rent_id": r.rent_id,
                    "equipment_name": r.equipment_name,
                    "equipment_code": r.equipment_code,
                    "borrower_name": r.borrower_name,
                    "start_date": r.start_date,
                    "due_date": r.due_date,
                    "is_overdue": diff < 0,
                    "overdue_days": abs(diff) if diff < 0 else 0,
                })
            return result
