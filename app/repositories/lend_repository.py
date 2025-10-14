from app.db.db import SessionLocal
from app.db.models import Subject,User,RentReturn, Equipment
from datetime import datetime, time
from zoneinfo import ZoneInfo
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.orm import Session

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



def insert_rent_record(data):
    """
    ✅ บันทึกข้อมูลการยืมลงตาราง rent_returns
    และอัปเดตสถานะอุปกรณ์ในตาราง equipments
    """
    import time as pytime  # ใช้เวลารอระหว่าง retry
    from sqlalchemy.exc import SQLAlchemyError

    retry_delays = [5, 10, 30]  # วินาทีสำหรับ retry 3 ครั้ง
    max_retries = len(retry_delays)
    attempt = 0

    while attempt < max_retries:
        db = SessionLocal()
        try:
            # ------------------------------
            # ✅ LOCK ROW ของอุปกรณ์ที่จะยืม
            # ------------------------------
            equipment = db.execute(
                select(Equipment)
                .where(Equipment.code == data["code"])
                .with_for_update()  # lock row
            ).scalar_one_or_none()

            if not equipment:
                raise ValueError("❌ ไม่พบอุปกรณ์ที่เลือก")

            # ------------------------------
            # ✅ ตรวจสอบสถานะอุปกรณ์
            # ------------------------------
            if equipment.status != "available":
                raise ValueError("❌ อุปกรณ์นี้ถูกยืมไปแล้ว")

            # ------------------------------
            # หา user
            # ------------------------------
            user = db.query(User).filter(User.name == data["borrower_name"]).first()
            if not user:
                raise ValueError("❌ ไม่พบผู้ใช้ในระบบ")

            # ------------------------------
            # เตรียมค่า subject / teacher_confirmed
            # ------------------------------
            subject_val = data.get("subject_id")
            teacher_val = data.get("teacher_confirmed")

            # ------------------------------
            # ✅ แปลง datetime เป็น naive (SQLite compatible)
            # ------------------------------
            start_date = data["start_date"]
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            start_date = start_date.replace(tzinfo=None)

            due_date = datetime.combine(
                datetime.strptime(data["return_date"], "%Y-%m-%d").date(),
                time(hour=18, minute=0, second=0)
            ).replace(tzinfo=None)

            # ------------------------------
            # ✅ สร้าง RentReturn record
            # ------------------------------
            rent_record = RentReturn(
                equipment_id=equipment.equipment_id,
                user_id=user.user_id,
                subject_id=int(subject_val) if subject_val else None,
                start_date=start_date,
                due_date=due_date,
                teacher_confirmed=int(teacher_val) if teacher_val else None,
                reason=data.get("reason"),
                status_id=data["status_id"],
                created_at=datetime.utcnow()
            )
            db.add(rent_record)

            # ------------------------------
            # ✅ อัปเดตสถานะอุปกรณ์
            # ------------------------------
            equipment.status = "unavailable"
            db.add(equipment)

            # ------------------------------
            # ✅ COMMIT → ถ้า success → return
            # ------------------------------
            db.commit()
            db.close()
            print(f"✅ บันทึกการยืมและอัปเดตสถานะอุปกรณ์ (ID: {equipment.equipment_id}) เรียบร้อย")
            return {"status": "success"}

        except (SQLAlchemyError, ValueError) as e:
            db.rollback()
            db.close()
            attempt += 1
            print(f"⚠️ Attempt {attempt}/{max_retries} failed: {e}")

            # ------------------------------
            # ⏳ รอเวลาตาม retry_delays ก่อน retry ครั้งถัดไป
            # ------------------------------
            if attempt < max_retries:
                delay = retry_delays[attempt - 1]
                print(f"⏳ รอ {delay} วินาทีก่อน retry ครั้งถัดไป")
                pytime.sleep(delay)

    # ถ้า retry ครบ max_retries → fail
    print("❌ ล้มเหลวหลังจาก retry 3 ครั้ง")
    return {"status": "failed"}
