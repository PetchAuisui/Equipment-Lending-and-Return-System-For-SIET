from flask import session
from app.repositories.trackstatus_repository import TrackStatusRepository


# ------------------------------
# ✅ Service เดิม (Track หน้าแรก)
# ------------------------------
class TrackStatusService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_track_status_list(self):
        """ดึงข้อมูลทั้งหมด (รวมสถานะ) แล้วกรองเฉพาะ user ที่ login
           และเฉพาะ status = pending, approved เท่านั้น
        """
        user_id = session.get("user_id")
        if not user_id:
            return []

        # ✅ ดึงข้อมูลทั้งหมดจาก repository
        all_rents = self.repo.get_all_rent_returns_with_equipment()

        # ✅ กรองเฉพาะของ user และสถานะ pending / approved
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


# ------------------------------
# ✅ Service ใหม่ (หน้า lend_detail)
# ------------------------------
class TrackStatusUserService:
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_user_track_status(self):
        """ดึงข้อมูลการยืมของ user ที่ล็อกอิน (ข้อมูลครบเหมือนใน repository)"""
        user_id = session.get("user_id")
        if not user_id:
            return []

        # ✅ ดึงข้อมูลทั้งหมดแบบ full join จาก repository
        all_rents = self.repo.get_all_rent_returns_full()

        # ✅ กรองเฉพาะของ user ที่ล็อกอิน
        user_rents = [r for r in all_rents if r["user_id"] == user_id]

        self.repo.close()
        return user_rents
