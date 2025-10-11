# app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.db import Base


class User(Base):
    __tablename__ = "users"

    # -------- Columns --------
    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String, nullable=False)
    student_id    = Column(String, unique=True, nullable=True)   # สำหรับ student
    employee_id   = Column(String, unique=True, nullable=True)   # สำหรับบุคลากร
    email         = Column(String, nullable=False, unique=True)
    phone         = Column(String, nullable=True)
    major         = Column(String, nullable=True)
    member_type   = Column(String, nullable=False)               # student | teacher | officer | staff
    gender        = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role          = Column(String, nullable=False, default="member")
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # -------- Relationships (สอดคล้องกับตารางที่มีอยู่ในโปรเจกต์) --------
    classes           = relationship("Class", back_populates="owner")
    rents             = relationship("Rent", back_populates="user")
    stock_movements   = relationship("StockMovement", back_populates="actor")
    returns           = relationship("Return", back_populates="receiver")
    notifications     = relationship("Notification", back_populates="user")
    renewals_approved = relationship("Renewal", back_populates="approver")
    audits            = relationship("Audit", back_populates="actor")

    # -------- Helpers --------
    def to_dict(self) -> dict:
        """แปลง ORM instance → dict (รวมฟิลด์ auth/timestamps)"""
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

    def public_dict(self) -> dict:
        """สำหรับส่งกลับ UI/API (ไม่รวม password_hash)"""
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

    def __repr__(self) -> str:
        ident = self.student_id or self.employee_id or "-"
        return f"<User {self.user_id} {self.email} ({ident})>"
