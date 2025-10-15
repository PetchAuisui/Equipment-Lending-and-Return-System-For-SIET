# app/services/lend_service.py
from app.repositories import lend_repository
from app.db.db import SessionLocal
from app.db.models import Equipment, User
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from flask import flash, redirect, url_for, current_app
from app.repositories.lend_repository import insert_rent_record


def get_all_subjects():
    return lend_repository.get_all_subjects()


def get_all_users():
    users = lend_repository.get_all_users()
    teachers = [
        {"user_id": u["user_id"], "name": u["name"]}
        for u in users if u["member_type"] in ["อาจารย์", "teacher"]
    ]
    return {"teachers": teachers}


# services/lend_service.py
def lend_data_service(data):
    db = SessionLocal()
    try:
        # ✅ ใช้ user_id แทน id
        user = db.query(User).filter(User.user_id == data["borrower_id"]).first()
        if not user:
            raise ValueError("❌ ไม่พบผู้ใช้ในระบบ")

        equipment = db.query(Equipment).filter(Equipment.code == data["code"]).first()
        if not equipment:
            raise ValueError("❌ ไม่พบอุปกรณ์ในระบบ")

        # ... (ส่วนอื่นเหมือนเดิม)


        # ✅ เวลาโซน Bangkok
        now_bkk = datetime.now(ZoneInfo("Asia/Bangkok")).replace(tzinfo=None)

        # ✅ กำหนด status อัตโนมัติ
        if user.member_type in ["teacher", "officer"]:
            status_id = 2  # approved
        else:
            status_id = 1 if equipment.confirm == 1 else 2

        # ✅ เตรียมข้อมูลสำหรับบันทึก
        rent_data = {
            "equipment_id": equipment.equipment_id,
            "user_id": user.user_id,
            "start_date": now_bkk,
            "due_date": datetime.strptime(data["return_date"], "%Y-%m-%d"),
            "teacher_confirmed": data.get("teacher_confirmed"),
            "reason": data.get("reason"),
            "status_id": status_id,
            "created_at": now_bkk,
        }

        # ✅ เรียก repository เพื่อบันทึก (มี retry 3 ครั้งภายใน)
        result = insert_rent_record(rent_data)

        if result.get("status") == "success":
            # ✅ อัปเดตสถานะอุปกรณ์เป็น unavailable
            equipment.status = "unavailable"
            db.commit()
            flash("✅ บันทึกการยืมสำเร็จ", "success")
        else:
            flash("❌ ล้มเหลวหลังจาก retry 3 ครั้ง กรุณาลองใหม่", "danger")

    except ValueError as ve:
        flash(str(ve), "warning")
    except Exception as e:
        current_app.logger.error(f"lend_data_service error: {e}")
        flash("❌ เกิดข้อผิดพลาดของระบบ กรุณาลองใหม่อีกครั้ง", "danger")
    finally:
        db.close()

    # ✅ กลับหน้า track เสมอ
    return redirect(url_for("tracking.track_index"))
