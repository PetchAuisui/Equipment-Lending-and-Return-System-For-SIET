from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, List, Dict, TYPE_CHECKING

# ✅ ป้องกัน circular import
if TYPE_CHECKING:
    from app.repositories.history_repository import RentHistoryRepository


# ---- type alias ----
OrderLiteral = Literal["asc", "desc"]
DateField = Literal["start_date", "return_date"]


# ---- filter object สำหรับกรองข้อมูลใน repo ----
@dataclass
class HistoryFilter:
    start_date: Optional[datetime] = None
    end_date:   Optional[datetime] = None
    returned_only: bool = False
    order: OrderLiteral = "desc"
    date_field: DateField = "start_date"


# ---- service layer ----
class BorrowHistoryService:
    """
    จัดการข้อมูลประวัติการยืม-คืนทั้งหมด
    ใช้ร่วมกับ RentHistoryRepository ที่ทำงานกับตาราง rent_returns
    """

    def __init__(self, repo: "RentHistoryRepository"):
        self.repo = repo

    def get_all(self, f: HistoryFilter) -> List[Dict]:
        """
        ดึงประวัติทั้งหมด (ทุก user)
        รองรับการกรอง/เรียงลำดับตาม HistoryFilter
        """
        return self.repo.fetch_all(f)

    def get_for_user(self, user_id: int, returned_only: bool = False) -> List[Dict]:
        """
        ดึงเฉพาะประวัติของผู้ใช้คนหนึ่ง
        ถ้า returned_only=True จะกรองเฉพาะที่คืนแล้ว
        """
        f = HistoryFilter(returned_only=returned_only)
        return self.repo.fetch_for_user(user_id, f)
