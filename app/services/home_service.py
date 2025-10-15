from typing import List, Optional
from app.repositories.home_repository import HomeRepository
from app.services.schemas import TopBorrowedDTO, OutstandingDTO
from app.services.item_broke_service import ItemBrokeService
from app.services.schemas import RecentLostDTO
from datetime import datetime

class HomeService:
    """Business logic ของหน้า Home"""

    def __init__(self, repo: Optional[HomeRepository] = None):
        self.repo = repo or HomeRepository()


    def get_top_borrowed_items(self, limit: int = 8) -> List[TopBorrowedDTO]:
        rows = self.repo.get_top_borrowed(limit=limit)
        return [
            TopBorrowedDTO(
                equipment_id=r.equipment_id,
                name=r.name,
                code=r.code,
                borrow_count=r.borrow_count,
                image_path=r.image_path or "images/default_equip.png"  # 👈 รูป fallback
            )
            for r in rows
        ]


    def get_outstanding_items_for_user(self, user_id: int, limit: int = 10) -> List[OutstandingDTO]:
        rows = self.repo.get_outstanding_by_user(user_id=user_id, limit=limit)
        return [
            OutstandingDTO(
                rent_id=r["rent_id"],
                equipment_name=r["equipment_name"],
                equipment_code=r["equipment_code"],
                borrower_name=r["borrower_name"],
                start_date=r["start_date"],
                due_date=r["due_date"],
                is_overdue=r["is_overdue"],
                overdue_days=r["overdue_days"],
            )
            for r in rows
        ]

    def get_recent_lost_reports(self, limit: int = 4) -> List[RecentLostDTO]:
        ibs = ItemBrokeService()
        rows = ibs.list_reports() or []
        out = []
        for r in rows:
            try:
                if r.get('type') != 'lost':
                    continue
                img = (r.get('images') or [None])[0]
                out.append(RecentLostDTO(
                    item_broke_id=r.get('item_broke_id'),
                    equipment_name=r.get('equipment_name') or r.get('equipment_code') or 'ไม่ระบุ',
                    image_path=(img if img else 'images/default_equip.png'),
                    created_at=r.get('created_at') if isinstance(r.get('created_at'), datetime) else None,
                    contact_phone=r.get('contact_phone')
                ))
                if len(out) >= limit:
                    break
            except Exception:
                continue
        return out
