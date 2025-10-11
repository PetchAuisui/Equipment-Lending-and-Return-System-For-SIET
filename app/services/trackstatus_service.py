# app/services/trackstatus_service.py
from flask import session
from app.repositories.trackstatus_repository import TrackStatusRepository

class TrackStatusService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_track_status_list(self):
        """ดึงข้อมูลทั้งหมด แล้วกรองเฉพาะของผู้ใช้ที่ login อยู่จาก session"""
        user_id = session.get("user_id")
        if not user_id:
            return []  # ถ้ายังไม่ได้ login จะไม่ส่งข้อมูลกลับ

        all_rents = self.repo.get_all_rent_returns_with_equipment()

        # กรองเฉพาะข้อมูลของ user ปัจจุบัน
        filtered = [
            {
                "rent_id": r["rent_id"],
                "equipment_name": r["equipment_name"],
                "start_date": r["start_date"],
                "due_date": r["due_date"],
            }
            for r in all_rents
            if r["user_id"] == user_id
        ]

        self.repo.close()
        return filtered
