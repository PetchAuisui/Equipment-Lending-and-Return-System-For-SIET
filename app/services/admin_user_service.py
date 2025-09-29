from math import ceil
from typing import Dict, Any, List, Optional, Tuple
from app.repositories.user_repository import UserRepository
from sqlalchemy import text
from app.services import validators as v

ALLOWED_MEMBER_TYPES = {"student", "teacher", "officer", "staff"}
ALLOWED_GENDERS      = {"male", "female"}

class AdminUserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_table(self, page: int = 1, per_page: int = 10, q: str = "") -> Dict[str, Any]:
        # normalize
        try:
            page = max(int(page or 1), 1)
        except Exception:
            page = 1
        try:
            per_page = min(max(int(per_page or 10), 5), 50)
        except Exception:
            per_page = 10
        q = (q or "").strip()

        result = self.repo.list_users(page=page, per_page=per_page, q=q)
        rows, total = result["rows"], result["total"]

        # map rows
        users: List[Dict[str, Any]] = []
        for u in rows:
            uid = u.get("user_id") or u.get("id")
            code = u.get("student_id") or u.get("employee_id") or (f"U{uid:04d}" if uid else "U")
            users.append({
                "user_id": uid,
                "code": code,
                "name": u.get("name", "-"),
                "email": u.get("email", "-"),
                "role": u.get("role", "member"),               
                "member_type": u.get("member_type", "-"),   
                "major": u.get("major", "-"),
                "phone": u.get("phone", "-"),
            })

        total_pages = ceil(total / per_page) if per_page else 1

        return {
            "users": users,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "q": q,
        }
    

    def drop_user(self, user_id: int) -> bool:
        sql = text("DELETE FROM users WHERE user_id = :uid RETURNING user_id")
        row = self.repo.session.execute(sql, {"uid": user_id}).first()
        if not row:
            return False    
        self.repo.session.commit()
        return True
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.repo.session.execute(
            text("SELECT * FROM users WHERE user_id = :uid LIMIT 1"),
            {"uid": user_id}
        ).first()
        return dict(row._mapping) if row else None
    
    def validate_update(self, user_id: int, data: Dict[str, Any]) -> Optional[str]:
        name   = v.norm(data.get("name"))
        email  = v.norm(data.get("email")).lower()
        phone  = v.norm(data.get("phone"))
        major  = v.norm(data.get("major"))
        mtype  = v.norm(data.get("member_type")).lower()
        gender = v.norm(data.get("gender")).lower()

        if not name:
            return "Missing field: name"
        if not email or not v.validate_email(email):
            return "Email must be a valid @kmitl.ac.th address"
        if phone and not v.validate_phone(phone):
            return "Invalid phone number"
        if mtype and mtype not in ALLOWED_MEMBER_TYPES:
            return f"member_type must be one of: {', '.join(ALLOWED_MEMBER_TYPES)}"
        if gender and gender not in ALLOWED_GENDERS:
            return f"gender must be one of: {', '.join(ALLOWED_GENDERS)}"

        # ตรวจ uniqueness ของ email ถ้าเปลี่ยน
        current = self.get_user(user_id)
        if not current:
            return "User not found"
        if email and email != (current.get("email") or "").lower():
            exists = self.repo.session.execute(
                text("SELECT user_id FROM users WHERE email = :email LIMIT 1"),
                {"email": email}
            ).first()
            if exists and int(exists.user_id) != int(user_id):
                return "Email already in use"

        return None

    def update_user(self, user_id: int, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        err = self.validate_update(user_id, data)
        if err:
            return None, err

        allowed = {"name", "email", "phone", "major", "member_type", "gender"}
        payload = {k: v.norm(data.get(k)) for k in allowed}

        row = self.repo.session.execute(
            text("""
                UPDATE users
                SET name = :name,
                    email = :email,
                    phone = :phone,
                    major = :major,
                    member_type = :member_type,
                    gender = :gender,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :uid
                RETURNING *
            """),
            {**payload, "uid": user_id}
        ).first()
        self.repo.session.commit()

        return (dict(row._mapping), None) if row else (None, "User not found")