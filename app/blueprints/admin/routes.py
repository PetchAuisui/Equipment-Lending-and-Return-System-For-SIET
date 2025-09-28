from flask import Blueprint, render_template

# ----- /admin (dashboard) -----
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/")
def admin_home():
    return render_template("pages_admin/home_admin.html")


# ----- /admin/users (จัดการสมาชิก) -----
admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")

@admin_users_bp.get("/", endpoint="index")
def users_index():
    return render_template("pages_admin/user.html")
