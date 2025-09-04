from flask import render_template
from . import pages_bp

@pages_bp.get("/")
def home():
    return render_template("pages/home.html")

@pages_bp.get("/about")
def about_us():
    return render_template("pages/about_us.html")

@pages_bp.get("/policy")
def policy():
    return render_template("pages/policy.html")
