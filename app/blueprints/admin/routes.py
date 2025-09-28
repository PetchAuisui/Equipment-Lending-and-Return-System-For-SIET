from flask import Blueprint, render_template

admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")


@admin_users_bp.get("/", endpoint="index")
def index():
    return render_template("pages_admin/user.html")
