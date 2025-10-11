from flask import Blueprint, render_template, session
from flask_login import current_user
from app.services.home_service import HomeService

pages_bp = Blueprint("pages", __name__)
home_service = HomeService()

def _resolve_user_id():
    if getattr(current_user, "is_authenticated", False):
        return getattr(current_user, "user_id", None) or getattr(current_user, "id", None)
    return session.get("user_id")

@pages_bp.get("/")
def home():
    user_id = _resolve_user_id()

    top_borrowed = home_service.get_top_borrowed_items(limit=8)
    outstanding = home_service.get_outstanding_items_for_user(user_id, limit=10) if user_id else []

    return render_template(
        "pages/home.html",
        top_borrowed=top_borrowed,
        outstanding=outstanding,
    )


@pages_bp.get("/about")
def about_us():
    return render_template("pages/about_us.html")

@pages_bp.get("/policy")
def policy():
    return render_template("pages/policy.html")


