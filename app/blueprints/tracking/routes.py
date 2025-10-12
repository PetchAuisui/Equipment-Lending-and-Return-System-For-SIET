from flask import render_template
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService, TrackStatusUserService

@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()
    return render_template("tracking/trackstatus.html", rents=rents)

@tracking_bp.get("/lend_detial")
def lend_detial():
    """แสดงรายละเอียดการยืมของผู้ใช้ที่ล็อกอิน"""
    service = TrackStatusUserService()
    rents = service.get_user_track_status()  # ✅ ดึงข้อมูลจาก Service
    return render_template("tracking/lend_detial.html", rents=rents)
