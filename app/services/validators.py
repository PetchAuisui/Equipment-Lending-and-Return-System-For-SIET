# app/services/validators.py
from __future__ import annotations

import re
from typing import Optional

__all__ = [
    "norm",
    "validate_email",
    "validate_phone",
    "validate_student_id",
    "validate_employee_id",
]

# ---------------- Small helper ----------------
def norm(s: Optional[str]) -> str:
    """Trim ช่องว่างซ้ายขวา; หากเป็น None จะคืน ''"""
    return (s or "").strip()

# ---------------- Regex rules ----------------
EMAIL_RE   = re.compile(r"^[A-Za-z0-9._%+\-]+@kmitl\.ac\.th$", re.IGNORECASE)
PHONE_RE   = re.compile(r"^0\d{8,9}$")        # 9–10 หลักขึ้นต้นด้วย 0
STUDENT_RE = re.compile(r"^\d{7,10}$")        # ปรับตามรูปแบบจริงของรหัส นศ.
EMP_RE     = re.compile(r"^[A-Za-z0-9\-]{3,20}$")  # ยืดหยุ่นสำหรับบุคลากร

# ---------------- Validators ----------------
def validate_email(email: str) -> bool:
    """ต้องเป็นอีเมล @kmitl.ac.th เท่านั้น"""
    return bool(EMAIL_RE.match(norm(email).lower()))

def validate_phone(phone: str) -> bool:
    """เบอร์โทรไทยพื้นฐาน: 0 ตามด้วยเลขอีก 8–9 ตัว"""
    return bool(PHONE_RE.match(norm(phone)))

def validate_student_id(student_id: str) -> bool:
    """ตรวจฟอร์แมตรหัสนักศึกษา (ตัวเลข 7–10 หลัก)"""
    return bool(STUDENT_RE.match(norm(student_id)))

def validate_employee_id(employee_id: str) -> bool:
    """ตรวจฟอร์แมตรหัสบุคลากร (อักษร/ตัวเลข/ขีด 3–20 ตัว)"""
    return bool(EMP_RE.match(norm(employee_id)))