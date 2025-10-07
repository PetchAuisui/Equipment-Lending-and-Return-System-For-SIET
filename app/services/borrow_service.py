from dataclasses import dataclass
from datetime import datetime
from .. import db
from ..database.models import Rent, Equipment, EquipmentAsset, StatusRent




@dataclass
class BorrowService:
    repo: object # BorrowRepository


    def _get_or_create_status(self, name: str) -> StatusRent:
        status = StatusRent.query.filter_by(name=name).first()
        if not status:
            status = StatusRent(name=name, color_code='#888888')
            db.session.add(status)
            db.session.commit()
        return status


    def request_borrow(self, student_id: int, equipment_id: int, qty: int, start_date: datetime, due_date: datetime, reason: str = '') -> list[Rent]:
        # Allocate assets if available; create one Rent per asset
        pending = self._get_or_create_status('PENDING')
        assets_q = EquipmentAsset.query.filter_by(equipment_id=equipment_id, status='available', is_active=True)
        assets = assets_q.limit(max(1, qty)).all()
        if len(assets) < max(1, qty):
            raise ValueError('Equipment not available')
        rents: list[Rent] = []
        for asset in assets:
            r = Rent(
                equipment_id=equipment_id,
                asset_id=asset.asset_id,
                user_id=student_id,
                start_date=start_date,
                due_date=due_date,
                reason=reason,
                status_id=pending.status_id,
            )
            db.session.add(r)
            rents.append(r)
        db.session.commit()
        return rents


    def approve(self, rent_id: int) -> Rent:
        r = self.repo.get(rent_id)
        if not r:
             raise ValueError('Request not found')
        approved = self._get_or_create_status('APPROVED')
        r.status_id = approved.status_id
    # mark asset as rented
        if r.asset:
            r.asset.status = 'rented'
        db.session.commit()
        return r
    
    def reject(self, rent_id: int) -> Rent:
        r = self.repo.get(rent_id)
        if not r:
            raise ValueError('Request not found')
        rejected = self._get_or_create_status('REJECTED')
        r.status_id = rejected.status_id
        db.session.commit()
        return r


    def mark_returned(self, rent_id: int) -> Rent:
        r = self.repo.get(rent_id)
        if not r:
            raise ValueError('Request not found')
        returned = self._get_or_create_status('RETURNED')
        r.status_id = returned.status_id
        if r.asset:
            r.asset.status = 'available'
        db.session.commit()
        return r