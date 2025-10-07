from flask import render_template, request, redirect, url_for, current_app, flash, abort, session
from app.blueprints.inventory import inventory_bp
from app.services.lend_device_service import get_grouped_equipments_separated
from app.db.db import SessionLocal
from app.models.equipment import Equipment
from app.models.equipment_images import EquipmentImage
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.sql import exists, and_
from app.models.stock_movements import StockMovement
import os, uuid


@inventory_bp.route('/equipments/lend_device')
def lend_device():
    equipments = lend_device_service.get_equipment_list()
    return render_template("pages_inventory/lend_device.html", equipments=equipments)

@inventory_bp.route('/equipments/lend', methods=['GET'])

def lend():
    return render_template('pages_inventory/lend.html')

@inventory_bp.route("/admin/equipments", methods=["GET"], endpoint="admin_equipment_list")
def admin_equipment_list():
    q = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    db = SessionLocal()
    try:
        query = (
            db.query(Equipment)
              .options(joinedload(Equipment.images))
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
def admin_equipment_detail(eid):
    db = SessionLocal()
    try:
        item = (
            db.query(Equipment)
              .options(joinedload(Equipment.images))
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
        return render_template("pages_inventory/admin_equipment_detail.html", item=item)
    finally:
        db.close()

@inventory_bp.route("/admin/equipments/new", methods=["GET", "POST"])
def admin_equipment_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        code = (request.form.get("code") or "").strip()
        category = (request.form.get("category") or "").strip()
        detail = (request.form.get("detail") or "").strip()
        brand = (request.form.get("brand") or "").strip()
        status = (request.form.get("status") or "").strip()
        buy_date_raw = (request.form.get("buy_date") or "").strip()
        img = request.files.get("image")

        buy_date = None
        if buy_date_raw:
            try:
                buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
            except ValueError:
                buy_date = None

        if not name or not code:
            flash("กรุณากรอกชื่ออุปกรณ์และรหัส/หมายเลข", "error")
            return render_template("pages_inventory/admin_equipment_new.html")

        db = SessionLocal()
        try:
            now = datetime.utcnow()
            new_equipment = Equipment(
                name=name,
                code=code,
                category=category,
                detail=detail,
                brand=brand,
                buy_date=buy_date,
                status=status or "available",
                created_at=now,
            )
            db.add(new_equipment)
            db.commit()
            db.refresh(new_equipment)

            if img and img.filename:
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                img.save(os.path.join(upload_dir, fname))

                image_path = f"uploads/equipment/{fname}"
                img_record = EquipmentImage(
                    equipment_id=new_equipment.equipment_id,
                    image_path=image_path,
                    created_at=datetime.utcnow()
                )
                db.add(img_record)
                db.commit()

            flash("เพิ่มอุปกรณ์เรียบร้อย", "success")
            return redirect(url_for("inventory.admin_equipment_list"))

        except IntegrityError:
            db.rollback()
            flash("รหัส/หมายเลขนี้ถูกใช้แล้ว", "error")
            return render_template("pages_inventory/admin_equipment_new.html")
        finally:
            db.close()

    return render_template("pages_inventory/admin_equipment_new.html")

@inventory_bp.route("/admin/equipments/<int:eid>/edit", methods=["GET", "POST"], endpoint="admin_equipment_edit")
def admin_equipment_edit(eid):
    db = SessionLocal()
    try:
        item = db.query(Equipment).options(joinedload(Equipment.images)).filter(Equipment.equipment_id == eid).first()
        if not item:
            abort(404)

        if request.method == "POST":
            item.name = (request.form.get("name") or "").strip()
            item.code = (request.form.get("code") or "").strip()
            item.category = (request.form.get("category") or "").strip()
            item.detail = (request.form.get("detail") or "").strip()
            item.brand = (request.form.get("brand") or "").strip()
            item.status = (request.form.get("status") or "").strip() or item.status

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
                for im in list(item.images):
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
def admin_equipment_delete(eid):
    db = SessionLocal()
    try:
        item = db.query(Equipment).filter(Equipment.equipment_id == eid).first()
        if not item:
            flash("❌ ไม่พบอุปกรณ์", "error")
            return redirect(url_for("inventory.admin_equipment_list"))

        # หา actor_id แบบไม่พึ่ง Flask-Login (ถ้าเก็บไว้ใน session ใช้ได้เลย)
        actor_id = session.get("user_id")  # ถ้าไม่มีระบบ session จะเป็น None

        # บันทึกประวัติ
        movement = StockMovement(
            equipment_id=item.equipment_id,
            history=f"[DELETED] อุปกรณ์ '{item.name}' (รหัส: {item.code}) ถูกลบออกจากระบบ",
            actor_id=actor_id,
            created_at=datetime.utcnow()
        )
        db.add(movement)

        # ลบจริง
        db.delete(item)
        db.commit()

        flash("🗑️ ลบอุปกรณ์เรียบร้อย (เก็บประวัติแล้ว)", "success")
        return redirect(url_for("inventory.admin_equipment_list"))
    finally:
        db.close()
