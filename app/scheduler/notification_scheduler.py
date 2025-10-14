# app/scheduler/notification_scheduler.py
import os
import threading
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.notification_service import NotificationService


_scheduler_started = False  # ✅ ป้องกันรันซ้ำหลายรอบ


def start_notification_scheduler(app):
    """⏰ สร้าง Background Scheduler สำหรับตรวจสอบแจ้งเตือนอัตโนมัติ"""
    global _scheduler_started

    should_start_scheduler = not app.testing and (
        not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    )

    if should_start_scheduler and not _scheduler_started:
        _scheduler_started = True

        scheduler = BackgroundScheduler(timezone="Asia/Bangkok", daemon=True)

        def job_check_due():
            """🔔 Task ที่รันซ้ำทุกระยะเวลา"""
            thread_id = threading.current_thread().ident
            with app.app_context():
                app.logger.info(f"🔔 Running job_check_due (thread={thread_id})")
                NotificationService().process_due_notifications()

        scheduler.add_job(
            func=job_check_due,
            trigger="interval",
            seconds=30,  # 🔁 เปลี่ยนรอบเวลาได้ เช่น 180 = 3 นาที
            id="check_due_notifications",
            replace_existing=True,
            coalesce=True,
            misfire_grace_time=300,
            max_instances=1,
        )

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown(wait=False))
        app.logger.info("✅ Scheduler started: ตรวจสอบแจ้งเตือนทุก 30 วินาที")

    else:
        app.logger.info("⏩ Scheduler already running, skip duplicate start")
