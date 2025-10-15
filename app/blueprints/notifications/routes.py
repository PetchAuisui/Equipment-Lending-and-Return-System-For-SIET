from flask import Blueprint, jsonify, session
from app.db.db import SessionLocal
from app.db.models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.get("/unread")
def get_unread_notifications():
    """📩 ดึงเฉพาะแจ้งเตือนที่ยังไม่อ่านของผู้ใช้ปัจจุบัน"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    db = SessionLocal()
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .filter(Notification.status == "unread")
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "id": n.notification_id,
            "template": n.template,
            "message": n.payload.get("message") if isinstance(n.payload, dict) else n.payload,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for n in notifs
    ]
    db.close()
    return jsonify(result)


@notifications_bp.post("/dismiss/<int:notif_id>")
def dismiss_notification(notif_id):
    """❌ ปิดแจ้งเตือน (เปลี่ยนสถานะเป็น 'read')"""
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.notification_id == notif_id).first()
        if notif:
            notif.status = "read"
            db.commit()
            return jsonify({"ok": True})
        return jsonify({"error": "Notification not found"}), 404
    except Exception as e:
        db.rollback()
        print(f"[ERROR dismiss_notification] {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

