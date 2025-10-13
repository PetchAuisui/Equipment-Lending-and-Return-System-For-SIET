from flask import request, render_template, redirect, url_for, flash
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService, TrackStatusUserService
from flask import render_template, request
from app.services import renewal_service

# หน้า list การยืมทั้งหมด
@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()
    return render_template("tracking/trackstatus.html", rents=rents)

# หน้า detail ของการยืม
@tracking_bp.get("/lend_detial")
def lend_detial():
    rent_id = request.args.get("rent_id", type=int)
    service = TrackStatusUserService()
    rents = service.get_user_track_status()
    rent = next((r for r in rents if r["rent_id"] == rent_id), None)
    return render_template("tracking/lend_detial.html", rent=rent)

# หน้าเพิ่มเวลาการยืม
@tracking_bp.get("/add_time")
def add_time():
    rent_id = request.args.get("rent_id", type=int)
    service = TrackStatusUserService()
    rents = service.get_user_track_status()
    rent = next((r for r in rents if r["rent_id"] == rent_id), None)
    return render_template("tracking/add_time.html", rent=rent)



@tracking_bp.route("/add_time_submit", methods=["POST"])
def add_time_submit():
    """
    ✅ รับข้อมูลจากฟอร์ม /add_time แล้วส่งให้ renewal_service
    """
    form = request.form
    data = {
        "rent_id": form.get("rent_id"),
        "old_due": form.get("old_due"),
        "new_due": form.get("new_due"),
        "reason": form.get("extend_reason"),
        "created_at": form.get("created_at"),
    }

    # ✅ เรียกไปที่ service
    ok, msg = renewal_service.create_renewal(data)

    if ok:
        flash("✅ ส่งคำขอขยายเวลาสำเร็จ", "success")
    else:
        flash(f"❌ {msg}", "error")

    return redirect(url_for("tracking.track_index"))

@tracking_bp.get("/comfirm_add_time")
def comfirm_add_time():
    return render_template("tracking/comfirm_add_time.html")