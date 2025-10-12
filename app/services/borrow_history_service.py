# app/services/borrow_history_service.py
from __future__ import annotations
from typing import List, Dict

from app.repositories.rent_history_repository import RentHistoryRepository


class BorrowHistoryService:
    def __init__(self, repo: RentHistoryRepository):
        self.repo = repo

    def get_for_user(self, user_id: int) -> List[Dict]:
        return self.repo.list_by_user(user_id)
