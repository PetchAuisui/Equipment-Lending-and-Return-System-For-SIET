
from flask import render_template, redirect, url_for, flash,request
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService, TrackStatusUserService
from app.services.user_return_service import UserReturnService
from datetime import datetime
from app.db.db import SessionLocal
from app.db.models import RentReturn
from app.services import renewal_service


# หน้า list การยืมทั้งหมด
@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()
    return render_template("tracking/trackstatus.html", rents=rents)


@tracking_bp.get("/user_return/<int:rent_id>")
def user_return(rent_id):
    service = UserReturnService()
    rent_info = service.get_user_return_info(rent_id)
    return render_template("tracking/user_return.html", rent_info=rent_info)



@tracking_bp.post("/confirm_return/<int:rent_id>")
def confirm_return(rent_id):
    service = UserReturnService()
    result = service.confirm_return(rent_id)

    if result:
        flash("อัปเดตสถานะการคืนเรียบร้อยแล้ว", "success")
    else:
        flash("เกิดข้อผิดพลาด ไม่สามารถอัปเดตข้อมูลได้", "error")
    return redirect(url_for("tracking.track_index"))


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

@tracking_bp.route('/return/<int:equipment_id>')
def show_return_item(equipment_id):
    db = get_db()
    item = db.execute("""
        SELECT r.id, e.name, r.return_date, r.student_id, s.name AS student_name, e.image_url
        FROM rentals r
        JOIN equipment e ON r.equipment_id = e.id
        JOIN students s ON r.student_id = s.id
        WHERE e.id = ?
    """, (equipment_id,)).fetchone()

    return render_template('return_equipment.html', item=item, current_date=date.today())

@tracking_bp.route('/detail/<int:equipment_id>')
def detail(equipment_id):
    # ดึงข้อมูลอุปกรณ์ถ้าต้องการ (ตอนนี้ placeholder ไว้ก่อน)
    return render_template('pages_tracking/detail.html', equipment_id=equipment_id)