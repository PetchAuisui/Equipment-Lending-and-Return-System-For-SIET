from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from app.db.db import SessionLocal
from app.db import models as M

class HomeRepository:
    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def get_top_borrowed(self, limit: int = 8):
        """อุปกรณ์ยอดนิยม: เฉพาะที่ status = 'available' + มีรูป"""
        with self._session_factory() as db:
            # ใช้ subquery เพื่อหาภาพแรกของแต่ละอุปกรณ์
            subq = (
                db.query(
                    M.EquipmentImage.equipment_id,
                    func.min(M.EquipmentImage.equipment_image_id).label("first_image_id")
                )
                .group_by(M.EquipmentImage.equipment_id)
                .subquery()
            )

            q = (
                db.query(
                    M.Equipment.equipment_id,
                    M.Equipment.name,
                    M.Equipment.code,
                    func.count(M.RentReturn.rent_id).label("borrow_count"),
                    M.EquipmentImage.image_path.label("image_path"),
                )
                .join(M.RentReturn, M.RentReturn.equipment_id == M.Equipment.equipment_id)
                .outerjoin(subq, subq.c.equipment_id == M.Equipment.equipment_id)
                .outerjoin(M.EquipmentImage, M.EquipmentImage.equipment_image_id == subq.c.first_image_id)
                .filter(func.lower(M.Equipment.status) == "available")  # เฉพาะของที่ว่าง
                .group_by(
                    M.Equipment.equipment_id,
                    M.Equipment.name,
                    M.Equipment.code,
                    M.EquipmentImage.image_path
                )
                .order_by(func.count(M.RentReturn.rent_id).desc(), M.Equipment.name.asc())
                .limit(limit)
            )
            return q.all()


    def get_outstanding_by_user(self, user_id: int, limit: int = 10):
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

            # ใช้เวลาไทยแบบเต็ม ไม่ตัดเป็น .date()
            THAI_TZ = timezone(timedelta(hours=7))
            now = datetime.now(THAI_TZ).replace(tzinfo=None)

            result = []
            for r in q.all():
                # เปรียบเทียบเวลาจริงเต็ม ๆ
                diff_seconds = (r.due_date - now).total_seconds()
                is_overdue = diff_seconds < 0
                overdue_days = abs(diff_seconds) / 86400 if is_overdue else 0

                result.append({
                    "rent_id": r.rent_id,
                    "equipment_name": r.equipment_name,
                    "equipment_code": r.equipment_code,
                    "borrower_name": r.borrower_name,
                    "start_date": r.start_date,
                    "due_date": r.due_date,
                    "is_overdue": is_overdue,
                    "overdue_days": round(overdue_days, 2),
                })
            return result