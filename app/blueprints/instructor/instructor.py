# app/blueprints/instructor/instructor.py
from flask import Blueprint, render_template, url_for

bp = Blueprint("instructor", __name__)

@bp.get("/home")
def teacher_home():
    # --- demo data สำหรับหน้า home ของอาจารย์ ---
    announcements = [
        {"title": "แจ้งปิดปรับปรุงระบบ", "summary": "คืนวันเสาร์ 02:00–03:00", "url": "#"},
        {"title": "เพิ่มอุปกรณ์ใหม่", "summary": "ไมค์ + กล้อง WebCam พร้อมให้ยืม", "url": "#"},
    ]
    shortcuts = [
        {"label": "คำขอรออนุมัติ", "href": url_for("instructor.pending")},
        {"label": "รายการกำลังยืม (Coming Soon)", "href": "#"},
    ]
    popular = [
        {"name": "Laptop", "usage_count": 65},
        {"name": "Power strip", "usage_count": 64},
    ]
    return render_template(
        "instructor/home.html",
        announcements=announcements,
        shortcuts=shortcuts,
        popular=popular,
    )

@bp.get("/pending")
def pending():
    demo_reqs = [
        {"id": 1, "student": "สมชาย", "equipment": "กล้อง DSLR", "status": "PENDING"},
        {"id": 2, "student": "สมหญิง", "equipment": "โน้ตบุ๊ค", "status": "PENDING"},
    ]
    return render_template("instructor/pending.html", reqs=demo_reqs)