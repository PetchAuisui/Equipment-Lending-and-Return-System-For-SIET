from datetime import datetime
from app.db.db import SessionLocal
from app.db.models import Renewal, RentReturn, User, Equipment, EquipmentImage


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


def get_renewal_info(rent_id: int):
    """
    ✅ ดึงข้อมูลคำขอขยายเวลาล่าสุดของ rent_id
    รวมข้อมูลชื่อผู้ยืม, ชื่ออุปกรณ์, วันที่ยืม, วันที่ครบกำหนด, วันที่ขอขยายเวลา, พาธรูป
    """
    db = SessionLocal()
    try:
        # 🔹 Join ตารางที่เกี่ยวข้องทั้งหมด
        latest = (
            db.query(
                Renewal.renewal_id,
                User.name.label("borrower_name"),
                Equipment.name.label("equipment_name"),
                RentReturn.start_date,
                RentReturn.due_date.label("old_due"),
                Renewal.new_due.label("new_due"),
                Renewal.status,
                Renewal.note,
                Equipment.equipment_id
            )
            .join(RentReturn, Renewal.rent_id == RentReturn.rent_id)
            .join(User, RentReturn.user_id == User.user_id)
            .join(Equipment, RentReturn.equipment_id == Equipment.equipment_id)
            .filter(Renewal.rent_id == rent_id)
            .order_by(Renewal.renewal_id.desc())
            .first()
        )

        if not latest:
            print(f"⚠️ ไม่พบคำขอขยายเวลาสำหรับ rent_id={rent_id}")
            return None

        # 🔹 ดึง path รูปทั้งหมดของอุปกรณ์
        image_paths = (
            db.query(EquipmentImage.image_path)
            .filter(EquipmentImage.equipment_id == latest.equipment_id)
            .all()
        )
        images = [img.image_path for img in image_paths]

        # ✅ รวมข้อมูลเป็น dict
        result = {
            "renewal_id": latest.renewal_id,
            "borrower_name": latest.borrower_name,
            "equipment_name": latest.equipment_name,
            "images": images,
            "start_date": latest.start_date.strftime("%Y-%m-%d %H:%M"),
            "old_due": latest.old_due.strftime("%Y-%m-%d %H:%M"),
            "new_due": latest.new_due.strftime("%Y-%m-%d %H:%M"),
            "status": latest.status,
            "note": latest.note,
        }

        print(f"📦 ดึงข้อมูลคำขอขยายเวลา rent_id={rent_id} สำเร็จ")
        return result

    except Exception as e:
        print("❌ Database Error:", e)
        raise
    finally:
        db.close()
