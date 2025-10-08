# app/blueprints/overdue/routes.py
from flask import Blueprint, jsonify, session, Response
from app.db.db import SessionLocal
from app.models.notification import Notification
from app.services.overdue_checker import check_overdue_rents
import json

overdue_bp = Blueprint("overdue", __name__, url_prefix="/overdue")


@overdue_bp.route("/check")
def test_overdue():
    """ตรวจสอบการยืมที่เกินกำหนด และสร้างการแจ้งเตือน"""
    msg = check_overdue_rents()
    return Response(
        json.dumps({"message": msg}, ensure_ascii=False),
        content_type="application/json"
    )


@overdue_bp.route("/get-notifications")
def get_notifications():
    """ดึงการแจ้งเตือนของผู้ใช้ที่ล็อกอินอยู่"""
    if not session.get("is_authenticated"):
        return Response(
            json.dumps({"error": "กรุณาเข้าสู่ระบบก่อน"}, ensure_ascii=False),
            content_type="application/json",
            status=401
        )

    user_id = session.get("user_id")
    db = SessionLocal()

    notifs = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()

    result = [
        {
            "id": n.notification_id,
            "template": n.template,
            "status": n.status,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "payload": n.payload,
        }
        for n in notifs
    ]
    db.close()
    return Response(
        json.dumps(result, ensure_ascii=False),
        content_type="application/json"
    )
