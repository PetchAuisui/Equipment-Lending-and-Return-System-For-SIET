import os
from flask import Flask
from flask_apscheduler import APScheduler  
from .config import Config
from app.blueprints.inventory.api_equipment import api_equipment_bp
from app.services.overdue_checker import check_overdue_rents  # ✅ import service ตรวจแจ้งเตือน
from app.blueprints.overdue.routes import overdue_bp

scheduler = APScheduler()  # ✅ สร้าง scheduler object

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.register_blueprint(api_equipment_bp)

    # ===== Upload config (สำคัญสำหรับให้รูป “มา”) =====
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'equipment')
    app.config['ALLOWED_IMAGE_EXT'] = {'jpg','jpeg','png','gif','webp'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ===== Register blueprints =====
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from .blueprints.admin import admin_users_bp
    from .blueprints.admin import admin_bp                     # root: "/"

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(overdue_bp)

    # ===== Scheduler สำหรับตรวจสอบการยืมที่เลยกำหนด =====
    app.config['SCHEDULER_TIMEZONE'] = 'Asia/Bangkok'
    app.config['SCHEDULER_JOB_DEFAULTS'] = {
        'max_instances': 1,
        'coalesce': True,
        'misfire_grace_time': 60,
    }

    scheduler.init_app(app)

    def start_jobs():
        # กันซ้ำเวลา reload
        if scheduler.get_job("check_overdue_interval"):
            return

        # ✅ รันใน app_context เสมอ (กันปัญหา context/extension)
        def run_check():
            with app.app_context():
                msg = check_overdue_rents()
                print(f"[APScheduler] {msg}")

        # ทดสอบให้ถี่ก่อน แล้วค่อยปรับเป็น 30 นาทีทีหลัง
        scheduler.add_job(
            id="check_overdue_interval",
            func=run_check,
            trigger="interval",
            minutes=1,           
            replace_existing=True,
        )
        scheduler.start()

    # ✅ กันรันสองรอบตอน debug reloader
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_jobs()

    return app