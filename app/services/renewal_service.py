from datetime import datetime
from app.repositories import renewal_repository


# ✅ ฟังก์ชันสร้างคำขอขยายเวลา
def create_renewal(data):
    try:
        rent_id = int(data["rent_id"])
        old_due = datetime.strptime(data["old_due"], "%Y-%m-%d")
        new_due = datetime.strptime(data["new_due"], "%Y-%m-%d")
        reason = data.get("reason")
        created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")

        if new_due <= old_due:
            return False, "วันขยายเวลาต้องมากกว่าวันคืนเดิม"

        if renewal_repository.is_pending_request_exists(rent_id):
            return False, "มีคำขอขยายเวลาที่ยังรอดำเนินการอยู่แล้ว"

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


# ✅ ดึงข้อมูลทั้งหมด (แยก pending / history)
def get_renewal_summary_service():
    """
    ✅ ดึงข้อมูลคำขอทั้งหมด
    - renewals: เฉพาะ status = pending
    - history_renewals: เฉพาะ status = approved หรือ cancle
    """
    try:
        rent_data = renewal_repository.get_all_rent_returns_with_renewal()
        renewals = []          # ✅ pending เท่านั้น
        history_renewals = []  # 🕓 approved + cancle

        for rent in rent_data:
            if rent.get("renewals"):
                for rn in rent["renewals"]:
                    item = {
                        "renewal_id": rn["renewal_id"],
                        "status": rn["status"],  # ✅ เพิ่มสถานะมาด้วย
                        "equipment_name": rent["equipment"]["name"],
                        "borrower_name": rent["user"]["name"],
                        "start_date": rent["start_date"].strftime("%Y-%m-%d") if rent["start_date"] else None,
                        "old_due": rn["old_due"].strftime("%Y-%m-%d") if rn["old_due"] else None,
                        "new_due": rn["new_due"].strftime("%Y-%m-%d") if rn["new_due"] else None,
                    }

                    # ✅ แยกตามสถานะ
                    if rn["status"] == "pending":
                        renewals.append(item)
                    elif rn["status"] in ["approved", "cancle"]:
                        history_renewals.append(item)

        print(f"📦 pending = {len(renewals)} รายการ | history = {len(history_renewals)} รายการ")
        return True, {
            "renewals": renewals,
            "history_renewals": history_renewals
        }

    except Exception as e:
        print("❌ Error:", e)
        return False, str(e)


# ✅ อนุมัติคำขอ
def approve_renewal_service(renewal_id, user_id):
    try:
        renewal_repository.update_renewal_status(
            renewal_id=renewal_id,
            new_status="approved",
            rent_status_id=6,
            update_due_date=True,
            approved_by=user_id  # ✅ บันทึกผู้อนุมัติ
        )
        print(f"✅ อนุมัติ renewal_id={renewal_id} โดย user_id={user_id}")
        return True, "อนุมัติคำขอขยายเวลาเรียบร้อยแล้ว"
    except Exception as e:
        print("❌ Error ใน approve_renewal_service:", e)
        return False, str(e)


# ❌ ไม่อนุมัติคำขอ
def reject_renewal_service(renewal_id, user_id):
    try:
        renewal_repository.update_renewal_status(
            renewal_id=renewal_id,
            new_status="cancle",
            rent_status_id=7,
            update_due_date=False,
            approved_by=user_id  # ✅ บันทึกผู้อนุมัติ
        )
        print(f"❌ ไม่อนุมัติ renewal_id={renewal_id} โดย user_id={user_id}")
        return True, "ไม่อนุมัติคำขอเรียบร้อยแล้ว"
    except Exception as e:
        print("❌ Error ใน reject_renewal_service:", e)
        return False, str(e)
