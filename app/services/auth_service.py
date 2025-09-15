# app/services/auth_service.py
from __future__ import annotations

import re
from typing import Dict, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.repositories.user_repository import UserRepository


EMAIL_RE   = re.compile(r"^[A-Za-z0-9._%+\-]+@kmitl\.ac\.th$", re.IGNORECASE)
PHONE_RE   = re.compile(r"^0\d{8,9}$")          # 9-10 หลักขึ้นต้นด้วย 0
STUDENT_RE = re.compile(r"^\d{7,10}$")          # ปรับตาม format ที่ใช้จริง

ALLOWED_MEMBER_TYPES = {"student", "teacher", "officer", "staff"}
ALLOWED_GENDERS      = {"male", "female", "other"}


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # -------- Utilities --------
    @staticmethod
    def _norm(s: str) -> str:
        return (s or "").strip()

    # -------- Validation --------
    def validate_register(self, data: Dict) -> Optional[str]:
        required = [
            "student_id", "name", "major", "member_type", "phone",
            "email", "password", "confirm_password", "gender"
        ]
        # ว่าง/ไม่มีค่า
        for f in required:
            if f not in data or self._norm(str(data[f])) == "":
                return f"Missing field: {f}"

        # นอร์มอลไลซ์
        student_id = self._norm(data["student_id"])
        name       = self._norm(data["name"])
        major      = self._norm(data["major"])
        member_type= self._norm(data["member_type"]).lower()
        phone      = self._norm(data["phone"])
        email      = self._norm(str(data["email"])).lower()
        gender     = self._norm(data["gender"]).lower()
        password   = str(data["password"])
        confirm    = str(data["confirm_password"])

        # รูปแบบข้อมูล
        if not EMAIL_RE.match(email):
            return "Email must be a valid @kmitl.ac.th address"
        if not STUDENT_RE.match(student_id):
            return "Invalid student_id format"
        if not PHONE_RE.match(phone):
            return "Invalid phone number"
        if member_type not in ALLOWED_MEMBER_TYPES:
            return f"member_type must be one of: {', '.join(ALLOWED_MEMBER_TYPES)}"
        if gender not in ALLOWED_GENDERS:
            return f"gender must be one of: {', '.join(ALLOWED_GENDERS)}"
        if len(password) < 6:
            return "Password must be at least 6 characters"
        if password != confirm:
            return "Password and Confirm-Password do not match"

        # ซ้ำซ้อน
        if self.user_repo.find_by_email(email):
            return "Email already registered"
        if self.user_repo.find_by_student_id(student_id):
            return "Student ID already registered"

        return None

    # -------- Register --------
    def register(self, data: Dict) -> User:
        """
        ต้องเรียก validate_register() ให้ผ่านก่อนทุกครั้ง
        ป้องกันยัด role จากฝั่ง client: บังคับ role='member' เสมอ
        """
        u = User(
            student_id=self._norm(data["student_id"]),
            name=self._norm(data["name"]),
            major=self._norm(data["major"]),
            member_type=self._norm(data["member_type"]).lower(),
            phone=self._norm(data["phone"]),
            email=self._norm(str(data["email"])).lower(),
            gender=self._norm(data["gender"]).lower(),
            password_hash=generate_password_hash(str(data["password"])),
            role="member",
        )
        # upsert: repo ของคุณต้องรองรับ (ถ้าซ้ำ student_id/email ให้ raise / ป้องกันไว้แล้วใน validate)
        self.user_repo.upsert(u.to_dict())
        return u    