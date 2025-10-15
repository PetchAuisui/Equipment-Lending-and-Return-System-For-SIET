import os
from flask import Flask
from .config import Config
from app.blueprints.inventory.api_equipment import api_equipment_bp
from app.scheduler import start_notification_scheduler 
from app.db.db import Base, engine
from app.db import models




def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super-secret-key-change-this")

    app.config.from_object(Config)
    app.register_blueprint(api_equipment_bp)

    # ===== Upload config (สำคัญสำหรับให้รูป “มา”) =====
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'equipment')
    app.config['ALLOWED_IMAGE_EXT'] = {'jpg','jpeg','png','gif','webp'}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Run small idempotent DB migrations (add equipment_name column if missing)
    try:
        from app.db.migrations import ensure_equipment_name_column
        added = ensure_equipment_name_column(backfill=True)
        if added:
            app.logger.info('DB migration: added equipment_name column to item_brokes')
    except Exception as e:
        # Do not prevent the app from starting; admin route will show a flash
        app.logger.warning(f'Could not run DB migration for equipment_name: {e}')

    # ===== Register blueprints =====
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from .blueprints.instructor import instructor_bp  
    from app.blueprints.admin.routes import admin_bp, admin_users_bp, admin_history_bp                  # root: "/"
    from app.blueprints.pages.routes import pages_bp
    from app.blueprints.history.routes import history_bp                 # root: "/"
    from .blueprints.notifications import notifications_bp



    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp,)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp, url_prefix="/instructor")   
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_history_bp)
    app.register_blueprint(notifications_bp)


    
    # ===== 🔔 เริ่ม Scheduler สำหรับแจ้งเตือน =====
    start_notification_scheduler(app)
    return app

