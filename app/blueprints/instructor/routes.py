# app/blueprints/instructor/routes.py
from flask import Blueprint
from app.blueprints.instructor.views import (
    InstructorRequestsView,
    InstructorPendingView,
    InstructorPendingDecideView,
    RequestDetailView,
)

instructor_bp = Blueprint("instructor", __name__, url_prefix="/instructor")

# GET
instructor_bp.add_url_rule("/requests",
    view_func=InstructorRequestsView.as_view("requests"))
instructor_bp.add_url_rule("/pending",
    view_func=InstructorPendingView.as_view("pending"))
instructor_bp.add_url_rule("/requests/<int:req_id>",
    view_func=RequestDetailView.as_view("request_detail"))

# POST
instructor_bp.add_url_rule(
    "/pending/decide/<int:req_id>",
    view_func=InstructorPendingDecideView.as_view("pending_decide"),
    methods=["POST"],
)

# --- alias เพื่อความเข้ากันย้อนหลัง ---
bp = instructor_bp
