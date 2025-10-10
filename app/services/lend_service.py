from app.repositories import lend_repository

def get_all_subjects():
    return lend_repository.get_all_subjects()


def get_all_users():
    """
    ดึงข้อมูลผู้ใช้ทั้งหมดจาก repository 
    และกรองเฉพาะอาจารย์ให้เป็น list
    """
    users = lend_repository.get_all_users()

    # ✅ สร้าง list ของชื่ออาจารย์
    teacher_names = [
        u["name"] for u in users
        if u["member_type"] in ["อาจารย์", "teacher"]
    ]

    # ✅ ส่งข้อมูลกลับ (ทั้ง users ทั้งรายชื่ออาจารย์)
    return {
        "teachers": teacher_names
    }
