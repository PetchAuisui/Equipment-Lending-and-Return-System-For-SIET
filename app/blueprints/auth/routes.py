from flask import render_template, request, jsonify, current_app, redirect, url_for, flash
from . import auth_bp
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
import os


def _svc() -> AuthService:
    # ใช้ instance เป็นค่าเริ่มต้นหากไม่ได้ตั้ง DATA_DIR และสร้างโฟลเดอร์ให้ด้วย
    data_dir = current_app.config.get("DATA_DIR", "instance")
    os.makedirs(data_dir, exist_ok=True)
    repo = UserRepository(os.path.join(data_dir, "users.json"))
    return AuthService(repo)


# หน้าเว็บสมัคร (GET)
@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")


# สมัครผ่านฟอร์มหรือ JSON (POST)
@auth_bp.post("/register")
def register_action():
    """
    รองรับสองแบบ:
    - HTML form: Content-Type = application/x-www-form-urlencoded
    - JSON API : Content-Type = application/json
    แก้ปัญหา JSONDecodeError โดยไม่พยายาม parse JSON ถ้าไม่ใช่ JSON จริง
    """
    if request.is_json:  # เฉพาะเมื่อ header บอกว่าเป็น JSON เท่านั้นถึงจะอ่าน JSON
        payload = request.get_json(silent=True) or {}
    else:
        payload = request.form.to_dict() or {}

    # debug ไว้ตรวจดู payload เวลาเจอปัญหา
    current_app.logger.debug("register payload: %r", payload)

    svc = _svc()
    err = svc.validate_register(payload)
    if err:
        if request.is_json:
            return jsonify({"error": err}), 400
        # ส่งค่าเก่ากลับไปเติมในฟอร์ม
        return render_template("auth/register.html", error=err, old=payload), 400

    user = svc.register(payload)

    if request.is_json:
        # โหมด API → 201 Created
        return jsonify({"user": user.public_dict()}), 201

    # โหมดฟอร์ม → แสดง overlay ติ๊กถูกบนหน้าเดิม
    # (ใน register.html ให้มีโค้ดเปิด overlay เมื่อ success=True)
    return render_template("auth/register.html", success=True, user=user.public_dict()), 200
    # หากต้องการ PRG (Redirect หลังสำเร็จ):
    # flash("สมัครสมาชิกสำเร็จ! โปรดเข้าสู่ระบบ", "success")
    # return redirect(url_for("auth.login_page"), code=303)


@auth_bp.get("/login")
def login_page():
    return render_template("auth/login.html")
