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
        # Minimal server-side: collect some fields (could be expanded to save to DB later)
        fullname = request.form.get('full_name')
        phone = request.form.get('phone')
        device = request.form.get('device')
        # Flash a success message and redirect back to the form (could redirect to a thank-you page)
        flash('แบบแจ้งความถูกส่งเรียบร้อย', 'success')
        return redirect(url_for('pages.lost_report'))

    return render_template('pages/lost.html')