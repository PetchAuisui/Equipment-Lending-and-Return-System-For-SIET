# =============================================
# app/services/borrow_history_service.py
# =============================================
from __future__ import annotations
from typing import List, Dict

from app.repositories.history_repository import RentHistoryRepository


class BorrowHistoryService:
    """
    ชั้นบริการ (Service Layer) สำหรับประวัติการยืม-คืนของผู้ใช้
    ใช้เรียกข้อมูลจาก RentHistoryRepository
    """

    def __init__(self, repo: RentHistoryRepository):
        self.repo = repo

    def get_for_user(self, user_id: int, returned_only: bool = True) -> List[Dict]:
        """
        ดึงประวัติการยืมของผู้ใช้ตาม user_id
        ถ้า returned_only=True → แสดงเฉพาะที่คืนแล้ว (return_date != NULL)
        """
        return self.repo.list_by_user(user_id, returned_only=returned_only)
