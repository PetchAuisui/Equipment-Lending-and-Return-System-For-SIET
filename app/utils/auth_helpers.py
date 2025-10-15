# app/db/auth_helpers.py
from __future__ import annotations
from typing import Optional, Dict
from flask import session
from sqlalchemy import text
from app.db.db import SessionLocal

class UserContext:
    """
    คลาสอ่านข้อมูลผู้ใช้จาก session + database
    ใช้แบบ: UserContext.get_current_user()
    """
    @staticmethod
    def get_current_user() -> Optional[Dict]:
        if not session.get("is_authenticated"):
            return None

        identity = session.get("student_id") or session.get("employee_id")
        email = session.get("user_email")

        db = SessionLocal()
        try:
            row = db.execute(text("""
                SELECT user_id, name, email, student_id, employee_id, role, member_type
                FROM users
                WHERE (student_id = :id OR employee_id = :id OR email = :email)
                LIMIT 1
            """), {"id": identity, "email": email}).first()

            return dict(row._mapping) if row else None
        finally:
            db.close()

    @staticmethod
    def get_current_user_id() -> Optional[int]:
        u = UserContext.get_current_user()
        return u["user_id"] if u else None

    @staticmethod
    def get_current_user_role() -> str:
        return session.get("role", "member")


# ---------- ฟังก์ชันเดิม (คงไว้เพื่อไม่ให้โค้ดที่เรียกอยู่พัง) ----------
def get_current_user():
    return UserContext.get_current_user()

def get_current_user_id() -> Optional[int]:
    return UserContext.get_current_user_id()

def get_current_user_role() -> str:
    return UserContext.get_current_user_role()
