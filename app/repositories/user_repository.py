from typing import Optional, Dict, List
from .base_repository import BaseJsonRepository

class UserRepository(BaseJsonRepository):
    def all(self) -> List[Dict]:
        return self._load()

    def find_by_student_id(self, student_id: str) -> Optional[Dict]:
        return next((u for u in self._load() if u["student_id"] == student_id), None)

    def find_by_email(self, email: str) -> Optional[Dict]:
        return next((u for u in self._load() if u["email"].lower() == email.lower()), None)

    def upsert(self, row: Dict):
        rows = self._load()
        for i, r in enumerate(rows):
            if r["student_id"] == row["student_id"]:
                rows[i] = row
                self._save(rows)
                return
        rows.append(row)
        self._save(rows)
