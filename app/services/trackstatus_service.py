# app/services/trackstatus_service.py
from flask import session, current_app
from app.repositories.trackstatus_repository import TrackStatusRepository
from app.repositories.item_broke_repository import ItemBrokeRepository

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
        # build a quick lookup of latest item_broke.type by rent_id so the track page
        # can reflect reports (lost/damaged) that are recorded in item_brokes table.
        try:
            ib_repo = ItemBrokeRepository()
            ib_list = ib_repo.list_all() or []
            latest_by_rent = {}
            for ib in ib_list:
                try:
                    rid = int(ib.get('rent_id') or 0)
                except Exception:
                    continue
                # keep the first encountered (list_all returns newest first)
                if rid and rid not in latest_by_rent:
                    latest_by_rent[rid] = ib
        except Exception:
            latest_by_rent = {}
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
            status_name = (status.get("name") or "")
            status_color = status.get("color_code")

            # if there is an item_broke report for this rent, prefer showing its type
            try:
                rid_val = int(r.get('rent_id') or 0)
            except Exception:
                rid_val = 0
            ib = latest_by_rent.get(rid_val)
            if ib:
                ib_type = (ib.get('type') or '').strip()
                if ib_type:
                    # If the rent currently has status_id == 1 (pending) and the item_broke
                    # type is 'lost', use the status_rents entry with id 8 (configured in DB)
                    try:
                        current_status_id = int(r.get('status_id') or 0)
                    except Exception:
                        current_status_id = 0

                    if ib_type.lower() == 'lost' and current_status_id == 1:
                        # try to map to status_rents.id == 8
                        mapped = self.repo.get_status_by_id(8)
                        if mapped:
                            status_name = mapped.get('name')
                            status_color = mapped.get('color_code')
                        else:
                            status_name = ib_type
                            status_color = '#d32f2f'
                    else:
                        # show the DB type directly (e.g., 'damaged') and use red for problematic states
                        status_name = ib_type
                        if ib_type.lower() in ('lost', 'damaged'):
                            status_color = '#d32f2f'  # red
            # โชว์ก่อนถ้ายังไม่คืน หรืออยู่ในสถานะ active
            still_active = (r.get("return_date") is None) or (status_name in ACTIVE_STATUSES)

            if still_active:
                items.append({
                    "rent_id": r.get("rent_id"),
                    "equipment_name": equip.get("name"),
                    "equipment_code": equip.get("code"),
                    "start_date": r.get("start_date"),
                    "due_date": r.get("due_date"),
                    "status_name": status_name,
                    "status_color": status_color,
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
