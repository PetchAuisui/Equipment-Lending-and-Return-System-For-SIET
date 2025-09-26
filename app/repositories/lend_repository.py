# app/repository/lend_repository.py
# 📌 repository ทำหน้าที่ "เชื่อมต่อกับ data source"
# ในที่นี้ยังไม่ใช้ database → เลย mock data ไว้ก่อน

from app.models.lend import Lend

def get_all_equipment_mock():
    # 📌 คืนค่าเป็น list ของ Lend object
    equipments = [
        Lend("images/hdmi.jpg", "สาย HDMI", 3),
        Lend("images/mouse.jpg", "เมาส์", 5),
        Lend("images/keyboard.jpg", "คีย์บอร์ด", 2),
        Lend("images/keyboard.jpg", "คีย์บอร์ด", 2)
    ]
    return equipments
