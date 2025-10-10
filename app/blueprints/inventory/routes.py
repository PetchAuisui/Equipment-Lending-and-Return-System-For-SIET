from flask import render_template, request, redirect, url_for, current_app, flash, abort
from app.blueprints.inventory import inventory_bp
from app.services import lend_device_service
from app.db.db import SessionLocal
from app.models.equipment import Equipment
from app.models.equipment_images import EquipmentImage
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid
from app.services.return_item import ReturnItemService


@inventory_bp.route('/equipments/lend_device')
def lend_device():
    # 📌 ดึงข้อมูลจาก service
    equipments = lend_device_service.get_equipment_list()
    # ✅ ส่งต่อไปหน้า UI
    return render_template("pages_inventory/lend_device.html", equipments=equipments)


@inventory_bp.route('/equipments/lend', methods=['GET'])
def lend():
    return render_template('pages_inventory/lend.html')


@inventory_bp.route("/admin/equipments")
def admin_equipment_list():
    q = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    db = SessionLocal()
    try:
        # ✅ preload images ด้วย joinedload
        query = db.query(Equipment).options(joinedload(Equipment.images))

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


# 📄 หน้าแสดงรายละเอียดอุปกรณ์
@inventory_bp.route("/admin/equipments/<int:eid>", methods=["GET"], endpoint="admin_equipment_detail")
def admin_equipment_detail(eid):
    db = SessionLocal()
    try:
        item = (
            db.query(Equipment)
              .options(joinedload(Equipment.images))
              .filter(Equipment.equipment_id == eid)   # ✅ ต้อง filter ด้วย eid
              .first()
        )
        if not item:
            abort(404)
        return render_template("pages_inventory/admin_equipment_detail.html", item=item)
    finally:
        db.close()


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

        # 📌 รับไฟล์จากฟอร์มเพียงครั้งเดียว
        img = request.files.get("image")
        current_app.logger.info("UPLOAD_FOLDER = %s", current_app.config['UPLOAD_FOLDER'])
        current_app.logger.info("IMAGE FIELD = %s", img.filename if img else None)

        # 📌 แปลงวันที่
        buy_date = None
        if buy_date_raw:
            try:
                buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
            except ValueError:
                buy_date = None

        # 📌 ตรวจค่าที่จำเป็น
        if not name or not code:
            flash("กรุณากรอกชื่ออุปกรณ์และรหัส/หมายเลข", "error")
            return render_template("pages_inventory/admin_equipment_new.html")

        # 📌 ตรวจสอบชนิดไฟล์ถ้ามีอัปโหลด
        if img and img.filename:
            allowed = current_app.config.get("ALLOWED_IMAGE_EXT", {"jpg","jpeg","png","gif","webp"})
            if "." not in img.filename or img.filename.rsplit(".", 1)[1].lower() not in allowed:
                flash("อนุญาตเฉพาะไฟล์ภาพ jpg, jpeg, png, gif, webp", "error")
                return render_template("pages_inventory/admin_equipment_new.html")

        db = SessionLocal()
        try:
            # 📌 1) สร้างอุปกรณ์ใหม่
            now = datetime.utcnow()
            new_equipment = Equipment(
                name=name,
                code=code,
                category=category,
                detail=detail,
                brand=brand,
                buy_date=buy_date,
                status=status or "available",
                created_at=now,            )
            db.add(new_equipment)
            db.commit()
            db.refresh(new_equipment)

            # 📌 2) ถ้ามีไฟล์ → เซฟและบันทึก path
            if img and img.filename:
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)

                save_path = os.path.join(upload_dir, fname)
                img.save(save_path)
                current_app.logger.info("SAVE DST = %s", save_path)
                current_app.logger.info("FILE EXISTS = %s", os.path.exists(save_path))

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

    # GET
    return render_template("pages_inventory/admin_equipment_new.html")


@inventory_bp.route("/admin/equipments/<int:eid>/edit", methods=["GET", "POST"], endpoint="admin_equipment_edit")
def admin_equipment_edit(eid):
    db = SessionLocal()
    try:
        item = (
            db.query(Equipment)
              .options(joinedload(Equipment.images))
              .filter(Equipment.equipment_id == eid)   # ✅ ต้อง filter ด้วย eid
              .first()
        )
        if not item:
            abort(404)

        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            code = (request.form.get("code") or "").strip()
            category = (request.form.get("category") or "").strip()
            detail = (request.form.get("detail") or "").strip()
            brand = (request.form.get("brand") or "").strip()
            status = (request.form.get("status") or "").strip()
            buy_date_raw = (request.form.get("buy_date") or "").strip()

            # ✅ แปลงวันที่
            buy_date = None
            if buy_date_raw:
                try:
                    buy_date = datetime.strptime(buy_date_raw, "%Y-%m-%d").date()
                except ValueError:
                    buy_date = None

            # ✅ ถ้าไม่ได้กรอก name/code → flash และอยู่หน้าเดิม
            if not name or not code:
                flash("กรุณากรอกชื่ออุปกรณ์และรหัส/หมายเลข", "error")
                return render_template("pages_inventory/admin_equipment_edit.html", item=item)

            # ✅ อัปเดตค่าลง DB
            item.name = name
            item.code = code
            item.category = category
            item.detail = detail
            item.brand = brand
            item.buy_date = buy_date
            item.status = status or item.status

            # ✅ ถ้าอัปโหลดรูปใหม่
            img = request.files.get("image")
            if img and img.filename:
                allowed = current_app.config.get("ALLOWED_IMAGE_EXT", {"jpg","jpeg","png","gif","webp"})
                if "." not in img.filename or img.filename.rsplit(".",1)[1].lower() not in allowed:
                    flash("อนุญาตเฉพาะไฟล์ภาพ jpg, jpeg, png, gif, webp", "error")
                    return render_template("pages_inventory/admin_equipment_edit.html", item=item)

                # ✅ ลบรูปเก่าทั้งหมด (ไฟล์ + เรคคอร์ด DB)
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

                db.flush()  # ล้างข้อมูลเก่าก่อนเพิ่มใหม่

                # ✅ เซฟไฟล์ใหม่
                ext = secure_filename(img.filename).rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                img.save(os.path.join(upload_dir, fname))

                # ✅ เพิ่มเรคคอร์ดรูปใหม่
                new_img = EquipmentImage(
                    equipment_id=item.equipment_id,
                    image_path=f"uploads/equipment/{fname}",
                    created_at=datetime.utcnow()
                )
                db.add(new_img)

            # ✅ อัปเดตเวลาเพื่อกันแคช
            db.commit()
            flash("บันทึกการแก้ไขแล้ว", "success")
            return redirect(url_for("inventory.admin_equipment_list"))

        # GET → แสดงฟอร์ม
        return render_template("pages_inventory/admin_equipment_edit.html", item=item)
    finally:
        db.close()


@inventory_bp.route('/equipments/return', methods=['GET'])
def return_item_form():
    """แสดงหน้าฟอร์มสำหรับการคืนอุปกรณ์"""
    # ในหน้า form นี้ ควรจะมีช่องให้กรอก 'รหัสอุปกรณ์' หรือ 'รหัสการยืม' 
    # เพื่อใช้ในการค้นหาและประมวลผลการคืน
    return render_template('pages_inventory/admin_return_item.html')


@inventory_bp.route('/equipments/return', methods=['POST'])
def return_item_submit():
    """ประมวลผลการคืนอุปกรณ์"""
    
    # 1. ดึงข้อมูลจากฟอร์ม (สมมติว่ารับ 'code' ของอุปกรณ์ หรือ 'borrow_id')
    equipment_code = (request.form.get("code") or "").strip()
    
    if not equipment_code:
        flash("กรุณากรอกรหัส/หมายเลขอุปกรณ์ที่ต้องการคืน", "error")
        return redirect(url_for('inventory.return_item_form'))

    db = SessionLocal()
    try:
        # 2. ค้นหาอุปกรณ์ด้วยรหัส/หมายเลข
        equipment = (
            db.query(Equipment)
              .filter(Equipment.code == equipment_code)
              .first()
        )
        
        if not equipment:
            flash(f"ไม่พบอุปกรณ์ด้วยรหัส/หมายเลข: {equipment_code}", "error")
            return redirect(url_for('inventory.return_item_form'))

        # 3. ตรวจสอบสถานะว่าสามารถคืนได้หรือไม่ (สมมติว่า 'on_loan' คือสถานะที่ยืมอยู่)
        if equipment.status != 'on_loan':
            flash(f"อุปกรณ์ '{equipment.name}' รหัส {equipment_code} ไม่ได้อยู่ในสถานะยืม", "error")
            # ถ้ามีระบบยืม/คืนที่ซับซ้อนกว่านี้ (เช่น มีตาราง BorrowRecord)
            # ควรจะตรวจสอบจากตารางนั้นว่ามีการยืมที่ยังไม่คืนหรือไม่
            return redirect(url_for('inventory.return_item_form'))

        # 4. อัปเดตสถานะอุปกรณ์ (หลักการเบื้องต้นของการคืนคือเปลี่ยน status กลับเป็น 'available')
        equipment.status = 'available'
        
        # 5. อัปเดตเวลาการแก้ไข (optional)
        # equipment.updated_at = datetime.utcnow()
        
        # 6. (สำหรับระบบที่ซับซ้อน) ถ้ามีตาราง BorrowRecord
        # ควรจะอัปเดตเรคคอร์ดการยืมที่เกี่ยวข้อง ให้มีเวลา 'return_date'
        # latest_borrow_record = db.query(BorrowRecord).filter(...).first()
        # latest_borrow_record.return_date = datetime.utcnow()
        # db.add(latest_borrow_record) 
        
        db.commit()
        flash(f"คืนอุปกรณ์ '{equipment.name}' รหัส {equipment_code} เรียบร้อยแล้ว", "success")
        return redirect(url_for('inventory.lend_device')) # หรือไปหน้าหลัก/หน้ารายการอุปกรณ์

    except Exception as e:
        db.rollback()
        current_app.logger.error("Return item failed: %s", e)
        flash("เกิดข้อผิดพลาดในการคืนอุปกรณ์ กรุณาลองใหม่อีกครั้ง", "error")
        return redirect(url_for('inventory.return_item_form'))
    finally:
        db.close()

@inventory_bp.route("/user/return/<int:borrow_id>", methods=["POST"])
def user_submit_return(borrow_id):
    db = SessionLocal()
    try:
        return_service = ReturnItemService(db)
        # ... สมมติว่า user_id ถูกดึงมาจาก session หรือ token ...
        
        updated_record, message = return_service.user_request_return(borrow_id)

        if updated_record:
            flash(message, "success")
        else:
            flash(message, "error")
            
        return redirect(url_for("...")) # หน้าแสดงรายการยืมของผู้ใช้
    finally:
        db.close()

# ...
@inventory_bp.route("/admin/confirm_return/<int:borrow_id>", methods=["POST"])
def admin_confirm_return_item(borrow_id):
    db = SessionLocal()
    try:
        return_service = ReturnItemService(db)
        # ... สมมติว่า admin_id ถูกดึงมาจาก session ...
        admin_id = 1 # แทนที่ด้วย ID จริงของ Admin ที่ล็อกอินอยู่

        updated_record, message = return_service.admin_confirm_return(borrow_id, admin_id)

        if updated_record:
            flash(message, "success")
        else:
            flash(message, "error")
            
        return redirect(url_for("...")) # หน้าแสดงรายการรอการยืนยันของ Admin
    finally:
        db.close()

@inventory_bp.route("/admin/returns/pending")
def admin_pending_returns():
    db = SessionLocal()
    try:
        return_service = ReturnItemService(db)
        pending_records = return_service.get_pending_returns_list()
        # ส่งรายการที่รอดำเนินการไปให้ template
        return render_template("pages_inventory/admin_return_item.html", pending_records=pending_records)
    finally:
        db.close()