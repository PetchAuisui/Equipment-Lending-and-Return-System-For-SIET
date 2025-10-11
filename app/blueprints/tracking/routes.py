from flask import render_template
from . import tracking_bp
from app.services.trackstatus_service import TrackStatusService

@tracking_bp.get("/")
def track_index():
    service = TrackStatusService()
    rents = service.get_track_status_list()

    print("\n=== DEBUG TRACK STATUS ===")
    for r in rents:
        print(f"Rent ID: {r['rent_id']} | {r['equipment_name']} | {r['start_date']} → {r['due_date']}")
    print("==========================\n")

    return render_template("tracking/trackstatus.html", rents=rents)
