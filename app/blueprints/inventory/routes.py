from flask import render_template, request, redirect, url_for
from app.blueprints.inventory import inventory_bp
from app.services import lend_device_service
from app.db.db import SessionLocal
from app.models.equipment import Equipment
from datetime import datetime
from flask import current_app, flash
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
import os, uuid
from app.models.equipment_images import EquipmentImage
from sqlalchemy.orm import joinedload
from flask import abort


@inventory_bp.route('/lend_device')
def lend_device():
    # 📌 ดึงข้อมูลจาก service
    equipments = lend_device_service.get_equipment_list()
    
    # ✅ return template พร้อมส่งข้อมูลไปยัง HTML
    return render_template("pages_inventory/lend_device.html", equipments=equipments)


@inventory_bp.route('/lend')
def lend():
    return render_template("pages_inventory/lend.html")

@inventory_bp.route("/admin/equipments")
def admin_equipment_list():
    q = request.args.get("q", "").strip()
    db = SessionLocal()

    # ✅ โหลด images มาด้วยเวลา query
    query = (
        db.query(Equipment)
          .options(joinedload(Equipment.images))
          .filter(Equipment.is_active == True)
    )

    if q:
        query = query.filter(
            (Equipment.name.ilike(f"%{q}%")) |
            (Equipment.code.ilike(f"%{q}%"))
        )

    # เพื่อกรองตามหมวดหมู่
    category_filter = request.args.get("category", "").strip()
    if category_filter:
        query = query.filter(Equipment.category == category_filter)    

    items = query.order_by(Equipment.created_at.desc()).all()
    db.close()
    return render_template("pages_inventory/admin_equipment_list.html", items=items)


# ฟอร์มเพิ่มอุปกรณ์
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

        # แปลงวันที่ให้เป็น date
        buy_date = None
        if buy_date_raw:
            try:
                buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
            except ValueError:
                buy_date = None

        # validate
        if not name or not code:
            flash("กรุณากรอกชื่ออุปกรณ์และรหัส/หมายเลข", "error")
            return render_template("pages_inventory/admin_equipment_new.html")

        # อัปโหลดรูป (อาจเว้นได้)
        img = request.files.get("image")
        image_path = None
        if img and img.filename:
            # ตรวจนามสกุลไฟล์
            allowed = current_app.config.get("ALLOWED_IMAGE_EXT", {"jpg","jpeg","png","gif","webp"})
            if "." not in img.filename or img.filename.rsplit(".",1)[1].lower() not in allowed:
                flash("อนุญาตเฉพาะไฟล์ภาพ jpg, jpeg, png, gif, webp", "error")
                return render_template("pages_inventory/admin_equipment_new.html")

        db = SessionLocal()
        try:
            # 1) บันทึกลง equipments
            new_equipment = Equipment(
                name=name,
                code=code,
                category=category,
                detail=detail,
                brand=brand,
                buy_date=buy_date,
                status=status or "available",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_equipment)
            db.commit()
            db.refresh(new_equipment)  # เอา equipment_id ที่เพิ่งสร้าง

            # 2) ถ้ามีรูป → เซฟไฟล์แล้วบันทึกลง equipment_images
            if img and img.filename:
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"

                # โฟลเดอร์เก็บรูป
                upload_dir = current_app.config.get(
                    "UPLOAD_FOLDER",
                    os.path.join(current_app.root_path, "static", "uploads", "equipment")
                )
                os.makedirs(upload_dir, exist_ok=True)

                # เซฟไฟล์
                img.save(os.path.join(upload_dir, fname))

                # เก็บ path แบบ relative จาก static/
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

    # GET → แสดงฟอร์ม
    return render_template("pages_inventory/admin_equipment_new.html")

@inventory_bp.route("/admin/equipments/<int:eid>/edit", methods=["GET", "POST"])
def admin_equipment_edit(eid):
    db = SessionLocal()
    item = (
        db.query(Equipment)
          .options(joinedload(Equipment.images))
          .filter(Equipment.equipment_id == eid, Equipment.is_active == True)
          .first()
    )
    if not item:
        db.close()
        abort(404)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        code = (request.form.get("code") or "").strip()
        category = (request.form.get("category") or "").strip()
        detail = (request.form.get("detail") or "").strip()
        brand = (request.form.get("brand") or "").strip()
        status = (request.form.get("status") or "").strip()
        buy_date_raw = (request.form.get("buy_date") or "").strip()

        buy_date = None
        if buy_date_raw:
            try:
                buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
            except ValueError:
                buy_date = None

        if not name or not code:
            db.close()
            flash("กรุณากรอกชื่ออุปกรณ์และรหัส/หมายเลข", "error")
            return render_template("pages_inventory/admin_equipment_edit.html", item=item)

        # อัปเดตค่า
        item.name = name
        item.code = code
        item.category = category
        item.detail = detail
        item.brand = brand
        item.buy_date = buy_date
        item.status = status or item.status
        item.updated_at = datetime.utcnow()

        # แนบรูปใหม่ (เพิ่มแถวใน equipment_images)
        img = request.files.get("image")
        if img and img.filename:
            allowed = current_app.config.get("ALLOWED_IMAGE_EXT", {"jpg","jpeg","png","gif","webp"})
            if "." in img.filename and img.filename.rsplit(".",1)[1].lower() in allowed:
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = current_app.config.get("UPLOAD_FOLDER", os.path.join("static","uploads","equipment"))
                os.makedirs(upload_dir, exist_ok=True)
                img.save(os.path.join(upload_dir, fname))
                db.add(EquipmentImage(
                    equipment_id=item.equipment_id,
                    image_path=f"uploads/equipment/{fname}",
                    created_at=datetime.utcnow()
                ))

        db.commit()
        db.close()
        flash("บันทึกการแก้ไขแล้ว", "success")
        return redirect(url_for("inventory.admin_equipment_list"))

    # GET
    db.close()
    return render_template("pages_inventory/admin_equipment_edit.html", item=item)
