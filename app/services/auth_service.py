# app/services/auth_service.py
from __future__ import annotations

import re
from typing import Dict, Optional
from werkzeug.security import generate_password_hash

from app.repositories.user_repository import UserRepository

EMAIL_RE   = re.compile(r"^[A-Za-z0-9._%+\-]+@kmitl\.ac\.th$", re.IGNORECASE)
PHONE_RE   = re.compile(r"^0\d{8,9}$")              # 9–10 หลักขึ้นต้นด้วย 0
STUDENT_RE = re.compile(r"^\d{7,10}$")              # รหัสนศ.
EMP_RE     = re.compile(r"^[A-Za-z0-9\-]{3,20}$")   # รูปแบบรหัสบุคลากร (ยืดหยุ่น)

ALLOWED_MEMBER_TYPES = {"student", "teacher", "officer", "staff"}
ALLOWED_GENDERS      = {"male", "female", "other"}

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @staticmethod
    def _norm(s: str) -> str:
        return (s or "").strip()

    def validate_register(self, data: Dict) -> Optional[str]:
        required = [
            "name", "major", "member_type", "phone",
            "email", "password", "confirm_password", "gender"
        ]
        for f in required:
            if f not in data or self._norm(str(data[f])) == "":
                return f"Missing field: {f}"

        member_type = self._norm(data["member_type"]).lower()
        email       = self._norm(data["email"]).lower()
        phone       = self._norm(data["phone"])
        gender      = self._norm(data["gender"]).lower()

        if not EMAIL_RE.match(email):
            return "Email must be a valid @kmitl.ac.th address"
        if not PHONE_RE.match(phone):
            return "Invalid phone number"
        if member_type not in ALLOWED_MEMBER_TYPES:
            return f"member_type must be one of: {', '.join(ALLOWED_MEMBER_TYPES)}"
        if gender not in ALLOWED_GENDERS:
            return f"gender must be one of: {', '.join(ALLOWED_GENDERS)}"

        password = str(data["password"])
        confirm  = str(data["confirm_password"])
        if len(password) < 6:
            return "Password must be at least 6 characters"
        if password != confirm:
            return "Password and Confirm-Password do not match"

        # ---- ตรวจ id ตามประเภท ----
        student_id  = self._norm(data.get("student_id"))
        employee_id = self._norm(data.get("employee_id") or "")

        if member_type == "student":
            if not student_id:
                return "Missing field: student_id"
            if not STUDENT_RE.match(student_id):
                return "Invalid student_id format"
            if self.user_repo.find_by_student_id(student_id):
                return "Student ID already registered"
        else:
            emp = employee_id or student_id  # รองรับกรณีส่งมาในช่อง student_id เดิม
            if not emp:
                return "Missing field: employee_id"
            if not EMP_RE.match(emp):
                return "Invalid employee_id format"
            if self.user_repo.find_by_employee_id(emp):
                return "Employee ID already registered"

        # ซ้ำ email
        if self.user_repo.find_by_email(email):
            return "Email already registered"

        return None

    def register(self, data: Dict):
        member_type = self._norm(data["member_type"]).lower()
        student_id  = self._norm(data.get("student_id"))
        employee_id = self._norm(data.get("employee_id") or "")

        if member_type == "student":
            payload_sid = student_id
            payload_eid = None
        else:
            payload_sid = None
            payload_eid = employee_id or student_id

        record = {
            "student_id":   payload_sid,
            "employee_id":  payload_eid,
            "name":         self._norm(data["name"]),
            "major":        self._norm(data["major"]),
            "member_type":  member_type,
            "phone":        self._norm(data["phone"]),
            "email":        self._norm(str(data["email"])).lower(),
            "gender":       self._norm(data["gender"]).lower(),
            "password_hash": generate_password_hash(str(data["password"])),
            "role":         "member",
        }
        # ให้ repository จัดการ ORM/SQL เอง
        user = self.user_repo.upsert(record)
        return user
