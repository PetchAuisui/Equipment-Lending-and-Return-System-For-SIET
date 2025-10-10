from app.repositories import lend_repository

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


def print_lend_data(data_list):
    """
    ✅ รับข้อมูลจากฟอร์มยืม แล้ว print แสดงใน console
    """
    print("📦 ข้อมูลการยืมที่ได้รับ:")
    print(data_list)
