from flask import render_template, request, redirect, url_for
from app.blueprints.inventory import inventory_bp
from app.services import lend_device_service
from app.db.db import SessionLocal
from app.models.equipment import Equipment
from datetime import datetime

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
    # ดึงข้อมูลจาก DB
    db = SessionLocal()
    items = db.query(Equipment).all()
    db.close()
    return render_template("pages_inventory/admin_equipment_list.html", items=items)

# ฟอร์มเพิ่มอุปกรณ์
@inventory_bp.route("/admin/equipments/new", methods=["GET", "POST"])
def admin_equipment_new():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        category = request.form.get("category")
        detail = request.form.get("detail")
        brand = request.form.get("brand")
        buy_date = request.form.get("buy_date")
        status = request.form.get("status")

        with SessionLocal() as db:
            equipment = Equipment(
                name=name,
                code=code,
                category=category,
                detail=detail,
                brand=brand,
                buy_date=buy_date,
                status=status,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(equipment)
            db.commit()

        return redirect(url_for("inventory.admin_equipment_list"))

    # ถ้า GET → แสดงหน้า form
    return render_template("pages_inventory/admin_equipment_new.html")