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
    db = SessionLocal()
    try:
        # ------------------------------
        # ✅ LOCK ROW ของอุปกรณ์ที่จะยืม
        # ------------------------------
        # เพิ่ม with_for_update() เพื่อป้องกันหลาย process แก้ไขอุปกรณ์เดียวกันพร้อมกัน
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
        # ✅ สร้าง RentReturn record
        # ------------------------------
        rent_record = RentReturn(
            equipment_id=equipment.equipment_id,
            user_id=user.user_id,
            subject_id=int(subject_val) if subject_val else None,
            start_date=data["start_date"],
            due_date=datetime.combine(
                datetime.strptime(data["return_date"], "%Y-%m-%d").date(),
                time(hour=18, minute=0, second=0)
            ).replace(tzinfo=ZoneInfo("Asia/Bangkok")),
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
        # ✅ COMMIT ด้วยตัวเอง
        # ------------------------------
        db.commit()
        print(f"✅ บันทึกการยืมและอัปเดตสถานะอุปกรณ์ (ID: {equipment.equipment_id}) เรียบร้อย")

    except SQLAlchemyError as e:
        # ------------------------------
        # ✅ ROLLBACK เมื่อเกิด error
        # ------------------------------
        db.rollback()
        print("❌ Database Error:", e)
        raise e
    finally:
        db.close()
