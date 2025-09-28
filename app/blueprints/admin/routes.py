from flask import Blueprint, render_template, request
from app.db.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.admin_user_service import AdminUserService   # ✅ เพิ่มบรรทัดนี้


# ----- /admin (dashboard) -----
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/")
def admin_home():
    return render_template("pages_admin/home_admin.html")


# ----- /admin/users (จัดการสมาชิก) -----
admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")

def _svc():
    return AdminUserService(UserRepository(SessionLocal()))

@admin_users_bp.get("/", endpoint="index")
def users_index():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    q = request.args.get("q", "")

    svc = _svc()
    payload = svc.get_user_table(page=page, per_page=per_page, q=q)

    return render_template("pages_admin/user.html", **payload)