# app/repositories/rent_request_repository.py
from sqlalchemy import select, func, or_, false
from sqlalchemy.orm import joinedload, aliased

from app.db.models import RentReturn, StatusRent, Equipment, User

class RentRequestRepository:
    """รวม query ที่เกี่ยวกับคำขอ (RentReturn)"""

    def __init__(self, session):
        self.s = session

    def _only_my_requests(self, stmt, uid=None, email=None):
        """กรองให้เหลือเฉพาะคำขอที่ส่งถึงอาจารย์คนนี้ (teacher_confirmed -> users.user_id)"""
        if not uid and not email:
            return stmt.where(false())

        Teacher = aliased(User)
        stmt = stmt.join(Teacher, RentReturn.teacher_confirmed == Teacher.user_id)

        conditions = []
        if uid:
            try:
                conditions.append(Teacher.user_id == int(uid))
            except Exception:
                pass
        if email:
            conditions.append(Teacher.email == str(email))

        return stmt.where(or_(*conditions)) if conditions else stmt.where(false())

    def query_requests(self, statuses=None, require_confirm=None, uid=None, email=None):
        """ดึงรายการคำขอตามเงื่อนไข"""
        stmt = (
            select(RentReturn)
            .options(
                joinedload(RentReturn.equipment),
                joinedload(RentReturn.user),
                joinedload(RentReturn.status),
            )
            .order_by(RentReturn.created_at.desc())
        )

        if statuses:
            norm = [str(x).lower() for x in statuses]
            stmt = stmt.join(StatusRent).where(func.lower(StatusRent.name).in_(norm))

        stmt = self._only_my_requests(stmt, uid, email)

        if require_confirm is True and hasattr(Equipment, "confirm"):
            stmt = stmt.join(Equipment).where(Equipment.confirm == 1)

        return self.s.execute(stmt).unique().scalars().all()