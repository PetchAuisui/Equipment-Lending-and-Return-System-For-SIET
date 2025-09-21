# app/models/user.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class User:
    # ids (อย่างใดอย่างหนึ่งจะมีค่า)
    student_id: Optional[str] = None
    employee_id: Optional[str] = None

    # profile
    name: str = ""
    major: str = ""
    member_type: str = ""   # student | teacher | officer | staff
    phone: str = ""
    email: str = ""
    gender: str = ""

    # auth
    password_hash: str = ""
    role: str = "member"

    # ---- helpers ----
    def to_dict(self) -> Dict[str, Any]:
        """ใช้ส่งให้ repository/ORM; เก็บทุกฟิลด์ (รวม employee_id)"""
        return asdict(self)

    def public_dict(self) -> Dict[str, Any]:
        """ใช้ส่งกลับฝั่ง UI/API (ซ่อน password_hash)"""
        return {
            "student_id": self.student_id,
            "employee_id": self.employee_id,
            "name": self.name,
            "major": self.major,
            "member_type": self.member_type,
            "phone": self.phone,
            "email": self.email,
            "gender": self.gender,
            "role": self.role,
        }
