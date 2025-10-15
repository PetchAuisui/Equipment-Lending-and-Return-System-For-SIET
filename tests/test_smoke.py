# tests/test_app_startup.py
from app import create_app

def test_app_can_start():
    """ทดสอบว่า Flask app สามารถสร้าง instance ได้"""
    app = create_app()
    assert app is not None
    assert app.name == "app"  # หรือชื่อจริงของโมดูลคุณ

def test_app_has_routes():
    """ตรวจสอบว่ามี route สำคัญอยู่จริง"""
    app = create_app()
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/" in routes  # หน้าหลัก