from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.db.db import SessionLocal
from app.repositories.home_repository import HomeRepository
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    """สร้างแจ้งเตือนให้เฉพาะผู้ที่ยืมของอยู่"""

    def __init__(self):
        self.db = SessionLocal()
        self.home_repo = HomeRepository(SessionLocal)
        self.notif_repo = NotificationRepository(self.db)

    def process_due_notifications(self):
        """
        ✅ ตรวจสอบของที่ยังไม่คืนจาก rent_returns
        - แจ้งเตือน 3 ระดับ (เกินกำหนด / พรุ่งนี้ถึงกำหนด / เหลือ 1 ชม.)
        """
        THAI_TZ = timezone(timedelta(hours=7))
        now = datetime.now(THAI_TZ).replace(tzinfo=None)
        created_count = 0

        # ✅ ดึงข้อมูลการยืมที่ยังไม่คืน
        with self.db as session:
            all_rents = session.execute(text("""
                SELECT rent_id, user_id, due_date, start_date
                FROM rent_returns
                WHERE return_date IS NULL
            """)).fetchall()

        # ✅ วนลูปตรวจสอบแต่ละรายการ
        for r in all_rents:
            rent_id = r.rent_id
            user_id = r.user_id
            due_raw = r.due_date

            # 🧠 แปลงเป็น datetime เสมอ
            try:
                due_str = str(due_raw).split('.')[0]
                due = datetime.strptime(due_str, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"[WARN] ❌ แปลง due_date ไม่ได้ rent_id={rent_id}, raw={due_raw} ({e})")
                continue

            diff_seconds = (due - now).total_seconds()
            diff_hours = diff_seconds / 3600
            diff_minutes = int(diff_seconds // 60)
            h, m = divmod(diff_minutes, 60)

            print(f"[DEBUG] rent_id={rent_id}, user_id={user_id}, due={due}, diff={h:02d}:{m:02d} (≈{diff_hours:.2f}h)")

            # ✅ 1. เกินกำหนดแล้ว (diff < 0)
            if diff_hours < 0:
                if self._create_notification(user_id, rent_id, "overdue", f"รายการยืม #{rent_id} เกินกำหนดคืนแล้ว!"):
                    created_count += 1

            # ✅ 2. เหลือเวลาไม่เกิน 1 ชั่วโมง (แจ้งเตือนสุดท้าย)
            elif 0 <= diff_hours <= 1:
                if self._create_notification(user_id, rent_id, "due_now", f"รายการยืม #{rent_id} จะครบกำหนดภายใน 1 ชั่วโมง!"):
                    created_count += 1

            # ✅ 3. เหลือเวลาไม่เกิน 24 ชั่วโมง (พรุ่งนี้ครบกำหนด)
            elif 1 < diff_hours <= 24:
                if self._create_notification(user_id, rent_id, "due_tomorrow", f"รายการยืม #{rent_id} ต้องคืนภายในวันพรุ่งนี้!"):
                    created_count += 1

        self.db.commit()
        print(f"✅ สร้างแจ้งเตือนใหม่ {created_count} รายการ\n")
        self.db.close()

    def _create_notification(self, user_id, rent_id, template, message):
        """✅ สร้างแจ้งเตือนใหม่ (ถ้ายังไม่มีในวันนี้)"""
        THAI_TZ = timezone(timedelta(hours=7))
        now = datetime.now(THAI_TZ).replace(tzinfo=None)

        # ตรวจว่ามีแจ้งเตือน rent_id เดิมในวันนี้ไหม
        if self.notif_repo.exists_today(user_id, rent_id, template):
            print(f"[SKIP] ⚠️ ข้าม {template} (rent_id={rent_id}) ของ user_id={user_id} (มีอยู่แล้ววันนี้)")
            return False

        # ✅ บันทึก rent_id ลงใน payload JSON
        self.notif_repo.create({
            "user_id": user_id,
            "channel": "system",
            "template": template,
            "payload": {
                "rent_id": rent_id,   # ✅ ใส่ rent_id ลง payload
                "message": message
            },
            "send_at": now,
            "status": "unread",
            "created_at": now,
        })
        print(f"[NEW] 🔔 เพิ่มแจ้งเตือน {template} (rent_id={rent_id}) ให้ user_id={user_id}")
        return True
