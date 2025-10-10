from app.db.db import SessionLocal
from app.db.models import Subject  # ✅ เพิ่ม import
from app.db.models import User    # ✅ เพิ่ม import

def get_all_subjects():
    """
    ดึงข้อมูลวิชาทั้งหมดจากตาราง subjects
    """
    db = SessionLocal()
    try:
        subjects = db.query(Subject).all()
        return [
            {
                "subject_id": s.subject_id,
                "subject_code": s.subject_code,
                "subject_name": s.subject_name
            }
            for s in subjects
        ]
    finally:
        db.close()

def get_all_users():
    """
    ดึงข้อมูลผู้ใช้ทั้งหมดจากตาราง users
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [
            {
                "user_id": u.user_id,
                "name": u.name,
                "member_type": u.member_type
            }
            for u in users
        ]
    finally:
        db.close()


from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, User

def insert_rent_record(data):
    """
    ✅ บันทึกข้อมูลการยืมลงตาราง rent_returns
    """
    db = SessionLocal()
    try:
        # หา equipment_id จาก code
        equipment = db.query(Equipment).filter(Equipment.code == data["code"]).first()
        if not equipment:
            raise ValueError("❌ ไม่พบอุปกรณ์ที่เลือก")

        # หา user_id จากชื่อ (ในระบบจริงใช้ current_user.user_id แทนได้)
        user = db.query(User).filter(User.name == data["borrower_name"]).first()
        if not user:
            raise ValueError("❌ ไม่พบผู้ใช้ในระบบ")

        # ✅ สร้าง record RentReturn
        rent_record = RentReturn(
            equipment_id=equipment.equipment_id,
            user_id=user.user_id,
            subject_id=int(data["subject_id"]),
            start_date=data["start_date"],
            due_date=datetime.strptime(data["return_date"], "%Y-%m-%d"),
            teacher_confirmed=int(data["teacher_confirmed"]) if data["teacher_confirmed"] else None,
            reason=data.get("reason"),
            status_id=data["status_id"],
            created_at=datetime.utcnow()
        )

        # ✅ บันทึกลงฐานข้อมูล
        db.add(rent_record)
        db.commit()
        print("✅ บันทึก RentReturn สำเร็จ")

    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Database Error:", e)
        raise e
    finally:
        db.close()
