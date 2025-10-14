from flask import Blueprint, render_template, request, flash, redirect, url_for, session  # ✅ เพิ่ม session
from sqlalchemy import text  
from app.db.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.admin_user_service import AdminUserService
from app.utils.decorators import staff_required
from app.services import renewal_service
from app.db.models import Renewal
from flask_login import current_user



# ---- สำหรับประวัติยืม-คืน (admin) ----
from app.repositories.history_repository import RentHistoryRepository
from app.services.history_service import BorrowHistoryService


# ==============================
# /admin (dashboard)
# ==============================
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/")
@staff_required
def admin_home():
    return render_template("admin/home_admin.html")


# ==============================
# /admin/users (จัดการสมาชิก)
# ==============================
admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")

def _svc():
    return AdminUserService(UserRepository(SessionLocal()))


@admin_users_bp.get("/", endpoint="index")
@staff_required
def users_index():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    q = request.args.get("q", "")

    svc = _svc()
    payload = svc.get_user_table(page=page, per_page=per_page, q=q)
    return render_template("admin/user.html", **payload)


@admin_users_bp.post("/<int:user_id>/delete", endpoint="delete")
@staff_required
def delete(user_id: int):
    actor_id = session.get("user_id")  # ✅ ใครเป็นคนลบ (อาจ None ถ้ายังไม่ได้เก็บ)
    ok = _svc().drop_user(user_id, actor_id=actor_id)
    if not ok:
        return {"error": "User not found"}, 404
    return {"ok": True}, 200


@admin_users_bp.get("/<int:user_id>/edit", endpoint="edit_user_page")
@staff_required
def edit_user_page(user_id: int):
    svc = _svc()
    user = svc.get_user(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for("admin_users.index"))
    return render_template("admin/edit_user.html", user=user)


@admin_users_bp.post("/<int:user_id>/edit", endpoint="edit_user_action")
@staff_required
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

@admin_users_bp.post("/<int:user_id>/set-password")
@staff_required
def admin_set_password(user_id: int):
    new_password = (request.form.get("new_password") or "").strip()
    confirm      = (request.form.get("confirm_password") or "").strip()
    actor_id     = session.get("user_id")

    ok, err = _svc().set_password_for_user(
        user_id=user_id,
        new_password=new_password,
        confirm_password=confirm,
        actor_id=actor_id,
    )
    if not ok:
        flash(err or "ตั้งรหัสผ่านไม่สำเร็จ", "error")
    else:
        flash("ตั้งรหัสผ่านใหม่เรียบร้อย", "success")

    # กลับไปยังหน้าแก้ไขผู้ใช้เดิม
    return redirect(url_for("admin_users.edit_user_page", user_id=user_id))



admin_history_bp = Blueprint("admin_history", __name__, url_prefix="/admin/history")

def _hist_svc():
    """Service layer สำหรับดึงประวัติยืม-คืน"""
    return BorrowHistoryService(RentHistoryRepository(SessionLocal()))

def _user_repo():
    return UserRepository(SessionLocal())


@admin_history_bp.get("/", endpoint="index")
@staff_required
def admin_history_index():
    """
    แสดงประวัติการยืม-คืนของผู้ใช้ทุกคน (สำหรับแอดมิน/เจ้าหน้าที่)
    URL: /admin/history/
    """
    repo = _user_repo()
    svc = _hist_svc()

    # ดึง user ทั้งหมด (เฉพาะคอลัมน์ที่ต้องใช้)
    users = repo.session.execute(
        text("SELECT user_id, name, email, student_id, employee_id FROM users")
    ).fetchall()

    all_items = []
    for u in users:
        u = dict(u._mapping)
        histories = svc.get_for_user(u["user_id"], returned_only=False)
        for h in histories:
            h.update({
                "user_name": u["name"],
                "student_id": u["student_id"],
                "employee_id": u["employee_id"],
            })
            all_items.append(h)

    # เรียงจากล่าสุด
    all_items.sort(key=lambda x: x.get("start_date") or "", reverse=True)

    # ใช้ template เดิมที่คุณมีอยู่แล้ว
    return render_template("pages_history/admin_all_history.html", items=all_items)

from app.controllers.admin_history_controller import AdminHistoryController

# ใช้ factory/guard เดิมของคุณ
AdminHistoryController(
    bp=admin_history_bp,
    hist_svc_factory=_hist_svc,
    user_repo_factory=_user_repo,
    staff_guard=staff_required,
)

from app.services.item_broke_service import ItemBrokeService


@admin_bp.get('/lost-reports', endpoint='lost_reports')
@staff_required
def lost_reports():
    svc = ItemBrokeService()
    items = svc.list_reports()
    return render_template('admin/lost_list.html', items=items)


@admin_bp.get('/lost-reports/<int:item_id>', endpoint='lost_report_detail')
@staff_required
def lost_report_detail(item_id: int):
    svc = ItemBrokeService()
    item = svc.get_report(item_id)
    if not item:
        flash('ไม่พบรายการ', 'error')
        return redirect(url_for('admin.lost_reports'))
    return render_template('admin/lost_detail.html', item=item)


@admin_bp.post('/lost-reports/<int:item_id>/update', endpoint='lost_report_update')
@staff_required
def lost_report_update(item_id: int):
    new_status = request.form.get('update_status')
    svc = ItemBrokeService()
    ok = svc.set_status(item_id, new_status)
    if ok:
        flash('อัปเดตสถานะเรียบร้อย', 'success')
    else:
        flash('ไม่สามารถอัปเดตสถานะได้', 'error')
    return redirect(url_for('admin.lost_reports'))


@admin_bp.get("/confrim_add_time")
@staff_required
def confrim_add_time():
    success, data = renewal_service.get_renewal_summary_service()
    if not success:
        flash("เกิดข้อผิดพลาดในการโหลดข้อมูล", "danger")
        data = {"renewals": [], "history_renewals": []}

    # ✅ ต้องส่งเฉพาะ list ของ pending
    return render_template(
        "admin/confrim_add_time.html",
        renewals=data["renewals"]  # ❗️อย่าส่ง data ตรง ๆ
    )

@admin_bp.get("/confrim_add_time_history")
@staff_required
def confrim_add_time_history():
    success, data = renewal_service.get_renewal_summary_service()
    if not success:
        flash("เกิดข้อผิดพลาดในการโหลดข้อมูล", "danger")
        data = {"renewals": [], "history_renewals": []}

    return render_template(
        "admin/confrim_add_time_history.html",
        history_renewals=data["history_renewals"]
    )


from flask import request, session, redirect, url_for, flash
from app.services import renewal_service


@admin_bp.post("/approve_renewal/<int:renewal_id>")
def approve_renewal(renewal_id):
    user_id = session.get("user_id")  # ✅ ดึงจาก session (user ที่ล็อกอิน)
    success, msg = renewal_service.approve_renewal_service(renewal_id, user_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for("admin.confrim_add_time"))


@admin_bp.post("/reject_renewal/<int:renewal_id>")
def reject_renewal(renewal_id):
    user_id = session.get("user_id")  # ✅ ดึงจาก session (user ที่ล็อกอิน)
    success, msg = renewal_service.reject_renewal_service(renewal_id, user_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for("admin.confrim_add_time"))
