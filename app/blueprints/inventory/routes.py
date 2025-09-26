from flask import render_template
from app.blueprints.inventory import inventory_bp
from app.services import lend_device_service

@inventory_bp.route('/lend_device')
def lend_device():
    # 📌 ดึงข้อมูลจาก service
    equipments = lend_device_service.get_equipment_list()
    
    # ✅ return template พร้อมส่งข้อมูลไปยัง HTML
    return render_template("pages_inventory/lend_device.html", equipments=equipments)


@inventory_bp.route('/lend')
def lend():
    return render_template("pages_inventory/lend.html")
