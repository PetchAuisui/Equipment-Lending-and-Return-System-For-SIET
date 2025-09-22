# app/blueprints/auth/routes.py

from flask import (
    render_template, request, jsonify,
    redirect, url_for, session, flash, current_app
)

from . import auth_bp
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.db.db import SessionLocal


# ---------- Service Factory ----------
def _svc() -> AuthService:
    return AuthService(UserRepository(SessionLocal()))


# ---------- Register ----------
@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_action():
    payload = request.get_json(silent=True) if request.is_json else (request.form.to_dict() or {})
    current_app.logger.debug("register payload: %r", payload)

    svc = _svc()
    err = svc.validate_register(payload)
    if err:
        if request.is_json:
            return jsonify({"error": err}), 400
        return render_template("auth/register.html", error=err, old=payload), 400

    user = svc.register(payload)  # บริการคืน dict พร้อมฟิลด์ผู้ใช้

    if request.is_json:
        return jsonify({"user": user}), 201

    return render_template("auth/register.html", success=True, user=user), 200


# ---------- Login ----------
@auth_bp.get("/login")
def login_page():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_action():
    raw = request.get_json(silent=True) or request.form.to_dict() or {}
    email = raw.get("email", "")
    password = raw.get("password", "")

    svc = _svc()
    ok, err, user = svc.login(email, password)

    # ---- JSON Mode ----
    if request.is_json:
        if not ok:
            return jsonify({"error": err}), 401
        return jsonify({
            "ok": True,
            "user": {
                "email": _get(user, "email"),
                "name": _get(user, "name"),
                "student_id": _get(user, "student_id"),
                "employee_id": _get(user, "employee_id"),
                "role": _get(user, "role", "member"),
                "member_type": _get(user, "member_type"),
            }
        }), 200

    # ---- Form Mode ----
    if not ok:
        return render_template("auth/login.html", error=err, old={"email": email}), 401

    # ---- เก็บ session ----
    student_id   = _get(user, "student_id")
    employee_id  = _get(user, "employee_id")

    session.update({
        "user_email": _get(user, "email"),
        "user_name": _get(user, "name") or email.split("@")[0],
        "student_id": student_id,
        "employee_id": employee_id,
        "role": _get(user, "role", "member"),          # เก็บ role (ไม่แสดง)
        "member_type": _get(user, "member_type"),      # เก็บ member_type (ไม่แสดง)
        "identity": student_id or employee_id,         # ใช้โชว์รหัสใน navbar
        "is_authenticated": True,
    })

    return redirect(url_for("pages.home"))


# ---------- Logout ----------
@auth_bp.get("/logout")
def logout_action():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("pages.home"))



@auth_bp.app_context_processor
def inject_current_user():
    return {
        "current_user": {
            "email": session.get("user_email"),
            "name": session.get("user_name"),
            "identity": session.get("identity"),  # โชว์แค่ identity (student_id / emp_id)
            "is_authenticated": session.get("is_authenticated", False),
        }
    }



def _get(obj, name: str, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)