from flask import render_template
from . import tracking_bp

@tracking_bp.get("/")
def track_index():
    return render_template("tracking/index.html")
