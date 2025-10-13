# =============================================
# app/services/history_service.py
# =============================================
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.history_repository import RentHistoryRepository

OrderLiteral = Literal["asc", "desc"]
DateField = Literal["start_date", "return_date"]

@dataclass
class HistoryFilter:
    start_date: Optional[datetime] = None
    end_date:   Optional[datetime] = None
    returned_only: bool = True          # ✅ ให้ค่าเริ่มต้นเป็น True แบบโค้ดเดิม
    order: OrderLiteral = "desc"
    date_field: DateField = "start_date"


class BorrowHistoryService:
    """
    จัดการข้อมูลประวัติการยืม-คืนทั้งหมด (คงอินเตอร์เฟซปัจจุบัน)
    """

    def __init__(self, repo: "RentHistoryRepository"):
        self.repo = repo

    def get_all(self, f: HistoryFilter) -> List[Dict]:
        return self.repo.fetch_all(f)

    def get_for_user(self, user_id: int, returned_only: bool = True) -> List[Dict]:
        """
        ดึงเฉพาะประวัติของผู้ใช้คนหนึ่ง
        returned_only=True → พฤติกรรมเหมือนโค้ดที่รูปขึ้น
        """
        f = HistoryFilter(returned_only=returned_only)
        return self.repo.fetch_for_user(user_id, f)
