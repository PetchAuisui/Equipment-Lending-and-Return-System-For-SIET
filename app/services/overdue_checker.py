from datetime import datetime, timedelta, time
from app.db.db import SessionLocal
from app.models.rent import Rent
from app.models.notification import Notification
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Bangkok")   # ← NEW: โซนเวลาหลักที่ใช้คำนวณ

def check_overdue_rents():
    """
    ✅ หัวใจระบบแจ้งเตือนล่าช้า
    - ใช้เวลาแบบ aware (Asia/Bangkok) สำหรับคำนวณ
    - ก่อนคิวรี DB/บันทึก ให้ตัด tz ออก (naive) เพื่อเข้ากับคอลัมน์ DATETIME เดิม
    """
    db = SessionLocal()
    try:
        # ---------- เวลาอ้างอิง (aware) ----------
        now_aw = datetime.now(TZ)                      # ⏱️ เวลาปัจจุบันแบบ Asia/Bangkok (aware)
        created_count = 0

        cutoff_time = time(18, 0, 0)                   # 🕕 เส้นตายประจำวัน 18:00 (ไม่มี tz)
        today = now_aw.date()

        start_today_aw  = datetime.combine(today, time(0, 0), tzinfo=TZ)         # 00:00 วันนี้ (aware)
        cutoff_today_aw = datetime.combine(today, cutoff_time, tzinfo=TZ)        # 18:00 วันนี้ (aware)

        last30_aw   = now_aw + timedelta(minutes=30)                              # เส้น ≤ 30 นาที (aware)
        soon_upper_aw = (cutoff_today_aw if now_aw < cutoff_today_aw
                         else datetime.combine(today + timedelta(days=1), cutoff_time, tzinfo=TZ))

        # ---------- แปลงเป็น naive ก่อนคุยกับ DB ----------
        def _naive(d): return d.replace(tzinfo=None)

        now                   = _naive(now_aw)
        start_today           = _naive(start_today_aw)
        cutoff_today          = _naive(cutoff_today_aw)
        last_minute_threshold = _naive(last30_aw)
        soon_upper            = _naive(soon_upper_aw)

        base_not_returned = (Rent.status_id != 3)       # ยังไม่คืน

        def already_has(user_id, template, equipment_id):
            return db.query(Notification.notification_id).filter(
                Notification.user_id == user_id,
                Notification.template == template,
                Notification.payload.contains(f'"equipment_id": {equipment_id}')
            ).first() is not None

        def _close_prior(user_id, equipment_id, templates):
            # ปิดโนติขั้นก่อนหน้าสำหรับอุปกรณ์เดียวกัน
            db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.payload.contains(f'"equipment_id": {equipment_id}'),
                Notification.template.in_(templates),
                Notification.status == "unread"
            ).update({"status": "read"}, synchronize_session=False)

        # ========================= Queries =========================
        # 🟡 ใกล้ครบกำหนด: (> 30 นาที) .. ถึง cutoff รอบถัดไป
        rents_due_soon = db.query(Rent).filter(
            base_not_returned,
            Rent.due_date >  last_minute_threshold,
            Rent.due_date <= soon_upper
        ).all()

        # 🟠 เหลือไม่ถึง 30 นาที
        rents_due_very_soon = db.query(Rent).filter(
            base_not_returned,
            Rent.due_date >  now,
            Rent.due_date <= last_minute_threshold
        ).all()

        # 🔴 เกินกำหนด
        if now_aw >= cutoff_today_aw:   # ใช้ aware ตัดสินตรรกะวัน/รอบ
            overdue_rents = db.query(Rent).filter(
                base_not_returned,
                Rent.due_date <= cutoff_today
            ).all()
        else:
            overdue_rents = db.query(Rent).filter(
                base_not_returned,
                Rent.due_date < start_today
            ).all()

        # ========================= Creates =========================
        cutoff_str = cutoff_time.strftime("%H:%M")  # ใช้โชว์ในข้อความให้ตรงกัน
        created_ts = now                             # เวลาเซฟลง Notification (naive ให้ตรงกับคอลัมน์เดิม)

        # 🟡 due_soon
        for rent in rents_due_soon:
            if already_has(rent.user_id, "due_soon", rent.equipment_id):
                continue
            db.add(Notification(
                user_id=rent.user_id,
                channel="system",
                template="due_soon",
                payload={
                    "equipment_id": rent.equipment_id,
                    "equipment_name": rent.equipment.name if rent.equipment else "-",
                    "due_date": rent.due_date.strftime("%Y-%m-%d %H:%M"),
                    "message": f"อุปกรณ์ใกล้ครบกำหนด กรุณาคืนก่อน {cutoff_str} น."
                },
                send_at=created_ts, status="unread", created_at=created_ts,
            ))
            created_count += 1

        # 🟠 due_very_soon (ปิด due_soon ที่ค้าง)
        for rent in rents_due_very_soon:
            if already_has(rent.user_id, "due_very_soon", rent.equipment_id):
                continue
            db.add(Notification(
                user_id=rent.user_id,
                channel="system",
                template="due_very_soon",
                payload={
                    "equipment_id": rent.equipment_id,
                    "equipment_name": rent.equipment.name if rent.equipment else "-",
                    "due_date": rent.due_date.strftime("%Y-%m-%d %H:%M"),
                    "message": f"เหลือเวลาไม่ถึง 30 นาที ห้องจะปิด {cutoff_str} น. กรุณารีบคืน!"
                },
                send_at=created_ts, status="unread", created_at=created_ts,
            ))
            _close_prior(rent.user_id, rent.equipment_id, ["due_soon"])
            created_count += 1

        # 🔴 overdue_notice (ปิดทั้งสองขั้นก่อนหน้า)
        for rent in overdue_rents:
            if already_has(rent.user_id, "overdue_notice", rent.equipment_id):
                continue
            db.add(Notification(
                user_id=rent.user_id,
                channel="system",
                template="overdue_notice",
                payload={
                    "equipment_id": rent.equipment_id,
                    "equipment_name": rent.equipment.name if rent.equipment else "-",
                    "due_date": rent.due_date.strftime("%Y-%m-%d %H:%M"),
                    "message": "เกินกำหนด/ห้องปิดแล้ว กรุณาคืนวันถัดไปและชำระค่าปรับ"
                },
                send_at=created_ts, status="unread", created_at=created_ts,
            ))
            _close_prior(rent.user_id, rent.equipment_id, ["due_soon", "due_very_soon"])
            created_count += 1

        db.commit()
        return f"สร้างการแจ้งเตือนใหม่ {created_count} รายการ"

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
