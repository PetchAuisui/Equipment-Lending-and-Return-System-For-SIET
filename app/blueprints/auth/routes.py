from flask import render_template, request, jsonify, current_app
from . import auth_bp
from app.services.auth_service import AuthService

# ใช้ repo แบบ DB
from app.repositories.user_repository import UserRepository
from app.db.db import SessionLocal

def _svc() -> AuthService:
    repo = UserRepository(SessionLocal())
    return AuthService(repo)

# ── Register ─────────────────────────────────────────────
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

    user = svc.register(payload)

    if request.is_json:
        return jsonify({"user": user.public_dict()}), 201

    return render_template("auth/register.html", success=True, user=user.public_dict()), 200

# ── Login (เพิ่ม endpoint ให้ตรงกับที่ template เรียก) ──
@auth_bp.get("/login", endpoint="login_page")
def login_page():
    return render_template("auth/login.html")
