from datetime import datetime
from app.db.db import SessionLocal
from app.models.rent import Rent
from app.models.notification import Notification
import json

def check_overdue_rents():
    """ตรวจสอบการยืมที่เกินกำหนดและสร้างการแจ้งเตือนใหม่"""
    db = SessionLocal()
    now = datetime.now()

    overdue_rents = db.query(Rent).filter(
        Rent.due_date < now,
        Rent.status_id != 3
    ).all()

    created_count = 0
    for rent in overdue_rents:
        # ตรวจว่ามีแจ้งเตือนที่ยังไม่อ่านอยู่ไหม
        existing_notif = db.query(Notification).filter(
            Notification.user_id == rent.user_id,
            Notification.template == "overdue_notice",
            Notification.status == "unread"
        ).first()

        if existing_notif:
            continue

        # ✅ สร้างการแจ้งเตือนใหม่
        payload = {
            "equipment_id": rent.equipment_id,
            "equipment_name": rent.equipment.name if rent.equipment else "-",
            "due_date": rent.due_date.strftime("%Y-%m-%d"),
        }

        new_notif = Notification(
            user_id=rent.user_id,
            channel="system",
            template="overdue_notice",
            payload=json.dumps(payload, ensure_ascii=False),  # ✅ เก็บเป็น JSON string
            send_at=datetime.now(),
            status="unread",
            created_at=datetime.now(),
        )
        db.add(new_notif)
        created_count += 1

    db.commit()
    db.close()
    return {"message": f"สร้างการแจ้งเตือนใหม่ {created_count} รายการ"}
