# app/blueprints/pages/routes.py
from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import current_user
from app.services.home_service import HomeService

pages_bp = Blueprint("pages", __name__)
svc = HomeService()

@pages_bp.get("/")
def home():
    # ดึง user_id แบบสั้น ๆ ครอบคลุม 3 แหล่ง
    user_id = (
        getattr(current_user, "user_id", None)
        or getattr(current_user, "id", None)
        or session.get("user_id")
    )

    # ยอดฮิตโชว์ 4 ชิ้นเท่านั้น (OOP: ไปจัดการต่อใน Service/Repository)
    top_borrowed = svc.get_top_borrowed_items(limit=4)
    # ของฉันที่ยังไม่คืน
    outstanding = svc.get_outstanding_items_for_user(user_id, limit=10) if user_id else []

    return render_template("pages/home.html",
                           top_borrowed=top_borrowed,
                           outstanding=outstanding)

@pages_bp.get("/about")
def about_us():
    return render_template("pages/about_us.html")

@pages_bp.get("/policy")
def policy():
    return render_template("pages/policy.html")

@pages_bp.route('/lost', methods=['GET', 'POST'])
def lost_report():
    """Simple lost/damaged report page. Currently POST only flashes and redirects back."""
    if request.method == 'POST':
        # Minimal server-side handling: could save to DB here
        # Keep behavior simple: flash and redirect to confirmation page
        flash('แบบแจ้งความถูกส่งเรียบร้อย', 'success')
        return redirect(url_for('pages.lost_sent'))

    # allow callers to prefill some fields via query string (rent_id, equipment_name, equipment_code)
    rent_id = request.args.get('rent_id')
    equipment_name = request.args.get('equipment_name')
    equipment_code = request.args.get('equipment_code')

    return render_template('pages/lost.html',
                           rent_id=rent_id,
                           equipment_name=equipment_name,
                           equipment_code=equipment_code)

@pages_bp.get('/lost/sent')
def lost_sent():
    """Confirmation page after sending lost report."""
    return render_template('pages/lost_sent.html')

@pages_bp.get("/history")
def history():
    return render_template("pages/history.html")
