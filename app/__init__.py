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

    app.register_blueprint(pages_bp)                       # มี "/" ที่นี่
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(inventory_bp, url_prefix="/equipment")
    app.register_blueprint(tracking_bp, url_prefix="/track-status")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
