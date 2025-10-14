from flask import Blueprint, render_template, jsonify
from app.controllers.admin_return_controller import AdminReturnController

admin_success_return_bp = Blueprint("admin_success_return", __name__)

# ✅ แสดงหน้า HTML
@admin_success_return_bp.route("/admin/return")
def admin_return_page():
    rent_list = AdminReturnController.get_all_returns()
    return render_template("pages_inventory/admin_success_return.html", rent_list=rent_list)

# ✅ API สำหรับอัปเดตสถานะคืน
@admin_success_return_bp.route("/api/return/<int:rent_id>", methods=["POST"])
def api_confirm_return(rent_id):
    result = AdminReturnController.confirm_return(rent_id)
    status_code = 200 if result["status"] == "success" else 404
    return jsonify(result), status_code
