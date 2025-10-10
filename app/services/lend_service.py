from app.repositories import lend_repository
from datetime import datetime



def get_all_subjects():
    return lend_repository.get_all_subjects()


def get_all_users():
    """
    ดึงข้อมูลผู้ใช้ทั้งหมดจาก repository 
    และกรองเฉพาะอาจารย์ให้ได้ทั้ง user_id และ name
    """
    users = lend_repository.get_all_users()

    # ✅ สร้าง list ของอาจารย์เป็น object (dict)
    teachers = [
        {
            "user_id": u["user_id"],
            "name": u["name"]
        }
        for u in users
        if u["member_type"] in ["อาจารย์", "teacher"]
    ]

    # ✅ ส่งข้อมูลกลับ (ทั้ง users ทั้งรายชื่ออาจารย์)
    return {
        "teachers": teachers
    }


def lend_data(data_list):
    """
    ✅ รับข้อมูลจากฟอร์มยืม แล้วบันทึกลงตาราง rent_returns ผ่าน repository
    """
    print("📦 ข้อมูลการยืมที่ได้รับ:")
    print(data_list)

    # แปลง list ให้เป็น dict (ตามลำดับ key ที่ฟอร์มส่งมา)
    data = {
        "device_name": data_list[0],
        "code": data_list[1],
        "borrow_date": data_list[2],
        "return_date": data_list[3],
        "borrower_name": data_list[4],
        "phone": data_list[5],
        "major": data_list[6],
        "subject_id": data_list[7],
        "teacher_confirmed": data_list[8],
        "reason": data_list[9],
    }

    # ✅ เติมข้อมูลระบบ
    data["start_date"] = datetime.utcnow()
    data["status_id"] = 1  # รอดำเนินการ

    # ✅ ส่งต่อให้ repository จัดการ insert
    lend_repository.insert_rent_record(data)
