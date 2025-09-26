# app/service/lend_service.py
from app.repository import lend_repository, inventory_repository

def lend_equipment(user_id, equipment_id, quantity):
    # 1. เช็ก stock
    equipment = inventory_repository.get_equipment_by_id(equipment_id)
    if equipment['amount'] < quantity:
        raise ValueError("จำนวนไม่พอ")

    # 2. บันทึกการยืม
    lend_repository.create_lend_record(user_id, equipment_id, quantity)

    # 3. อัพเดต stock
    inventory_repository.update_equipment_amount(equipment_id, equipment['amount'] - quantity)

    return {"status": "success", "message": "ยืมสำเร็จ"}
