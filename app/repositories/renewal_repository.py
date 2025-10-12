from datetime import datetime
from app.db.db import SessionLocal
from app.db.models import Renewal

def insert_renewal(data):
    """
    ✅ เพิ่มข้อมูลคำขอขยายเวลาลงตาราง renewals
    """
    db = SessionLocal()
    try:
        new_record = Renewal(
            rent_id=data["rent_id"],
            old_due=data["old_due"],
            new_due=data["new_due"],
            note=data["note"],
            created_at=data["created_at"],
            status="pending"
        )
        db.add(new_record)
        db.commit()
        print(f"✅ บันทึกคำขอขยายเวลา rent_id={data['rent_id']}")
    except Exception as e:
        db.rollback()
        print("❌ Database Error:", e)
        raise
    finally:
        db.close()

def is_pending_request_exists(rent_id):
    """
    ✅ ตรวจสอบว่ามีคำขอ pending สำหรับ rent_id นี้หรือยัง
    """
    db = SessionLocal()
    try:
        return db.query(Renewal).filter(
            Renewal.rent_id == rent_id,
            Renewal.status == "pending"
        ).first() is not None
    finally:
        db.close()
