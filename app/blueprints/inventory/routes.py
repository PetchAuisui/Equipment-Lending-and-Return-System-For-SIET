from flask import render_template, request, redirect, url_for, current_app, flash, abort, session
from app.blueprints.inventory import inventory_bp
from app.services.lend_device_service import get_grouped_equipments_separated
from app.services import lend_service
from app.db.db import SessionLocal
from app.models.equipment import Equipment
from app.db.models import EquipmentImage
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from sqlalchemy.sql import exists, and_
from app.models.stock_movements import StockMovement
import os, uuid
from app.utils.decorators import staff_required
from app.services.equipment_service import EquipmentService


# ===== Helper Factory =====
def _equip_svc():
    """helper สำหรับสร้าง service ของอุปกรณ์"""
    return EquipmentService()

@inventory_bp.route("/lend_device")
def lend_device():
    equipments = get_grouped_equipments_separated()

    print("\n=== DEBUG EQUIPMENTS ===")
    for e in equipments["available"]:
        print(f"{e['name']} => {e.get('codes')}")
    print("========================\n")

    return render_template("pages_inventory/lend_device.html", equipments=equipments)

@inventory_bp.route('/lend')
def lend():
    codes_raw = request.args.get("codes", "")
    name = request.args.get("name", "")
    image = request.args.get("image", "")

    # แยกรหัสออกเป็น list
    codes = [c.strip() for c in codes_raw.split(",") if c.strip()]

    # ✅ ดึงข้อมูลวิชาและอาจารย์จาก service
    subjects = lend_service.get_all_subjects()
    teachers_data = lend_service.get_all_users()
    teachers = teachers_data["teachers"]

    # ✅ 3. ดึงข้อมูล confirm จากอุปกรณ์
    confirm_status = False  # ค่าเริ่มต้น (กรณีหาไม่เจอ)
    with SessionLocal() as db:
        if codes:
            equipment = db.query(Equipment).filter(Equipment.code == codes[0]).first()
            if equipment:
                confirm_status = equipment.confirm  # ✅ ดึงค่าจาก DB

    # ✅ เวลาปัจจุบันตาม Bangkok
    now_bangkok = datetime.now(ZoneInfo("Asia/Bangkok"))

    # ✅ print log ไปที่ console (ตามที่คุณขอ)
    print("\n--- Teachers Data ---")
    for t in teachers:
        print(f"ID: {t['user_id']}, Name: {t['name']}")
    print("---------------------\n")

    # ✅ ส่งข้อมูลไป render
    return render_template(
        "pages_inventory/lend.html",
        name=name,
        image=image,
        codes=codes,
        subjects=subjects,
        teachers=teachers,
        confirm=confirm_status,
        now_bangkok=now_bangkok  # <-- ส่งเวลา Bangkok ไป template
    )


@inventory_bp.route("/lend_submit", methods=["POST"])
def lend_submit():
    """
    ✅ รับข้อมูลจากฟอร์ม /lend แล้วส่งให้ lend_service.lend_data()
    """
    form = request.form

    # เก็บข้อมูลจากฟอร์มทั้งหมด
    data = {
        "device_name": form.get("device_name") or None,
        "code": form.get("code") or None,
        "borrow_date": form.get("borrow_date") or None,
        "return_date": form.get("return_date") or None,
        "borrower_name": form.get("borrower_name") or None,
        "phone": form.get("phone") or None,
        "major": form.get("major") or None,
        "subject": form.get("subject") or None,
        "teacher": form.get("teacher") or None,
        "reason": form.get("reason") or None,
    }

    # แปลงเป็น list
    data_list = [data.get(key, None) for key in data]

    # ✅ เรียกไปที่ lend_service.py
    lend_service.lend_data(data_list)

    flash("✅ ส่งข้อมูลไปยัง lend_service แล้ว", "success")
    return redirect(url_for("tracking.track_index"))

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
            actor_id=session.get("user_id"),
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

@inventory_bp.route("/equipments/<int:eid>/detail", methods=["GET"])
def equipment_detail(eid):
    from app.services import lend_device_service

    svc = lend_device_service.get_grouped_equipments_separated()
    all_items = svc["available"] + svc["unavailable"]

    item = next((i for i in all_items if i["equipment_id"] == eid), None)
    if not item:
        abort(404)

    return render_template("pages_inventory/equipment_detail.html", item=item)