from math import ceil
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import text
from app.repositories.user_repository import UserRepository
from app.services import validators as v

# -------- ใข้คนละความหมายกัน --------
ALLOWED_MEMBER_TYPES = {"student", "teacher", "officer"}
ALLOWED_GENDERS      = {"male", "female", "other"}
ALLOWED_ROLES        = {"member", "staff"}

class AdminUserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_table(self, page: int = 1, per_page: int = 10, q: str = "") -> Dict[str, Any]:
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
            "users": users, "page": page, "per_page": per_page,
            "total": total, "total_pages": total_pages, "q": q,
        }

    def drop_user(self, user_id: int, *, actor_id: Optional[int]) -> bool:
        """ลบผู้ใช้ + เขียน audit 'deleted' ผ่าน repository"""
        return self.repo.delete_user(user_id, actor_id=actor_id)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self.repo.session.execute(
            text("SELECT * FROM users WHERE user_id = :uid LIMIT 1"),
            {"uid": user_id}
        ).first()
        return dict(row._mapping) if row else None

    def validate_update(self, user_id: int, data: Dict[str, Any]) -> Optional[str]:
        current = self.get_user(user_id)
        if not current:
            return "User not found"

        # ใช้ค่าที่ส่งมา ถ้าไม่ส่งให้ fallback เป็นค่าปัจจุบัน (เพื่อเทียบ/ตรวจ)
        name   = v.norm(data.get("name"))   or (current.get("name") or "")
        email  = (v.norm(data.get("email")) or (current.get("email") or "")).lower()
        phone  = v.norm(data.get("phone"))  or (current.get("phone") or "")
        major  = v.norm(data.get("major"))  or (current.get("major") or "")
        mtype  = (v.norm(data.get("member_type")) or (current.get("member_type") or "")).lower()
        gender = (v.norm(data.get("gender")) or (current.get("gender") or "")).lower()
        role   = (v.norm(data.get("role")) or (current.get("role") or "member")).lower()

        if not name:
            return "Missing field: name"
        if email and not v.validate_email(email):
            return "Email must be a valid @kmitl.ac.th address"
        if phone and not v.validate_phone(phone):
            return "Invalid phone number"
        if mtype and mtype not in ALLOWED_MEMBER_TYPES:
            return f"member_type must be one of: {', '.join(ALLOWED_MEMBER_TYPES)}"
        if gender and gender not in ALLOWED_GENDERS:
            return f"gender must be one of: {', '.join(ALLOWED_GENDERS)}"
        if role and role not in ALLOWED_ROLES:
            return f"role must be one of: {', '.join(ALLOWED_ROLES)}"

        # ตรวจอีเมลซ้ำเฉพาะกรณีเปลี่ยนจริง
        if email and email != (current.get("email") or "").lower():
            exists = self.repo.session.execute(
                text("SELECT user_id FROM users WHERE email = :email LIMIT 1"),
                {"email": email}
            ).first()
            if exists and int(exists.user_id) != int(user_id):
                return "Email already in use"
        return None

    def update_user(self, user_id: int, data: Dict[str, Any], *, actor_id: Optional[int]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """อัปเดตผู้ใช้ผ่าน repo เพื่อให้เกิด audit 'updated'"""
        current = self.get_user(user_id)
        if not current:
            return None, "User not found"

        err = self.validate_update(user_id, data)
        if err:
            return None, err

        # อัปเดตเฉพาะคีย์ที่อนุญาต (partial update)
        allowed = {"name", "email", "phone", "major", "member_type", "gender", "role"}
        payload = {}
        for k in allowed:
            if k in data:
                payload[k] = v.norm(data.get(k))

        if not payload:
            return current, None

        updated = self.repo.update_user(user_id, payload, actor_id=actor_id)
        if not updated:
            return None, "User not found"
        return updated, None
