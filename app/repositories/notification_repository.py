# app/repositories/notification_repository.py
from datetime import datetime, timezone, timedelta, time, date
from sqlalchemy import func, cast, Integer, and_, select, exists
from sqlalchemy.dialects.postgresql import JSONB
from app.db import models as M


class NotificationRepository:
    def __init__(self, db):
        # db = SQLAlchemy Session
        self.db = db

    def create(self, data):
        notif = M.Notification(**data)
        self.db.add(notif)
        self.db.flush()
        return notif

    def exists_today(self, user_id, rent_id, template, day: date | None = None) -> bool:
        """
        ตรวจสอบว่ามีแจ้งเตือน (ของ rent_id เดิม) วันนี้หรือยัง
        - กรองช่วงเวลาวันนี้ [00:00, 24:00) ตามโซนเวลาไทย
        - รองรับทั้ง PostgreSQL และ SQLite ในการอ่านค่า rent_id จาก JSON payload
        """
        # ใช้โซนเวลาไทยตามเดิม
        THAI_TZ = timezone(timedelta(hours=7))
        now_th = datetime.now(THAI_TZ)
        d = day or now_th.date()

        # ใช้กรองช่วงเวลา (เลี่ยง func.date(...)) เพื่อให้ใช้ดัชนีได้ดีและไม่เจอปัญหา dialect
        start = datetime.combine(d, time.min)  # naive
        end = start + timedelta(days=1)        # [start, end)

        base_filters = [
            M.Notification.user_id == user_id,
            M.Notification.template == template,
            M.Notification.created_at >= start,
            M.Notification.created_at < end,
        ]

        # ระบุ dialect ปัจจุบันจาก session
        dialect = (self.db.bind and self.db.bind.dialect.name) or ""

        # สร้าง expression ของ rent_id จาก JSON payload ให้เหมาะกับแต่ละ DB
        if dialect == "postgresql":
            # payload อาจเป็น TEXT -> cast เป็น JSONB ก่อน แล้วดึง ['rent_id'] เป็น text -> cast เป็น int
            rent_id_expr = cast(cast(M.Notification.payload, JSONB)["rent_id"].astext, Integer)
        else:
            # SQLite (และ MySQL ที่มี json_extract)
            rent_id_expr = cast(func.json_extract(M.Notification.payload, "$.rent_id"), Integer)

        filters = and_(*base_filters, rent_id_expr == rent_id)

        # ใช้ EXISTS เร็วและชัดเจนกว่า .first() != None
        stmt = select(exists().where(filters))
        return bool(self.db.execute(stmt).scalar())
