# app/services/trackstatus_service.py
from flask import session, current_app
from app.repositories.trackstatus_repository import TrackStatusRepository

ACTIVE_STATUSES = {
    # สถานะที่ยังอยู่ระหว่างยืมหรือกระบวนการ
    "pending", "approved",
    "pending extend time", "approved extend time", "cancel extend time",
    "borrowing", "in progress",
}

class TrackStatusService:
    """รายการยืมแบบสั้น สำหรับหน้า list/track-status"""
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_track_status_list(self):
        # --- user_id ให้เป็น int แน่นอน ---
        try:
            user_id = int(session.get("user_id", 0))
        except (TypeError, ValueError):
            user_id = 0
        if not user_id:
            current_app.logger.info("[track] no user_id in session")
            return []

        all_rents = self.repo.get_all_rent_returns_with_equipment()
        current_app.logger.info("[track] total rents in db: %s", len(all_rents))

        items = []
        for r in all_rents:
            # cast r["user_id"] เป็น int
            try:
                r_uid = int(r.get("user_id"))
            except (TypeError, ValueError):
                continue
            if r_uid != user_id:
                continue

            status = (r.get("status") or {})
            equip  = (r.get("equipment") or {})
            status_name = (status.get("name") or "").lower()
            # โชว์ก่อนถ้ายังไม่คืน หรืออยู่ในสถานะ active
            still_active = (r.get("return_date") is None) or (status_name in ACTIVE_STATUSES)

            if still_active:
                items.append({
                    "rent_id": r.get("rent_id"),
                    "equipment_name": equip.get("name"),
                    "equipment_code": equip.get("code"),
                    "start_date": r.get("start_date"),
                    "due_date": r.get("due_date"),
                    "status_name": status.get("name"),
                    "status_color": status.get("color_code"),
                })

        current_app.logger.info("[track] rents for user %s: %s", user_id, len(items))
        self.repo.close()
        return items


class TrackStatusUserService:
    """รายละเอียดการยืม 1 รายการ (ใช้ในหน้า lend_detail)"""
    def __init__(self):
        self.repo = TrackStatusRepository()

    def get_user_track_status(self):
        try:
            user_id = int(session.get("user_id", 0))
        except (TypeError, ValueError):
            user_id = 0
        if not user_id:
            return []

        all_rents = self.repo.get_all_rent_returns_full()
        items = []
        for r in all_rents:
            try:
                r_uid = int(r.get("user_id"))
            except (TypeError, ValueError):
                continue
            if r_uid != user_id:
                continue

            items.append({
                "rent_id": r["rent_id"],
                "equipment_name": (r["equipment"] or {}).get("name"),
                "equipment_code": (r["equipment"] or {}).get("code"),
                "image_path": (r["equipment"] or {}).get("image_path"),
                "start_date": r["start_date"],
                "due_date": r["due_date"],
                "status_name": (r["status"] or {}).get("name"),
                "status_color": (r["status"] or {}).get("color_code"),
                "full_name": (r["user"] or {}).get("name"),
                "phone_number": (r["user"] or {}).get("phone"),
                "subject_name": (r["subject"] or {}).get("name"),
                "teacher_name": (r["teacher"] or {}).get("name"),
                "reason": r.get("reason"),
            })

        self.repo.close()
        return items
