from datetime import datetime, timezone, timedelta
from sqlalchemy import func, text
from app.db import models as M

class NotificationRepository:
    def __init__(self, db):
        self.db = db

    def create(self, data):
        notif = M.Notification(**data)
        self.db.add(notif)
        self.db.flush()
        return notif

    def exists_today(self, user_id, rent_id, template):
        """ตรวจสอบว่ามีแจ้งเตือน (ของ rent_id เดิม) วันนี้หรือยัง"""
        THAI_TZ = timezone(timedelta(hours=7))
        now = datetime.now(THAI_TZ).replace(tzinfo=None)
        today = now.date()

        return (
            self.db.query(M.Notification)
            .filter(M.Notification.user_id == user_id)
            .filter(M.Notification.template == template)
            .filter(func.date(M.Notification.created_at) == today)
            # ✅ ใช้ CAST → ให้ SQLite มอง rent_id เป็นตัวเลข (int) ตรงชนิดกัน
            .filter(text(f"CAST(json_extract(payload, '$.rent_id') AS INTEGER) = {rent_id}"))
            .first()
            is not None
        )
