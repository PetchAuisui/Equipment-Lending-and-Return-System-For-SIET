from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config.from_object(Config)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super-secret-key-change-this")

    # ✅ เพิ่ม URI เพื่อให้ Flask ใช้ SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ✅ Upload config
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads', 'equipment')
    app.config['ALLOWED_IMAGE_EXT'] = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ✅ เชื่อม db
    db.init_app(app)

    # ✅ Register blueprints
    from app.blueprints.inventory.api_equipment import api_equipment_bp
    from app.blueprints.pages import pages_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.tracking import tracking_bp
    from app.blueprints.admin.routes import admin_bp, admin_users_bp, admin_history_bp
    from app.blueprints.pages.routes import pages_bp
    from app.blueprints.history.routes import history_bp

    app.register_blueprint(api_equipment_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_history_bp)

    return app
