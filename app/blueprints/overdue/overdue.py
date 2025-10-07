from flask import Blueprint, Response
import json

overdue_bp = Blueprint("overdue", __name__)

@overdue_bp.route("/overdue")
def overdue_alerts():
    alerts = [
        {"name": "ไมค์โครโฟน", "due_date": "2025-10-01"},
        {"name": "ขาตั้งกล้อง", "due_date": "2025-10-03"}
    ]
    data = {"count": len(alerts), "alerts": alerts}
    return Response(json.dumps(data, ensure_ascii=False), content_type="application/json; charset=utf-8")
