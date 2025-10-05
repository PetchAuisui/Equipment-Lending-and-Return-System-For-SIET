from collections import defaultdict
from app.db.db import SessionLocal
from app.db.models import Equipment
from app.models.lend_device import device

def get_equipment_list():
    db = SessionLocal()
    try:
        all_eq = db.query(Equipment).all()
        # สร้าง dict เพื่อรวมชื่อและนับจำนวน
        equipment_count = defaultdict(int)
        for eq in all_eq:
            equipment_count[eq.name] += 1

        equipments = []
        for name, qty in equipment_count.items():
            # แปลงเป็น object device ของ UI
            equipments.append(
                device(
                    image_path=f"images/{name.replace(' ', '_')}.jpg",
                    name=name,
                    quantity=qty
                )
            )
        return equipments
    finally:
        db.close()
