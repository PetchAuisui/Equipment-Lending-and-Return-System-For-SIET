# app/__init__.py
import os
from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix
from app.scheduler import start_notification_scheduler 
from .config import Config
from app.db.db import Base, engine

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ----- Core Config -----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key-change-this")
    app.config.from_object(Config)

    # ใช้งานหลัง reverse proxy (Railway) ให้ url_for/redirect ถูกโปรโตคอล/โฮสต์
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # ----- Uploads -----
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads", "equipment")
    app.config["ALLOWED_IMAGE_EXT"] = {"jpg", "jpeg", "png", "gif", "webp"}
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ----- Blueprints -----
    # (สำคัญ: ให้ package ของแต่ละ blueprint import routes ภายในเองแล้ว)
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from .blueprints.notifications import notifications_bp
    from app.blueprints.admin.routes import admin_bp, admin_users_bp, admin_history_bp
    from app.blueprints.history.routes import history_bp
    from app.blueprints.inventory.api_equipment import api_equipment_bp
    from app.blueprints.instructor.routes import instructor_bp
    from app.blueprints.inventory.admin_success_return import admin_success_return_bp
    


    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(api_equipment_bp)
    app.register_blueprint(instructor_bp)  
    app.register_blueprint(admin_success_return_bp)
    app.register_blueprint(notifications_bp)
    # ----- DB bootstrap -----
    with app.app_context():
        from app.db import models  # noqa: F401 (ensure tables discovered)
        with engine.begin() as conn:
            locked = False
            try:
                if engine.dialect.name == "postgresql":
                    conn.execute(text("SELECT pg_advisory_lock(987654321)"))
                    locked = True
                Base.metadata.create_all(bind=conn)
            finally:
                if locked:
                    conn.execute(text("SELECT pg_advisory_unlock(987654321)"))

    # ----- Health check -----
    @app.get("/health")
    def health():
        return jsonify(ok=True), 200

    # ----- Root redirect (เลือกหน้าที่มีอยู่จริง) -----
    @app.get("/")
    def _root():
        for endpoint in ("pages.home", "admin.admin_home", "inventory.lend", "tracking.track_index"):
            try:
                return redirect(url_for(endpoint))
            except Exception:
                continue
        return jsonify(status="ok", hint="No landing page found."), 200

    # ----- Fallback: สร้าง alias ให้ 'pages.home' เสมอ ถ้ายังไม่มี -----
    if "pages.home" not in app.view_functions:
        @app.get("/home", endpoint="pages.home")
        def _pages_home_alias():
            return redirect(url_for("_root"))
    
    # ===== 🔔 เริ่ม Scheduler สำหรับแจ้งเตือน =====
    start_notification_scheduler(app)

    return app
