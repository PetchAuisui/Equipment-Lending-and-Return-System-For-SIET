from flask import render_template, request, jsonify, current_app
from . import auth_bp
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService



def _svc() -> AuthService:
    # ผูก repo กับ path ใน config
    data_dir = current_app.config["DATA_DIR"]
    repo = UserRepository(f"{data_dir}/users.json")
    return AuthService(repo)

# หน้าเว็บสมัคร (GET)
@auth_bp.get("/register")
def register_page():
    return render_template("auth/register.html")

# สมัครผ่านฟอร์มหรือ JSON (POST)
@auth_bp.post("/register")
def register_action():
    # รองรับทั้ง form-urlencoded และ JSON
    payload = request.get_json(silent=True) or request.form.to_dict()

    svc = _svc()
    err = svc.validate_register(payload)
    if err:
        # ถ้าเป็นฟอร์ม: render กลับหน้าเดิม; ถ้าเป็น JSON: คืน 400
        if request.is_json:
            return jsonify({"error": err}), 400
        return render_template("auth/register.html", error=err, old=payload), 400

    user = svc.register(payload)

    if request.is_json:
        return jsonify({"user": user.public_dict()}), 201

    # ถ้าเป็นฟอร์ม: แสดงผลลัพธ์ง่าย ๆ (ปรับเป็น redirect ได้)
    return render_template("auth/register.html", success=True, user=user.public_dict()), 201


@auth_bp.get("/login")
def login_page():
    # หน้าเปล่า ๆ ไว้ก่อน หรือใส่ฟอร์มจริงก็ได้
    return render_template("auth/login.html")
