from flask import session
from app.repositories.trackstatus_repository import TrackStatusRepository


# ------------------------------------------------------------------
# ✅ Service หน้าแรก (รายการสถานะ)
# ------------------------------------------------------------------
class TrackStatusService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_track_status_list(self):
        """ดึงข้อมูลของ user ที่ login เฉพาะสถานะ pending / approved"""
        user_id = session.get("user_id")
        if not user_id:
            return []

        all_rents = self.repo.get_all_rent_returns_with_equipment()

        filtered = [
            {
                "rent_id": r["rent_id"],
                "equipment_name": r["equipment"]["name"],
                "start_date": r["start_date"],
                "due_date": r["due_date"],
                "status_name": r["status"]["name"],
                "status_color": r["status"]["color_code"],
            }
            for r in all_rents
            if r["user_id"] == user_id and r["status"]["name"] in ["pending", "approved"]
        ]

        self.repo.close()
        return filtered


# ------------------------------------------------------------------
# ✅ Service หน้า lend_detail (รายละเอียด)
# ------------------------------------------------------------------
class TrackStatusUserService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_user_track_status(self):
        """ดึงข้อมูลการยืมของ user ที่ล็อกอิน (พร้อมข้อมูลครบ)"""
        user_id = session.get("user_id")
        if not user_id:
            return []

        all_rents = self.repo.get_all_rent_returns_full()

        user_rents = [
            {
                "rent_id": r["rent_id"],
                "equipment_name": r["equipment"]["name"],
                "equipment_code": r["equipment"]["code"],
                "image_path": r["equipment"]["image_path"],
                "start_date": r["start_date"],
                "due_date": r["due_date"],
                "status_name": r["status"]["name"],
                "status_color": r["status"]["color_code"],
                "full_name": r["user"]["name"],
                "phone_number": r["user"]["phone"],
                "subject_name": r["subject"]["name"],
                "teacher_name": r["teacher"]["name"],
                "reason": r["reason"],
            }
            for r in all_rents if r["user_id"] == user_id
        ]

        self.repo.close()
        return user_rents
