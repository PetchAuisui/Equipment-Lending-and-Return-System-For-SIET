from sqlalchemy.orm import joinedload
from sqlalchemy.sql import exists, and_
from app.db.db import SessionLocal
from app.db.models import Equipment, StockMovement

class LendDeviceRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_equipments_with_images(self):
        results = (
            self.db.query(Equipment)
            .options(joinedload(Equipment.equipment_images))  # หรือ .images
            .filter(
                ~exists().where(
                    and_(
                        StockMovement.equipment_id == Equipment.equipment_id,
                        StockMovement.history.ilike("%[DELETED]%")
                    )
                )
            )
            .all()
        )

        data = []
        for e in results:
            data.append({
                "equipment_id": e.equipment_id,
                "name": e.name,
                "category": e.category,
                "status": e.status,
                "image_path": (
                    e.equipment_images[0].image_path if getattr(e, "equipment_images", []) else "images/placeholder.png"
                ),
            })
        return data

    def close(self):
        self.db.close()
