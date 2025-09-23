from __future__ import annotations
from typing import Dict, Optional, Tuple, Union
from dataclasses import is_dataclass
from werkzeug.security import generate_password_hash, check_password_hash

from app.repositories.user_repository import UserRepository
from app.services import validators as v  #

try:
    from app.services.schemas import LoginDTO  # @dataclass {email, password}
except Exception:
    LoginDTO = None  # type: ignore


ALLOWED_MEMBER_TYPES = {"student", "teacher", "officer", "staff"}
ALLOWED_GENDERS      = {"male", "female", "other"}


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    @staticmethod
    def _norm(s: str) -> str:
        return v.norm(s)

    # ----------------- Register -----------------
    def validate_register(self, data: Dict) -> Optional[str]:
        required = [
            "name", "major", "member_type", "phone",
            "email", "password", "confirm_password", "gender"
        ]
        for f in required:
            if f not in data or v.norm(str(data[f])) == "":
                return f"Missing field: {f}"

        member_type = v.norm(data["member_type"]).lower()
        email       = v.norm(data["email"]).lower()
        phone       = v.norm(data["phone"])
        gender      = v.norm(data["gender"]).lower()

        if member_type not in ALLOWED_MEMBER_TYPES:
            return f"member_type must be one of: {', '.join(ALLOWED_MEMBER_TYPES)}"
        if gender not in ALLOWED_GENDERS:
            return f"gender must be one of: {', '.join(ALLOWED_GENDERS)}"
        if not v.validate_email(email):
            return "Email must be a valid @kmitl.ac.th address"
        if not v.validate_phone(phone):
            return "Invalid phone number"

        password = str(data["password"])
        confirm  = str(data["confirm_password"])
        if len(password) < 6:
            return "Password must be at least 6 characters"
        if password != confirm:
            return "Password and Confirm-Password do not match"

        # ---- ตรวจ id ตามประเภท ----
        student_id  = v.norm(data.get("student_id"))
        employee_id = v.norm(data.get("employee_id") or "")

        if member_type == "student":
            if not student_id:
                return "Missing field: student_id"
            if not v.validate_student_id(student_id):
                return "Invalid student_id format"
            if self.user_repo.find_by_student_id(student_id):
                return "Student ID already registered"
        else:
            emp = employee_id or student_id
            if not emp:
                return "Missing field: employee_id"
            if not v.validate_employee_id(emp):
                return "Invalid employee_id format"
            if self.user_repo.find_by_employee_id(emp):
                return "Employee ID already registered"

        if self.user_repo.find_by_email(email):
            return "Email already registered"

        return None

    def register(self, data: Dict):
        member_type = v.norm(data["member_type"]).lower()
        student_id  = v.norm(data.get("student_id"))
        employee_id = v.norm(data.get("employee_id") or "")

        if member_type == "student":
            sid, eid = student_id, None
        else:
            eid = employee_id or student_id
            sid = None

        record = {
            "student_id":   sid,
            "employee_id":  eid,
            "name":         v.norm(data["name"]),
            "major":        v.norm(data["major"]),
            "member_type":  member_type,
            "phone":        v.norm(data["phone"]),
            "email":        v.norm(str(data["email"])).lower(),
            "gender":       v.norm(data["gender"]).lower(),
            "password_hash": generate_password_hash(str(data["password"])),
            "role":         "member",
        }

        return self.user_repo.add(record)

    # ----------------- Login -----------------
    def login(
        self,
        creds: Union["LoginDTO", Dict, Tuple[str, str], None] = None,
        password: Optional[str] = None,
    ):
        if is_dataclass(creds) and getattr(creds, "__class__", None).__name__ == "LoginDTO":
            email = v.norm(creds.email).lower()
            pwd   = creds.password
        elif isinstance(creds, dict):
            email = v.norm(str(creds.get("email", ""))).lower()
            pwd   = creds.get("password", "")
        elif isinstance(creds, tuple):
            email = v.norm(str(creds[0])).lower()
            pwd   = creds[1]
        else:
            email = v.norm(str(creds or "")).lower()
            pwd   = password or ""

        if not email or not pwd:
            return False, "Email and password are required", None

        user = self.user_repo.find_by_email(email)
        if not user:
            return False, "User not found", None

        pwd_hash = _get(user, "password_hash")
        if not pwd_hash or not check_password_hash(pwd_hash, pwd):
            return False, "Invalid password", None

        return True, None, user

    authenticate = login


def _get(obj, name: str, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)