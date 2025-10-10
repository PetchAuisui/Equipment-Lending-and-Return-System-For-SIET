from flask import (
    render_template, request, redirect, url_for,
    flash, abort, session, current_app
)
from app.blueprints.inventory import inventory_bp
from app.utils.decorators import staff_required
from datetime import datetime

# ==== Service Imports ====
from app.services.equipment_service import EquipmentService
from app.services.lend_device_service import LendDeviceService

# ==== Helper Factory ====
def _equip_svc(): return EquipmentService()
def _lend_svc(): return LendDeviceService()

# ------------------------------------------------------------
# 1️⃣ หน้า "ระบบยืมอุปกรณ์"
# ------------------------------------------------------------
@inventory_bp.route("/lend_device")
def lend_device():
    """แสดงหน้าระบบยืมอุปกรณ์ (แยก available / unavailable)"""
    equipments = _lend_svc().get_grouped_equipments_separated()
    return render_template("pages_inventory/lend_device.html", equipments=equipments)

@inventory_bp.route("/lend")
def lend():
    """หน้าแบบฟอร์มยืม (อาจใช้ในอนาคต)"""
    return render_template("pages_inventory/lend.html")


# ------------------------------------------------------------
# 2️⃣ ส่วนของแอดมิน - แสดง/เพิ่ม/แก้ไข/ลบ อุปกรณ์
# ------------------------------------------------------------
@inventory_bp.route("/admin/equipments", methods=["GET"], endpoint="admin_equipment_list")
@staff_required
def admin_equipment_list():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    items = _equip_svc().list(q=q, category=category)
    return render_template("pages_inventory/admin_equipment_list.html", items=items)

@inventory_bp.route("/admin/equipments/<int:eid>", methods=["GET"], endpoint="admin_equipment_detail")
@staff_required
def admin_equipment_detail(eid):
    item = _equip_svc().get(eid)
    if not item:
        abort(404)
    return render_template("pages_inventory/admin_equipment_detail.html", item=item, equipment=item)

@inventory_bp.route("/admin/equipments/new", methods=["GET", "POST"])
@staff_required
def admin_equipment_new():
    """เพิ่มอุปกรณ์ใหม่ + อัปโหลดรูปตั้งแต่ตอนเพิ่ม"""
    if request.method == "POST":
        form = request.form
        buy_date = None
        if form.get("buy_date"):
            try:
                buy_date = datetime.strptime(form["buy_date"], "%Y-%m-%d").date()
            except ValueError:
                flash("⚠️ รูปแบบวันที่ไม่ถูกต้อง", "error")
                return render_template("pages_inventory/admin_equipment_new.html")

        ok, err, _ = _equip_svc().create(
            name=form.get("name"), code=form.get("code"),
            category=form.get("category"), brand=form.get("brand"),
            detail=form.get("detail"), buy_date=buy_date,
            status=form.get("status") or "available",
            confirm=form.get("require_teacher_approval") == "1",
            actor_id=session.get("user_id"),
            image_file=request.files.get("image"),
        )
        if not ok:
            flash(err, "error")
            return render_template("pages_inventory/admin_equipment_new.html")

        flash("✅ เพิ่มอุปกรณ์ใหม่เรียบร้อยแล้ว!", "success")
        return redirect(url_for("inventory.admin_equipment_list"))

    return render_template("pages_inventory/admin_equipment_new.html")

@inventory_bp.route("/admin/equipments/<int:eid>/edit", methods=["GET", "POST"], endpoint="admin_equipment_edit")
@staff_required
def admin_equipment_edit(eid):
    """แก้ไขข้อมูลอุปกรณ์ + เปลี่ยนรูป"""
    if request.method == "POST":
        form = request.form
        buy_date = None
        if form.get("buy_date"):
            try:
                buy_date = datetime.strptime(form["buy_date"], "%Y-%m-%d").date()
            except ValueError:
                pass

        ok, err, _ = _equip_svc().update(
            equipment_id=eid,
            name=form.get("name"), code=form.get("code"),
            category=form.get("category"), brand=form.get("brand"),
            detail=form.get("detail"), buy_date=buy_date,
            status=form.get("status"), confirm=form.get("confirm"),
            image_file=request.files.get("image"),
        )
        if not ok:
            flash(err, "error")
            return redirect(url_for("inventory.admin_equipment_edit", eid=eid))

        flash("บันทึกการแก้ไขแล้ว", "success")
        return redirect(url_for("inventory.admin_equipment_list"))

    item = _equip_svc().get(eid)
    if not item:
        abort(404)
    return render_template("pages_inventory/admin_equipment_edit.html", item=item)

@inventory_bp.route("/admin/equipments/<int:eid>/delete", methods=["POST"])
@staff_required
def admin_equipment_delete(eid):
    """ลบอุปกรณ์ (Soft Delete + ลบไฟล์ภาพจริง)"""
    ok, err, _ = _equip_svc().soft_delete(eid, actor_id=session.get("user_id"))
    if not ok:
        flash(err, "error")
    else:
        flash("🗑️ ลบอุปกรณ์และรูปภาพเรียบร้อย (บันทึกประวัติแล้ว)", "success")
    return redirect(url_for("inventory.admin_equipment_list"))

@inventory_bp.route("/equipments/<int:eid>/toggle_teacher_approval", methods=["POST"])
@staff_required
def toggle_teacher_approval(eid):
    """เปิด/ปิดโหมดต้องให้อาจารย์อนุมัติ"""
    svc = _equip_svc()
    eq = svc.get(eid)
    if not eq:
        flash("❌ ไม่พบอุปกรณ์", "error")
    else:
        eq.confirm = not eq.confirm
        svc.repo.commit()
        flash(f"{'เปิด' if eq.confirm else 'ปิด'}โหมดให้อาจารย์อนุมัติสำเร็จ", "success")
    return redirect(url_for("inventory.admin_equipment_list"))
