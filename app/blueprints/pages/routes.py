# app/blueprints/pages/routes.py
from . import pages_bp  
from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import current_user
from app.services.home_service import HomeService
from app.services.item_broke_service import ItemBrokeService

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
    # recent lost reports to show on home (no actions, just info)
    recent_lost = svc.get_recent_lost_reports(limit=4)

    return render_template("pages/home.html",
                           top_borrowed=top_borrowed,
                           outstanding=outstanding,
                           recent_lost=recent_lost)

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
        # collect fields and files
        form = request.form
        report_type = (form.get('report_type') or 'lost')
        rent_id = form.get('rent_id')
        detail = form.get('detail') or ''
        images = request.files.getlist('images')

        # persist via service
        ibs = ItemBrokeService()
        device_name = form.get('device') or form.get('equipment_name')
        try:
            item_id = ibs.create_report(rent_id=int(rent_id) if rent_id else None,
                                        type=report_type,
                                        detail=detail,
                                        images=images,
                                        equipment_name=device_name)
            flash('แบบแจ้งความถูกส่งเรียบร้อย', 'success')
        except Exception as e:
            # log/flash and redirect back with error
            flash('เกิดข้อผิดพลาดในการบันทึกข้อมูล โปรดลองอีกครั้ง', 'error')
            return redirect(url_for('pages.lost_report'))

        # redirect to confirmation
        return redirect(url_for('pages.lost_sent'))

    # allow callers to prefill some fields via query string (rent_id, equipment_name, equipment_code)
    rent_id = request.args.get('rent_id')
    equipment_name = request.args.get('equipment_name')
    equipment_code = request.args.get('equipment_code')
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
