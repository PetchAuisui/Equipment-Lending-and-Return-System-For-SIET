from flask import render_template
from . import inventory_bp

@inventory_bp.get("/")
def equipment_index():
    return render_template("pages_inventory/lend_device.html")

@inventory_bp.get("/lend")
def lend():
    return render_template("pages_inventory/lend.html")

