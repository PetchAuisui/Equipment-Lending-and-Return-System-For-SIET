from app.db.db import SessionLocal
from app.db.models import User,RentReturn, Equipment
from sqlalchemy.exc import SQLAlchemyError


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


def insert_rent_record(data):
    """
    ✅ เขียนข้อมูลลงตาราง rent_returns
    และอัปเดตสถานะอุปกรณ์เป็น unavailable
    มีระบบ retry สูงสุด 3 ครั้ง หากเกิดข้อผิดพลาดระหว่างบันทึก
    """
    import time as pytime

    retry_delays = [5, 10, 30]  # หน่วงเวลาก่อน retry (วินาที)
    max_retries = len(retry_delays)
    attempt = 0

    while attempt < max_retries:
        db = SessionLocal()
        try:
            # ✅ บันทึกข้อมูลการยืม
            rent_record = RentReturn(**data)
            db.add(rent_record)

                    # ✅ อัปเดตสถานะอุปกรณ์เป็น unavailable
            equipment = db.query(Equipment).filter(Equipment.equipment_id == data["equipment_id"]).first()
            if equipment:
                equipment.status = "unavailable"
                db.add(equipment)

            # ✅ Commit การเปลี่ยนแปลง
            db.commit()
            db.close()

            print("✅ บันทึกข้อมูลเรียบร้อย และอัปเดตสถานะอุปกรณ์เป็น unavailable")
            return {"status": "success"}

        except SQLAlchemyError as e:
            db.rollback()
            db.close()
            attempt += 1
            print(f"⚠️ Attempt {attempt}/{max_retries} failed: {e}")

            if attempt < max_retries:
                delay = retry_delays[attempt - 1]
                print(f"⏳ รอ {delay} วินาทีก่อน retry ครั้งถัดไป")
                pytime.sleep(delay)

        finally:
            db.close()

    print("❌ ล้มเหลวหลังจาก retry 3 ครั้ง")
    return {"status": "failed"}
