from datetime import datetime
from sqlalchemy.orm import joinedload
from app.db.db import SessionLocal
from app.db.models import Renewal, RentReturn, Equipment


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



# ------------------------------------------------------------------
# ✅ ของใหม่: ดึงข้อมูล RentReturn พร้อมข้อมูลการต่ออายุ (Renewal)
# ------------------------------------------------------------------
def get_all_rent_returns_with_renewal():
    """ดึงข้อมูล RentReturn พร้อมข้อมูลการต่ออายุ (Renewal) และผู้อนุมัติ"""
    db = SessionLocal()
    try:
        results = (
            db.query(RentReturn)
            .options(
                joinedload(RentReturn.equipment)
                    .joinedload(Equipment.equipment_images),
                joinedload(RentReturn.status),
                joinedload(RentReturn.user),
                joinedload(RentReturn.subject),
                joinedload(RentReturn.teacher_confirm),
                # ✅ โหลดข้อมูล Renewal (ต่ออายุ)
                joinedload(RentReturn.renewals)
                    .joinedload(Renewal.approver)
            )
            .all()
        )

        data = []
        for r in results:
            renewals_data = []
            if hasattr(r, "renewals") and r.renewals:
                for rn in r.renewals:
                    renewals_data.append({
                        "renewal_id": rn.renewal_id,
                        "old_due": rn.old_due,
                        "new_due": rn.new_due,
                        "status": rn.status,
                        "note": rn.note,
                        "created_at": rn.created_at,
                        "approved_by": {
                            "user_id": getattr(rn.approver, "user_id", None),
                            "name": getattr(rn.approver, "name", None)
                        }
                    })

            image_path = None
            if r.equipment and r.equipment.equipment_images:
                image_path = r.equipment.equipment_images[0].image_path

            data.append({
                "rent_id": r.rent_id,
                "start_date": r.start_date,
                "due_date": r.due_date,
                "reason": r.reason,
                "status": {
                    "name": getattr(r.status, "name", None),
                    "color_code": getattr(r.status, "color_code", None),
                },
                "equipment": {
                    "name": getattr(r.equipment, "name", None),
                    "code": getattr(r.equipment, "code", None),
                    "image_path": image_path,
                },
                "user": {
                    "name": getattr(r.user, "name", None),
                    "phone": getattr(r.user, "phone", None),
                },
                "renewals": renewals_data  # ✅ ต่ออายุทั้งหมด
            })

        return data

    except Exception as e:
        print("❌ Database Error:", e)
        raise
    finally:
        db.close()
