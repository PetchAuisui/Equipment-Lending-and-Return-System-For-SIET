from __future__ import annotations
from flask import render_template, session, redirect, url_for, current_app

from . import history_bp
from app.db.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.history_repository import RentHistoryRepository
from app.services.history_service import BorrowHistoryService
from app.utils.decorators import login_required


def _user_repo(): return UserRepository(SessionLocal())
def _svc():       return BorrowHistoryService(RentHistoryRepository(SessionLocal()))


@history_bp.get("/history")
@login_required
def my_borrow_history():
    email = session.get("user_email")
    user = _user_repo().find_by_email(email)
    if not user:
        current_app.logger.warning("User not found for session email: %s", email)
        return redirect(url_for("auth.logout_action"))

    items = _svc().get_for_user(user["user_id"])
    return render_template("pages_history/my_history.html", items=items)

