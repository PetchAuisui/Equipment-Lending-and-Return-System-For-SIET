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