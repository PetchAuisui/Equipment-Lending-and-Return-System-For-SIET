from __future__ import annotations
from functools import wraps
from flask import session, redirect, url_for, request, flash

class AuthGuard:
    @staticmethod
    def login_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("is_authenticated"):
                flash("Please log in first", "warning")
                return redirect(url_for("auth.login_page", next=request.path))
            return fn(*args, **kwargs)
        return wrapper

    @staticmethod
    def require_roles(*roles):
        def deco(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                if session.get("role", "member") not in roles:
                    return ("Forbidden", 403)
                return fn(*args, **kwargs)
            return wrapper
        return deco
