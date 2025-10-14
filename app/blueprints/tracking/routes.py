from flask import render_template, redirect, url_for, flash
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService
from app.services.user_return_service import UserReturnService
from datetime import datetime
from app.db.db import SessionLocal
from app.db.models import RentReturn


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

"""@tracking_bp.post("/confirm_return/<int:rent_id>")
def confirm_return(rent_id):
    session = SessionLocal()
    try:
        rent = session.query(RentReturn).filter(RentReturn.rent_id == rent_id).first()
        if rent:
            rent.status_id = 3  # เปลี่ยน status เป็น 3
            rent.return_date = datetime.utcnow()  # เพิ่มวันที่คืนปัจจุบัน
            session.commit()
    finally:
        session.close()
    
    return redirect(url_for("tracking.track_index"))  # กลับไปหน้า list """

@tracking_bp.post("/confirm_return/<int:rent_id>")
def confirm_return(rent_id):
    service = UserReturnService()
    result = service.confirm_return(rent_id)

    if result:
        flash("อัปเดตสถานะการคืนเรียบร้อยแล้ว", "success")
    else:
        flash("เกิดข้อผิดพลาด ไม่สามารถอัปเดตข้อมูลได้", "error")

    return redirect(url_for("tracking.track_index"))
