"""
app/database/db.py
-------------------------------------
ไฟล์นี้เชื่อมระบบ Session ของ SQLAlchemy กับ Flask SQLAlchemy
โดยใช้ instance `db` จาก app/__init__.py เพื่อหลีกเลี่ยงการซ้ำซ้อน
-------------------------------------
"""

from sqlalchemy.orm import sessionmaker, scoped_session
from app import db

# ✅ ใช้ engine ตัวเดียวกับ Flask SQLAlchemy
engine = db.engine

# ✅ สร้าง SessionLocal ที่ใช้ร่วมกับ Flask
SessionLocal = scoped_session(
    sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )
)

# ✅ ให้ import Base จาก db.Model ได้ (เหมือนเดิม)
Base = db.Model


def get_db_session():
    """
    คืนค่า session ใหม่จาก SessionLocal
    (ควรใช้กับ context manager เช่น `with get_db_session() as session:`)
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
