from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, StatusRent, Subject, User

class TrackStatusRepository:
    def __init__(self):
        self.db = SessionLocal()

    # -----------------------------
    # ✅ ของเดิม (อย่าแตะ) สำหรับ TrackStatusService
    # -----------------------------
    def get_all_rent_returns_with_equipment(self):
        """ดึงข้อมูล RentReturn ทั้งหมดพร้อมข้อมูลอุปกรณ์และสถานะ"""
        results = (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment),
                joinedload(RentReturn.status)
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

    # -----------------------------
    # ✅ ของใหม่ สำหรับ TrackStatusUserService (ใช้ /lend_detial)
    # -----------------------------
    def get_all_rent_returns_full(self):
        """ดึงข้อมูล RentReturn ทั้งหมด พร้อมข้อมูลอุปกรณ์, วิชา, สถานะ, และอาจารย์"""
        results = (
            self.db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment)
                    .joinedload(Equipment.equipment_images),  # ✅ โหลดรูปภาพอุปกรณ์
                joinedload(RentReturn.status),
                joinedload(RentReturn.subject),
                joinedload(RentReturn.teacher_confirm),     # ✅ โหลดอาจารย์ผู้อนุมัติ
            )
            .all()
        )

        data = []
        for r in results:
            # ✅ หา path ของภาพแรก (ถ้ามี)
            image_path = None
            if r.equipment and r.equipment.equipment_images:
                image_path = r.equipment.equipment_images[0].image_path

            data.append({
                "rent_id": r.rent_id,
                "user_id": r.user_id,
                "start_date": r.start_date,
                "due_date": r.due_date,
                "reason": r.reason,

                # ✅ Equipment
                "equipment": {
                    "name": getattr(r.equipment, "name", None),
                    "code": getattr(r.equipment, "code", None),
                    "image_path": image_path,
                },

                # ✅ Subject
                "subject": {
                    "name": getattr(r.subject, "subject_name", None),
                },

                # ✅ Teacher (จาก user)
                "teacher": {
                    "name": getattr(r.teacher_confirm, "name", None),
                },
            })
        return data

    def close(self):
        self.db.close()
