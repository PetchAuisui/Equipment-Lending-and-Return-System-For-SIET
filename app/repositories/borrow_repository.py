from typing import List
from sqlalchemy.orm import joinedload
from .base_repo import BaseRepository
from ..database.models import Rent, StatusRent




class BorrowRepository(BaseRepository[Rent]):
    def __init__(self):
        super().__init__(Rent)


    def for_student(self, student_id: int) -> List[Rent]:
        return (
            self.model.query
        .options(joinedload(Rent.equipment), joinedload(Rent.status))
        .filter(Rent.user_id == student_id)
        .order_by(Rent.created_at.desc())
        .all()
    )


    def pending(self) -> List[Rent]:
        # Ensure a status named 'PENDING' exists; otherwise return empty
        return (
            self.model.query
            .join(StatusRent, Rent.status_id == StatusRent.status_id)
            .options(joinedload(Rent.user), joinedload(Rent.equipment), joinedload(Rent.status))
            .filter(StatusRent.name == 'PENDING')
            .order_by(Rent.created_at.asc())
            .all()
        )