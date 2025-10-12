from flask import request, render_template
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService, TrackStatusUserService



@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()
    return render_template("tracking/trackstatus.html", rents=rents)

@tracking_bp.get("/lend_detial")
def lend_detial():
    """แสดงรายละเอียดการยืมตาม rent_id"""
    rent_id = request.args.get("rent_id", type=int)  # ✅ รับค่าจาก URL เช่น /lend_detial?rent_id=3
    service = TrackStatusUserService()
    rents = service.get_user_track_status()

    rent = next((r for r in rents if r["rent_id"] == rent_id), None)

    return render_template("tracking/lend_detial.html", rent=rent)

@tracking_bp.get("/add_time")
def add_time():
    return render_template("tracking/add_time.html")