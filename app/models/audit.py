# app/models/audit.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base


class Audit(Base):
    __tablename__ = "audits"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action = Column(String(100), nullable=False)  # เช่น 'create', 'update', 'delete'
    table_name = Column(String(100), nullable=True)
    record_id = Column(Integer, nullable=True)    # ID ของเรคคอร์ดที่เกี่ยวข้อง
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ ความสัมพันธ์กับ User
    actor = relationship("User", back_populates="audits")

    def __repr__(self):
        return f"<Audit id={self.audit_id} user_id={self.user_id} action={self.action}>"
