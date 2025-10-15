from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.db.db import SessionLocal, engine
from app.db.models import ItemBroke, RentReturn
from sqlalchemy.orm import joinedload, load_only
import os, time
from werkzeug.utils import secure_filename
from flask import current_app

class ItemBrokeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def list_all(self):
        """List all broken/lost item reports, compatible with both SQLite and PostgreSQL."""
        try:
            insp = inspect(engine)
            has_equipment_name = False

            # ตรวจว่าคอลัมน์ 'equipment_name' มีอยู่จริงไหม
            if insp.has_table("item_brokes"):
                cols = [col["name"] for col in insp.get_columns("item_brokes")]
                has_equipment_name = "equipment_name" in cols

            if has_equipment_name:
                results = (
                    self.db.query(ItemBroke)
                    .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment))
                    .order_by(ItemBroke.created_at.desc())
                    .all()
                )
            else:
                results = (
                    self.db.query(ItemBroke)
                    .options(
                        load_only(
                            "item_broke_id",
                            "rent_id",
                            "type",
                            "detail",
                            "status",
                            "created_at",
                        ),
                        joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment),
                    )
                    .order_by(ItemBroke.created_at.desc())
                    .all()
                )

            items = []
            for it in results:
                rr = getattr(it, "rent_return", None)
                equip = getattr(rr, "equipment", None) if rr else None
                items.append({
                    "item_broke_id": it.item_broke_id,
                    "rent_id": it.rent_id,
                    "type": it.type,
                    "detail": it.detail,
                    "status": it.status,
                    "created_at": it.created_at,
                    "equipment_name": getattr(it, "equipment_name", None) or getattr(equip, "name", None),
                    "equipment_code": getattr(equip, "code", None),
                })

            return items

        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
