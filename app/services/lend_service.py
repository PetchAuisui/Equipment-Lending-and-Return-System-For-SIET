from app.repositories import lend_repository
from app.db.db import SessionLocal
from app.db.models import Equipment, User
from datetime import datetime


def get_all_subjects():
    return lend_repository.get_all_subjects()


def get_all_users():
    users = lend_repository.get_all_users()
    teachers = [
        {"user_id": u["user_id"], "name": u["name"]}
        for u in users if u["member_type"] in ["อาจารย์", "teacher"]
    ]
    return {"teachers": teachers}


def lend_data(data_list):
    """
    ✅ รับข้อมูลจากฟอร์มยืม แล้วบันทึกลงตาราง rent_returns ผ่าน repository
    โดยเช็ค member_type และ confirm ของอุปกรณ์ก่อนกำหนด status_id
    """
    print("📦 ข้อมูลการยืมที่ได้รับ:")
    print(data_list)

    db = SessionLocal()
    try:
        # ✅ ดึงข้อมูลจากฟอร์ม
        data = {
            "device_name": data_list[0],
            "code": data_list[1],
            "borrow_date": data_list[2],
            "return_date": data_list[3],
            "borrower_name": data_list[4],
            "phone": data_list[5],
            "major": data_list[6],
            "subject_id": data_list[7],
            "teacher_confirmed": data_list[8],
            "reason": data_list[9],
        }

        # ✅ หา user จากชื่อ
        user = db.query(User).filter(User.name == data["borrower_name"]).first()
        if not user:
            raise ValueError("❌ ไม่พบผู้ใช้ในระบบ")

        # ✅ หา equipment จาก code
        equipment = db.query(Equipment).filter(Equipment.code == data["code"]).first()
        if not equipment:
            raise ValueError("❌ ไม่พบอุปกรณ์ในระบบ")

        # ✅ ตั้งค่าเวลาเริ่มต้น
        data["start_date"] = datetime.utcnow()

        # ✅ ตรวจสอบ member_type เพื่อกำหนด status
        if user.member_type in ["teacher", "staff"]:
            data["status_id"] = 2  # approved
        else:
            # ถ้าเป็นนักศึกษา
            if equipment.confirm == 1:
                data["status_id"] = 1  # pending
            else:
                data["status_id"] = 2  # approved

        # ✅ ส่งข้อมูลไปบันทึก
        lend_repository.insert_rent_record(data)

    finally:
        db.close()
