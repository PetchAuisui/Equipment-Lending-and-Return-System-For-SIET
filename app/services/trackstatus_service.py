from flask import session
from app.repositories.trackstatus_repository import TrackStatusRepository

class TrackStatusService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_track_status_list(self):
        """ดึงข้อมูลทั้งหมด (รวมสถานะ) แล้วกรองเฉพาะ user ที่ login"""
        user_id = session.get("user_id")
        if not user_id:
            return []

        all_rents = self.repo.get_all_rent_returns_with_equipment()

        filtered = []
        for r in all_rents:
            if r["user_id"] == user_id:
                filtered.append({
                    "rent_id": r["rent_id"],
                    "equipment_name": r["equipment"]["name"],
                    "start_date": r["start_date"],
                    "due_date": r["due_date"],
                    # ✅ เพิ่มข้อมูลสถานะ
                    "status_name": r["status"]["name"],
                    "status_color": r["status"]["color_code"],
                })

        self.repo.close()
        return filtered
