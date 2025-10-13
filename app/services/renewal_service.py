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

        # 🔹 ตรวจสอบว่า new_due ต้องมากกว่า old_due
        if new_due <= old_due:
            return False, "วันขยายเวลาต้องมากกว่าวันคืนเดิม"

        # 🔹 ตรวจสอบว่ามีคำขอ pending อยู่หรือไม่
        if renewal_repository.is_pending_request_exists(rent_id):
            return False, "มีคำขอขยายเวลาที่ยังรอดำเนินการอยู่แล้ว"

        # 🔹 ส่งต่อข้อมูลไป repository เพื่อบันทึก
        renewal_repository.insert_renewal({
            "rent_id": rent_id,
            "old_due": old_due,
            "new_due": new_due,
            "note": reason,
            "created_at": created_at,
        })

        return True, "✅ บันทึกคำขอขยายเวลาเรียบร้อยแล้ว"
    except Exception as e:
        print("❌ Error:", e)
        return False, str(e)



# ------------------------------------------------------------------
# ✅ ของใหม่: ดึงข้อมูล renew ทั้งหมด (ใช้ repository เดิม)
# ------------------------------------------------------------------
def get_renewal_summary_service():
    """
    ✅ ดึงข้อมูลสรุปคำขอขยายเวลาทั้งหมด
    โดยใช้ repository เดิม (get_all_rent_returns_with_renewal)
    และคืนข้อมูลเฉพาะที่ต้องการ เช่น ชื่ออุปกรณ์, ชื่อผู้ยืม, วันที่ยืม, วันที่คืนเก่า, วันที่คืนใหม่
    """
    try:
        rent_data = renewal_repository.get_all_rent_returns_with_renewal()

        summary = []
        for rent in rent_data:
            # มี renewals ไหม?
            if rent.get("renewals"):
                for rn in rent["renewals"]:
                    summary.append({
                        "equipment_name": rent["equipment"]["name"],
                        "borrower_name": rent["user"]["name"],
                        "start_date": rent["start_date"].strftime("%Y-%m-%d %H:%M") if rent["start_date"] else None,
                        "old_due": rn["old_due"].strftime("%Y-%m-%d %H:%M") if rn["old_due"] else None,
                        "new_due": rn["new_due"].strftime("%Y-%m-%d %H:%M") if rn["new_due"] else None,
                    })

        print(f"📦 ดึงข้อมูลสรุป Renewal ทั้งหมด {len(summary)} รายการ")
        return True, summary

    except Exception as e:
        print("❌ Error:", e)
        return False, str(e)
