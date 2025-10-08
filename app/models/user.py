from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.db.db import Base


class User(Base):
    __tablename__ = "users"

    user_id      = Column(Integer, primary_key=True, autoincrement=True)
    student_id   = Column(String, unique=True, nullable=True)
    employee_id  = Column(String, unique=True, nullable=True)
    name         = Column(String, nullable=False)
    major        = Column(String, nullable=True)
    member_type  = Column(String, nullable=False)   # student | teacher | officer | staff
    phone        = Column(String, nullable=True)
    email        = Column(String, unique=True, nullable=False)
    gender       = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role         = Column(String, default="member", nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow)

    # ---- Helper methods ----
    def to_dict(self):
        """ใช้สำหรับ ORM → dict (รวม password_hash)"""
        return {
            "user_id": self.user_id,
            "student_id": self.student_id,
            "employee_id": self.employee_id,
            "name": self.name,
            "major": self.major,
            "member_type": self.member_type,
            "phone": self.phone,
            "email": self.email,
            "gender": self.gender,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def public_dict(self):
        """ส่งกลับฝั่ง UI (ไม่โชว์ password_hash)"""
        return {
            "user_id": self.user_id,
            "student_id": self.student_id,
            "employee_id": self.employee_id,
            "name": self.name,
            "major": self.major,
            "member_type": self.member_type,
            "phone": self.phone,
            "email": self.email,
            "gender": self.gender,
            "role": self.role,
        }
