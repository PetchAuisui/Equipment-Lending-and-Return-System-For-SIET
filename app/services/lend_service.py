# app/service/lend_service.py
# 📌 service ใช้สำหรับประมวลผล logic

from app.repositories import lend_repository

def get_equipment_list():
    # 📌 ดึงข้อมูลจาก repository (mock data)
    equipments = lend_repository.get_all_equipment_mock()
    return equipments
