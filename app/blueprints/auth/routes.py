from flask import render_template
from . import auth_bp

@auth_bp.get("/login")
def login_page():
    return render_template("auth/login.html")

@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")
    