import os
from flask import Flask
from .config import Config
from app.blueprints.inventory.api_equipment import api_equipment_bp

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
    app.register_blueprint(inventory_bp,)
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)

    return app
