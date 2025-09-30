from flask import Blueprint, render_template, request, flash, redirect, url_for, session  # ✅ เพิ่ม session
from app.db.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.admin_user_service import AdminUserService

# ----- /admin (dashboard) -----
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/")
def admin_home():
    return render_template("admin/home_admin.html")

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
    return render_template("admin/user.html", **payload)

@admin_users_bp.post("/<int:user_id>/delete", endpoint="delete")
def delete(user_id: int):
    actor_id = session.get("user_id")  # ✅ ใครเป็นคนลบ (อาจ None ถ้ายังไม่ได้เก็บ)
    ok = _svc().drop_user(user_id, actor_id=actor_id)
    if not ok:
        return {"error": "User not found"}, 404
    return {"ok": True}, 200

@admin_users_bp.get("/<int:user_id>/edit", endpoint="edit_user_page")
def edit_user_page(user_id: int):
    svc = _svc()
    user = svc.get_user(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("admin_users.index"))
    return render_template("admin/edit_user.html", user=user)

@admin_users_bp.post("/<int:user_id>/edit", endpoint="edit_user_action")
def edit_user_action(user_id: int):
    svc = _svc()
    form = request.form.to_dict()
    actor_id = session.get("user_id")  # ✅ ใครเป็นคนแก้
    updated, err = svc.update_user(user_id, form, actor_id=actor_id)

    if err:
        user = svc.get_user(user_id)
        return render_template(
            "admin/edit_user.html",
            user=user,
            error=err,
            old=form
        ), 400

    flash("อัปเดตข้อมูลเรียบร้อยแล้ว ✅", "success")
    return redirect(url_for("admin_users.index"))
