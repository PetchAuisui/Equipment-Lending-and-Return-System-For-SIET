from flask import session
from app.db.db import SessionLocal
from sqlalchemy import text

def get_current_user():
    """
    ดึงข้อมูลผู้ใช้ที่ล็อกอินอยู่ตอนนี้จาก session + database
    คืนค่าเป็น dict {user_id, name, email, role, ...}
    """
    if not session.get("is_authenticated"):
        return None

    identity = session.get("student_id") or session.get("employee_id")
    email = session.get("user_email")

    db = SessionLocal()
    try:
        # หา user จาก identity หรือ email
        row = db.execute(text("""
            SELECT user_id, name, email, student_id, employee_id, role, member_type
            FROM users
            WHERE (student_id = :id OR employee_id = :id OR email = :email)
            LIMIT 1
        """), {"id": identity, "email": email}).first()

        if not row:
            return None
        return dict(row._mapping)
    finally:
        db.close()


def get_current_user_id() -> int | None:
    """ดึง user_id ของผู้ใช้ที่ล็อกอิน"""
    user = get_current_user()
    return user["user_id"] if user else None


def get_current_user_role() -> str:
    """ดึง role ของผู้ใช้ที่ล็อกอิน ('member', 'staff', 'admin', ...)"""
    return session.get("role", "member")
