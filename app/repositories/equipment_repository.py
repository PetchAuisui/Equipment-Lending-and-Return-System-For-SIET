from typing import List, Optional
from .base_repo import BaseRepository
from ..database.models import Equipment




class EquipmentRepository(BaseRepository[Equipment]):
    def __init__(self):
        super().__init__(Equipment)


    def search(self, q: str = '', category: Optional[str] = None) -> List[Equipment]:
        query = self.model.query # via Flask-SQLAlchemy query property
        if q:
            like = f"%{q}%"
            query = query.filter((self.model.name.ilike(like)) | (self.model.code.ilike(like)))
        if category:
            query = query.filter(self.model.category == category)
        return query.order_by(self.model.name.asc()).all()