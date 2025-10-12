from datetime import datetime
from app.repositories import renewal_repository

def create_renewal(data):
    """
    ✅ ตรวจสอบและส่งต่อข้อมูลไป repository
    """
    try:
        rent_id = int(data["rent_id"])
        old_due = datetime.strptime(data["old_due"], "%Y-%m-%d")
        new_due = datetime.strptime(data["new_due"], "%Y-%m-%d")
        reason = data.get("reason")
        created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")

        # 🔹 ตรวจสอบ logic: new_due ต้องมากกว่า old_due
        if new_due <= old_due:
            return False, "วันขยายเวลาต้องมากกว่าวันคืนเดิม"

        # 🔹 ตรวจสอบว่าเคยมีคำขอ pending อยู่แล้วหรือไม่
        if renewal_repository.is_pending_request_exists(rent_id):
            return False, "มีคำขอขยายเวลาที่ยังรอดำเนินการอยู่แล้ว"

        # 🔹 ส่งต่อให้ repository
        renewal_repository.insert_renewal({
            "rent_id": rent_id,
            "old_due": old_due,
            "new_due": new_due,
            "note": reason,
            "created_at": created_at,
        })

        return True, "บันทึกคำขอสำเร็จ"

    except Exception as e:
        print("❌ Error:", e)
        return False, str(e)
