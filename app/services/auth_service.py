from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def validate_register(self, data: Dict) -> Optional[str]:
        required = [
            "student_id","name","major","member_type","phone",
            "email","password","confirm_password","gender"
        ]
        for f in required:
            if f not in data or str(data[f]).strip() == "":
                return f"Missing field: {f}"

        if data["password"] != data["confirm_password"]:
            return "Password and Confirm-Password do not match"

        if not data["email"].endswith("@kmitl.ac.th"):
            return "Email must end with @kmitl.ac.th"

        if self.user_repo.find_by_email(data["email"]):
            return "Email already registered"
        if self.user_repo.find_by_student_id(data["student_id"]):
            return "Student ID already registered"

        return None

    def register(self, data: Dict) -> User:
        u = User(
            student_id=data["student_id"].strip(),
            name=data["name"].strip(),
            major=data["major"].strip(),
            member_type=data["member_type"].strip(),
            phone=data["phone"].strip(),
            email=data["email"].strip().lower(),
            gender=data["gender"].strip(),
            password_hash=generate_password_hash(data["password"]),
            role=data.get("role","member"),
        )
        self.user_repo.upsert(u.to_dict())
        return u

    def verify_password(self, password_hash: str, password: str) -> bool:
        return check_password_hash(password_hash, password)
