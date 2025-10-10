from flask import Blueprint, jsonify, session, Response, request
from app.db.db import SessionLocal
from app.models.notification import Notification
from app.models.equipment import Equipment
from app.services.overdue_checker import check_overdue_rents   
from datetime import datetime
import json

overdue_bp = Blueprint("overdue", __name__, url_prefix="/overdue")

TEMPLATES = {
    "due_soon": {
        "title": "อุปกรณ์ใกล้ครบกำหนดคืน",
        "fmt":   "กรุณานำ {name} มาคืนก่อน 18:00 น. (กำหนด {due})",
        "level": "warning", "icon": "ri-time-line",
    },
    "due_very_soon": {
        "title": "ครบกำหนดในอีกไม่ถึง 30 นาที",
        "fmt":   "กรุณารีบนำ {name} มาคืน (กำหนด {due})",
        "level": "warning", "icon": "ri-alarm-warning-line",
    },
    "overdue_notice": {
        "title": "อุปกรณ์ยังไม่คืน",
        "fmt":   "คุณมี {name} ยังไม่คืน (ครบกำหนด {due}) กรุณาคืนวันถัดไปและชำระค่าปรับ",
        "level": "danger",  "icon": "ri-error-warning-line",
    },
}

def _render_notif(n, db):
    # 1) แปลง payload ให้เป็น dict เสมอ (กันกรณีเป็นสตริง JSON)
    p = n.payload or {}
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except Exception:
            p = {}

    # 2) หา equipment_id / name ให้ได้ชื่อแน่ ๆ
    eid = p.get("equipment_id")
    name = p.get("equipment_name")
    if not name and eid:
        # ดึงชื่อจากตารางถ้ายังไม่มีใน payload
        name = db.query(Equipment.name).filter(Equipment.equipment_id == eid).scalar()
    if not name:
        name = f"อุปกรณ์ #{eid or '-'}"

    # 3) รูปแบบวันที่ครบกำหนด (รับทั้ง ISO string และ plain string)
    due_raw = p.get("due_date")
    due_fmt = "-"
    if due_raw:
        try:
            # รองรับ "YYYY-MM-DD HH:MM" หรือ ISO "YYYY-MM-DDTHH:MM:SS"
            due_dt = datetime.fromisoformat(due_raw.replace("T", " "))
            due_fmt = due_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            due_fmt = due_raw  # ถ้า parse ไม่ได้ ใช้ตามเดิม

    # 4) เรนเดอร์ข้อความตามเทมเพลต
    tpl = TEMPLATES.get(
        n.template,
        {"title": "การแจ้งเตือน", "fmt": "{name} (กำหนด {due})", "level": "info", "icon": "ri-information-line"},
    )
    text = tpl["fmt"].format(name=name, due=due_fmt)

    # 5) ส่งข้อมูลที่หน้าเว็บใช้ได้เลย
    return {
        "id": n.notification_id,
        "template": n.template,
        "status": n.status,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        "title": tpl["title"],
        "text": text,
        "level": tpl["level"],
        "icon": tpl["icon"],
    }

@overdue_bp.route("/get-notifications")
def get_notifications():
    """
    ✅ Endpoint สำหรับดึงรายการแจ้งเตือน
    - GET /overdue/get-notifications
    - ถ้าใส่ ?all=1 → จะได้ "ทั้งหมด (read + unread)"
    - ไม่ใส่ → จะได้เฉพาะ unread
    👉 ถ้าเพื่อนอยากทำหน้า "ประวัติแจ้งเตือน" ให้ใช้ ?all=1
    """
    if not session.get("is_authenticated"):
        return Response(json.dumps({"error":"กรุณาเข้าสู่ระบบก่อน"}, ensure_ascii=False),
                        content_type="application/json", status=401)

    user_id = session.get("user_id")
    show_all = request.args.get("all") in ("1","true","yes")
    db = SessionLocal()
    try:
        q = db.query(Notification).filter(Notification.user_id == user_id)
        if not show_all:
            q = q.filter(Notification.status == "unread")
        rows = q.order_by(Notification.created_at.desc()).all()
        out = [_render_notif(n, db) for n in rows]
        return Response(json.dumps(out, ensure_ascii=False), content_type="application/json")
    finally:
        db.close()

@overdue_bp.route("/run-check")
def run_overdue_check():
    """เรียกสร้างการแจ้งเตือนด้วยมือ (ใช้ทดสอบได้)"""
    msg = check_overdue_rents()
    return Response(msg, mimetype="text/plain")


@overdue_bp.route("/mark-read/<int:notif_id>", methods=["POST"])
def mark_read(notif_id):
    """
    ✅ Endpoint สำหรับเปลี่ยนสถานะแจ้งเตือนเป็น 'read'
    - ใช้กับปุ่มกดปิดแจ้งเตือน (X)
    """

    """อัปเดตแจ้งเตือนเป็น read (ใช้กับปุ่ม X ใน UI)"""
    if not session.get("is_authenticated"):
        return jsonify({"error": "กรุณาเข้าสู่ระบบก่อน"}), 401

    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(
            Notification.notification_id == notif_id,
            Notification.user_id == session.get("user_id")
        ).first()
        if not notif:
            return jsonify({"error": "ไม่พบการแจ้งเตือน"}), 404

        notif.status = "read"
        db.commit()
        return jsonify({"message": "ปิดแจ้งเตือนเรียบร้อยแล้ว"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"server error: {e}"}), 500
    finally:
        db.close()

