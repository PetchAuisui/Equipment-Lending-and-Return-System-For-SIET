# app/utils/decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("is_authenticated"):
            flash("กรุณาเข้าสู่ระบบก่อน", "error")
            return redirect(url_for("auth.login_page", next=request.path))
        return view(*args, **kwargs)
    return wrapper

def role_required(*allowed_roles):
    """ใช้ @role_required('staff') หรือหลายบทบาท @role_required('admin','staff')"""
    def deco(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not session.get("is_authenticated"):
                flash("กรุณาเข้าสู่ระบบก่อน", "error")
                return redirect(url_for("auth.login_page", next=request.path))
            role = session.get("role", "member")
            if allowed_roles and role not in allowed_roles:
                flash("คุณไม่มีสิทธิ์เข้าถึงหน้านี้", "error")
                return redirect(url_for("pages.home"))
            return view(*args, **kwargs)
        return wrapper
    return deco

def staff_required(view):
    return role_required("staff")(view)
