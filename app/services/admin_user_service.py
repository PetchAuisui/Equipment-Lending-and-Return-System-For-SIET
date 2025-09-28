from math import ceil
from typing import Dict, Any, List
from app.repositories.user_repository import UserRepository

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
                "role": u.get("role", "member"),                 # ✅ role
                "member_type": u.get("member_type", "-"),        # ✅ member_type
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
