from flask import render_template
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService

@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()
    return render_template("tracking/trackstatus.html", rents=rents)
