from flask import render_template, request, jsonify, redirect, url_for, session
from . import auth_bp
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.db.db import SessionLocal

def _svc() -> AuthService:
    return AuthService(UserRepository(SessionLocal()))

# ---------- Register ----------
@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")

@auth_bp.post("/register")
def register_action():
    payload = request.get_json(silent=True) or request.form.to_dict() or {}

    svc = _svc()
    err = svc.validate_register(payload)
    if err:
        if request.is_json:
            return jsonify({"error": err}), 400
        return render_template("auth/register.html", error=err, old=payload), 400

    user = svc.register(payload)

    if request.is_json:
        return jsonify({"user": {"id": user["id"], "email": user["email"], "name": user["name"]}}), 201
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

    if request.is_json:
        if not ok:
            return jsonify({"error": err}), 401
        return jsonify({"ok": True, "user": {"email": user["email"], "name": user["name"]}}), 200

    if not ok:
        return render_template("auth/login.html", error=err, old={"email": email}), 401

    # เก็บ session แบบง่าย ๆ
    session["user_email"] = user["email"]
    session["user_name"]  = user["name"]
    # เปลี่ยนปลายทางตามที่ต้องการ
    return redirect(url_for("pages.home"))