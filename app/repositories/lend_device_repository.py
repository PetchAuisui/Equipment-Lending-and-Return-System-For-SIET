from app.db.db import SessionLocal
from app.models.equipment import Equipment
from app.db.models import EquipmentImage

def get_all_equipments_with_images():
    db = SessionLocal()
    try:
        # ดึงอุปกรณ์ทั้งหมด
        equipments = db.query(Equipment).all()

        # ดึงรูปทั้งหมด
        images = db.query(EquipmentImage).all()
        image_dict = {img.equipment_id: img.image_path for img in images}

        equipment_list = []
        for e in equipments:
            equipment_list.append({
                "equipment_id": e.equipment_id,
                "name": e.name,
                "code": e.code,
                "category": e.category,
                "detail": e.detail,
                "brand": e.brand,
                "buy_date": e.buy_date,
                "status": e.status,
                "image_path": image_dict.get(e.equipment_id, None)
            })
        return equipment_list
    finally:
        db.close()
