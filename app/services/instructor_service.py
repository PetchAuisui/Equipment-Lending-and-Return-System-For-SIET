# app/services/instructor_service.py

from dataclasses import dataclass
from sqlalchemy import select, func

# ใช้ตัวนี้ที่อยู่ใน app/services/image_resolver.py
from app.services.image_resolver import ImageResolver


@dataclass
class RequestCard:
    rent_id: int
    borrower: str
    equipment_name: str
    status_name: str
    reason: str
    image_url: str


class StatusService:
    def __init__(self, session):
        self.s = session

    def get_or_create(self, name: str):
        norm = (name or "").upper()
        from app.db.models import StatusRent
        st = self.s.execute(
            select(StatusRent).where(func.upper(StatusRent.name) == norm)
        ).scalar_one_or_none()
        if not st:
            st = StatusRent(name=norm, color_code="#888888")
            self.s.add(st)
            self.s.commit()
        return st


class InstructorService:
    """ธุรกิจฝั่งอาจารย์: เห็นคำขอของตัวเอง / อนุมัติ-ปฏิเสธ"""

    def __init__(self, repo, session):
        self.repo = repo
        self.s = session

    def list_requests(self, statuses, require_confirm, uid, email):
        rows = self.repo.query_requests(statuses, require_confirm, uid, email)
        # ใส่ image_url ให้ทุกชิ้น
        for r in rows:
            if r.equipment:
                r.equipment.image_url = ImageResolver.equip_image_url(r.equipment)
        return rows

    def decide(self, rent_id: int, next_status: str):
        from app.db.models import RentReturn
        st = StatusService(self.s).get_or_create(next_status)
        r = self.s.get(RentReturn, rent_id)
        if not r:
            return None
        r.status_id = st.status_id
        return r