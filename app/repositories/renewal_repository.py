from datetime import datetime
from app.db.db import SessionLocal
from app.db.models import Renewal, RentReturn

def insert_renewal(data):
    """
    ✅ เพิ่มข้อมูลคำขอขยายเวลาลงตาราง renewals
    และอัปเดตสถานะ rent_returns.status_id = 5 โดยไม่เช็กเงื่อนไข
    """
    db = SessionLocal()
    try:
        # ✅ 1. เพิ่ม record ใหม่ในตาราง renewals
        new_record = Renewal(
            rent_id=data["rent_id"],
            old_due=data["old_due"],
            new_due=data["new_due"],
            note=data["note"],
            created_at=data["created_at"],
            status="pending"
        )
        db.add(new_record)

        # ✅ 2. อัปเดต status_id = 5 ใน rent_returns โดยไม่ต้องเช็ก
        db.query(RentReturn).filter(RentReturn.rent_id == data["rent_id"]).update(
            {"status_id": 5}
        )
        print(f"🔄 อัปเดต RentReturn ID={data['rent_id']} → status_id=5")

        # ✅ 3. commit พร้อมกัน
        db.commit()
        print(f"✅ บันทึกคำขอขยายเวลา rent_id={data['rent_id']} สำเร็จ")

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
        exists = db.query(Renewal).filter(
            Renewal.rent_id == rent_id,
            Renewal.status == "pending"
        ).first() is not None
        if exists:
            print(f"⚠️ พบคำขอ pending สำหรับ rent_id={rent_id}")
        return exists
    finally:
        db.close()
