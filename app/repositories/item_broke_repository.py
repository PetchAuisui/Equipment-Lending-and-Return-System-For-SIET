from app.db.db import SessionLocal
from app.db.models import ItemBroke, RentReturn, Equipment, User
from sqlalchemy.orm import joinedload


class ItemBrokeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def list_all(self):
        results = (
            self.db.query(ItemBroke)
            .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment))
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
                'equipment_name': getattr(equip, 'name', None),
                'equipment_code': getattr(equip, 'code', None),
            })

        return items

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

    def close(self):
        self.db.close()
