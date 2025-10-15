from flask import Blueprint, render_template, jsonify, session
from app.controllers.admin_return_controller import AdminReturnController

admin_success_return_bp = Blueprint("admin_success_return", __name__)

@admin_success_return_bp.route("/admin/return")
def admin_return_page():
    rent_list = AdminReturnController.get_all_returns()
    return render_template("pages_inventory/admin_success_return.html", rent_list=rent_list)

@admin_success_return_bp.route("/admin/return/detail/<int:rent_id>")
def admin_return_detail(rent_id):
    rent_detail = AdminReturnController.get_return_detail(rent_id)
    if not rent_detail:
        return render_template("pages_inventory/return_detail.html", rent=None)
    return render_template("pages_inventory/return_detail.html", rent=rent_detail)

# ✅ API ยืนยันคืน
@admin_success_return_bp.route("/api/return/<int:rent_id>", methods=["POST"])
def api_confirm_return(rent_id):
    print("📦 API CONFIRM RETURN by user_id:", session.get("user_id"))
    result = AdminReturnController.confirm_return(rent_id)
    status_code = 200 if result["status"] == "success" else 404
    return jsonify(result), status_code
