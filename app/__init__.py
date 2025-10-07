from flask import Flask
from .config import Config



def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Register blueprints
    from .blueprints.pages import pages_bp
    from .blueprints.auth import auth_bp
    from .blueprints.inventory import inventory_bp
    from .blueprints.tracking import tracking_bp
    from .blueprints.admin import admin_users_bp
    from .blueprints.admin import admin_bp
    from .blueprints.instructor import instructor_bp  

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp, url_prefix="/equipment")
    app.register_blueprint(tracking_bp, url_prefix="/track-status")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp, url_prefix="/instructor")   

    return app
