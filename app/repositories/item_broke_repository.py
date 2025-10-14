from app.db.db import SessionLocal, engine
from sqlalchemy import text
from app.db.models import ItemBroke, RentReturn, Equipment, User, ItemBrokeImage
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only
import os
import time
from werkzeug.utils import secure_filename
from flask import current_app


class ItemBrokeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def list_all(self):
        # Some deployments may have an older SQLite schema that doesn't include
        # the `equipment_name` column. Check at runtime and avoid selecting that
        # column if it's missing to prevent OperationalError until the DB is
        # migrated.
        try:
            has_equipment_name = False
            with engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info('item_brokes')"))
                cols = [row[1] for row in res.fetchall()]
                has_equipment_name = 'equipment_name' in cols

            if has_equipment_name:
                results = (
                    self.db.query(ItemBroke)
                    .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment))
                    .order_by(ItemBroke.created_at.desc())
                    .all()
                )
            else:
                # Load only the safe columns (do not reference equipment_name)
                results = (
                    self.db.query(ItemBroke)
                    .options(
                        load_only('item_broke_id', 'rent_id', 'type', 'detail', 'status', 'created_at'),
                        joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment),
                    )
                    .order_by(ItemBroke.created_at.desc())
                    .all()
                )

            items = []
            for it in results:
                rr = getattr(it, 'rent_return', None)
                equip = getattr(rr, 'equipment', None) if rr else None
                items.append({
                    'item_broke_id': it.item_broke_id,
                    'rent_id': it.rent_id,
                    'type': it.type,
                    'detail': it.detail,
                    'status': it.status,
                    'created_at': it.created_at,
                    # if equipment_name column is missing, it will be None here
                    'equipment_name': getattr(it, 'equipment_name', None) or getattr(equip, 'name', None),
                    'equipment_code': getattr(equip, 'code', None),
                })

            return items
        except Exception:
            # In case of any unexpected DB errors, raise so higher layers can
            # handle/display the traceback (useful during local debugging).
            raise

    def get(self, item_broke_id: int):
        return (
            self.db.query(ItemBroke)
            .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment))
            .filter(ItemBroke.item_broke_id == item_broke_id)
            .first()
        )

    def update_status(self, item_broke_id: int, new_status: str):
        it = self.db.query(ItemBroke).filter(ItemBroke.item_broke_id == item_broke_id).first()
        if not it:
            return False
        it.status = new_status
        self.db.add(it)
        self.db.commit()
        return True

    def create(self, rent_id: int | None, type: str, detail: str, images: list = None, equipment_name: str = None):
        """Create an ItemBroke entry and save any uploaded images.

        images should be a list of FileStorage objects (from Flask request.files.getlist)
        """
        images = images or []
        # create record
        try:
            # if equipment_name missing, try to infer from rent_return -> equipment
            if not equipment_name and rent_id:
                try:
                    rr = self.db.query(RentReturn).filter(RentReturn.rent_id == rent_id).first()
                    if rr and getattr(rr, 'equipment', None):
                        equipment_name = getattr(rr.equipment, 'name', None)
                except Exception:
                    equipment_name = equipment_name

            it = ItemBroke(rent_id=rent_id or 0, type=type or 'lost', detail=detail or '', status='pending', equipment_name=equipment_name)
            self.db.add(it)
            self.db.commit()
            self.db.refresh(it)

            # handle images
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            for f in images:
                if not f or f.filename == '':
                    continue
                fname = secure_filename(f.filename)
                uniq = f"itembroke_{it.item_broke_id}_{int(time.time())}_{fname}"
                dest_path = os.path.join(upload_dir, uniq)
                f.save(dest_path)

                # store relative path under static/ so templates can use url_for('static', filename=path)
                rel_path = os.path.join('uploads', uniq).replace('\\', '/')
                img = ItemBrokeImage(item_broke_id=it.item_broke_id, image_path=rel_path)
                self.db.add(img)

            self.db.commit()
            return it.item_broke_id
        except Exception:
            self.db.rollback()
            raise

    def close(self):
        self.db.close()
