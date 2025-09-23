# app/services/schemas.py

from dataclasses import dataclass
from typing import Optional, Dict


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