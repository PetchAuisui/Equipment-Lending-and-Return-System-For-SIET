# app/blueprints/instructor/routes.py
from flask import Blueprint
from app.blueprints.instructor.views import (
    InstructorRequestsView,
    InstructorPendingView,
    InstructorPendingDecideView,
    RequestDetailView,
)

bp = Blueprint("instructor", __name__, url_prefix="/instructor")

# GET
bp.add_url_rule("/requests", view_func=InstructorRequestsView.as_view("requests"))
bp.add_url_rule("/pending", view_func=InstructorPendingView.as_view("pending"))
bp.add_url_rule("/requests/<int:req_id>", view_func=RequestDetailView.as_view("request_detail"))

# POST
bp.add_url_rule(
    "/pending/decide/<int:req_id>",
    view_func=InstructorPendingDecideView.as_view("pending_decide"),
    methods=["POST"],
)