from dataclasses import dataclass
from typing import Dict
from datetime import datetime

@dataclass
class LoginDTO:
    email: str
    password: str

    @classmethod
    def from_raw(cls, raw: Dict) -> "LoginDTO":
        """
        รับ raw dict (จาก request.form หรือ request.json)
        แล้วแปลงเป็น DTO ที่มี email และ password
        """
        return cls(
            email=(raw.get("email") or "").strip().lower(),
            password=(raw.get("password") or "").strip(),
        )
    
@dataclass
class OutstandingDTO:
    rent_id: int
    equipment_name: str
    equipment_code: str
    borrower_name: str
    start_date: datetime
    due_date: datetime
    is_overdue: bool
    overdue_days: int

@dataclass
class TopBorrowedDTO:
    equipment_id: int
    name: str
    code: str
    borrow_count: int
    image_path: str | None = None   # 👈 เพิ่มตรงนี้
