from flask import render_template, request, redirect, url_for, current_app, flash, abort, session
from app.blueprints.inventory import inventory_bp
from app.services.lend_device_service import get_grouped_equipments_separated
from app.db.db import SessionLocal
from app.db.models import Equipment, EquipmentImage
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.sql import exists, and_
from app.models.stock_movements import StockMovement
import os, uuid
from app.utils.decorators import staff_required


@inventory_bp.route("/lend_device")
def lend_device():
    """
    แสดงหน้าระบบยืมอุปกรณ์
    - ส่ง 2 list: available / unavailable
    """
    equipments = get_grouped_equipments_separated()
    return render_template(
        "pages_inventory/lend_device.html",
        equipments=equipments
    )


@inventory_bp.route('/lend')
def lend():
    return render_template('pages_inventory/lend.html')


@inventory_bp.route("/admin/equipments", methods=["GET"], endpoint="admin_equipment_list")
@staff_required
def admin_equipment_list():
    q = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    db = SessionLocal()
    try:
        query = (
            db.query(Equipment)
              .options(joinedload(Equipment.equipment_images))
              .filter(
                  ~exists().where(
                      and_(
                          StockMovement.equipment_id == Equipment.equipment_id,
                          StockMovement.history.ilike("%[DELETED]%")
                      )
                  )
              )
        )

        if q:
            query = query.filter(
                (Equipment.name.ilike(f"%{q}%")) |
                (Equipment.code.ilike(f"%{q}%"))
            )
        if category_filter:
            query = query.filter(Equipment.category == category_filter)

        items = query.order_by(Equipment.created_at.desc()).all()
        return render_template("pages_inventory/admin_equipment_list.html", items=items)
    finally:
        db.close()


@inventory_bp.route("/admin/equipments/<int:eid>", methods=["GET"], endpoint="admin_equipment_detail")
@staff_required
def admin_equipment_detail(eid):
    db = SessionLocal()
    try:
        item = (
            db.query(Equipment)
              .options(joinedload(Equipment.equipment_images))
              .filter(
                  Equipment.equipment_id == eid,
                  ~exists().where(
                      and_(
                          StockMovement.equipment_id == Equipment.equipment_id,
                          StockMovement.history.ilike("%[DELETED]%")
                      )
                  )
              )
              .first()
        )
        if not item:
            abort(404)

        equipment = item
        return render_template(
            "pages_inventory/admin_equipment_detail.html",
            item=item,
            equipment=equipment
        )
    finally:
        db.close()

@inventory_bp.route("/admin/equipments/new", methods=["GET", "POST"])
@staff_required
def admin_equipment_new():
    db = SessionLocal()
    try:
        if request.method == "POST":
            # รับค่าจากฟอร์ม
            name = request.form.get("name", "").strip()
            code = request.form.get("code", "").strip()
            category = request.form.get("category")
            brand = request.form.get("brand")
            detail = request.form.get("detail")
            buy_date_str = request.form.get("buy_date")
            status = request.form.get("status") or "available"
            confirm = request.form.get("require_teacher_approval") == "1"

            # ✅ ตรวจชื่อ/รหัสว่าง
            if not name or not code:
                flash("⚠️ กรุณากรอกชื่อและรหัสอุปกรณ์", "error")
                return render_template("pages_inventory/admin_equipment_new.html")

            # ✅ ตรวจรหัสซ้ำ
            exists = db.query(Equipment).filter(Equipment.code == code).first()
            if exists:
                flash(f"⚠️ รหัสอุปกรณ์ '{code}' ถูกใช้ไปแล้ว กรุณาใช้รหัสอื่น", "error")
                return render_template("pages_inventory/admin_equipment_new.html")

            # ✅ แปลงวันที่ซื้อ
            buy_date = None
            if buy_date_str:
                try:
                    buy_date = datetime.strptime(buy_date_str, "%Y-%m-%d")
                except ValueError:
                    flash("⚠️ รูปแบบวันที่ไม่ถูกต้อง", "error")
                    return render_template("pages_inventory/admin_equipment_new.html")

            # ✅ เพิ่มอุปกรณ์ใหม่
            new_item = Equipment(
                name=name,
                code=code,
                category=category,
                brand=brand,
                detail=detail,
                buy_date=buy_date,
                status=status,
                confirm=confirm,
                created_at=datetime.utcnow()
            )
            db.add(new_item)
            db.commit()

            # ✅ บันทึกประวัติใน StockMovement
            actor_id = session.get("user_id")
            movement = StockMovement(
                equipment_id=new_item.equipment_id,
                history=f"[ADDED] เพิ่มอุปกรณ์ '{name}' (รหัส: {code})",
                actor_id=actor_id,
                created_at=datetime.utcnow()
            )
            db.add(movement)
            db.commit()

            flash("✅ เพิ่มอุปกรณ์ใหม่เรียบร้อยแล้ว!", "success")
            return redirect(url_for("inventory.admin_equipment_list"))

        # ถ้าเป็น GET
        return render_template("pages_inventory/admin_equipment_new.html")

    except Exception as e:
        db.rollback()
        flash(f"❌ เกิดข้อผิดพลาด: {str(e)}", "error")
        return render_template("pages_inventory/admin_equipment_new.html")

    finally:
        db.close()

@inventory_bp.route("/admin/equipments/<int:eid>/edit", methods=["GET", "POST"], endpoint="admin_equipment_edit")
@staff_required
def admin_equipment_edit(eid):
    db = SessionLocal()
    try:
        item = db.query(Equipment).options(joinedload(Equipment.equipment_images)).filter(Equipment.equipment_id == eid).first()
        if not item:
            abort(404)

        if request.method == "POST":
            item.name = (request.form.get("name") or "").strip()
            item.code = (request.form.get("code") or "").strip()
            item.category = (request.form.get("category") or "").strip()
            item.detail = (request.form.get("detail") or "").strip()
            item.brand = (request.form.get("brand") or "").strip()
            item.status = (request.form.get("status") or "").strip() or item.status
            item.confirm = bool(request.form.get("confirm"))

            buy_date_raw = (request.form.get("buy_date") or "").strip()
            if buy_date_raw:
                try:
                    item.buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
                except ValueError:
                    item.buy_date = None

            img = request.files.get("image")
            if img and img.filename:
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                for im in list(item.equipment_images):
                    try:
                        old_file = os.path.join(upload_dir, os.path.basename(im.image_path))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    except Exception as e:
                        current_app.logger.warning("remove old image failed: %s", e)
                    db.delete(im)

                db.flush()
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                img.save(os.path.join(upload_dir, fname))
                new_img = EquipmentImage(
                    equipment_id=item.equipment_id,
                    image_path=f"uploads/equipment/{fname}",
                    created_at=datetime.utcnow()
                )
                db.add(new_img)

            db.commit()
            flash("บันทึกการแก้ไขแล้ว", "success")
            return redirect(url_for("inventory.admin_equipment_list"))

        return render_template("pages_inventory/admin_equipment_edit.html", item=item)

    finally:
        db.close()

@inventory_bp.route("/admin/equipments/<int:eid>/delete", methods=["POST"])
@staff_required
def admin_equipment_delete(eid):
    db = SessionLocal()
    try:
        item = db.query(Equipment).filter(Equipment.equipment_id == eid).first()
        if not item:
            flash("❌ ไม่พบอุปกรณ์", "error")
            return redirect(url_for("inventory.admin_equipment_list"))

        upload_dir = current_app.config['UPLOAD_FOLDER']

        # ✅ ลบรูปภาพในโฟลเดอร์และ DB ก่อน
        images = db.query(EquipmentImage).filter_by(equipment_id=eid).all()
        for im in images:
            try:
                if im.image_path.startswith("uploads/"):
                    image_path = os.path.join("static", im.image_path.replace("/", os.sep))
                else:
                    image_path = os.path.join(upload_dir, os.path.basename(im.image_path))

                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"🗑️ ลบรูป: {image_path}")
                else:
                    print(f"⚠️ ไม่พบไฟล์รูป: {image_path}")

                db.delete(im)
            except Exception as e:
                current_app.logger.warning(f"⚠️ ลบรูปไม่สำเร็จ: {e}")

        # ✅ เก็บประวัติการลบไว้ใน StockMovement (ก่อนลบอุปกรณ์)
        actor_id = session.get("user_id")
        movement = StockMovement(
            equipment_id=item.equipment_id,
            history=f"[DELETED] อุปกรณ์ '{item.name}' (รหัส: {item.code}) ถูกลบออกจากระบบ",
            actor_id=actor_id,
            created_at=datetime.utcnow()
        )
        db.add(movement)
        db.flush()

        # ✅ ลบเรคคอร์ดของอุปกรณ์เอง
        db.delete(item)
        db.commit()

        flash("🗑️ ลบอุปกรณ์และรูปภาพเรียบร้อย (บันทึกประวัติแล้ว)", "success")
        return redirect(url_for("inventory.admin_equipment_list"))

    finally:
        db.close()

@inventory_bp.route("/equipments/<int:eid>/toggle_teacher_approval", methods=["POST"])
def toggle_teacher_approval(eid):
    db = SessionLocal()
    try:
        eq = db.query(Equipment).filter_by(equipment_id=eid).first()
        if not eq:
            flash("ไม่พบอุปกรณ์", "error")
            return redirect(url_for("inventory.admin_equipment_list"))

        eq.confirm = not eq.confirm
        db.commit()

        msg = (
            f"เปิดโหมด 'ต้องให้อาจารย์อนุมัติ' สำหรับ {eq.name}"
            if eq.confirm
            else f"ปิดโหมดอนุมัติอาจารย์สำหรับ {eq.name}"
        )
        flash(msg, "info")

        return redirect(url_for("inventory.admin_equipment_list"))
    finally:
        db.close()
