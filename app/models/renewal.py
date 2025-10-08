from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.db import Base

class Renewal(Base):
    __tablename__ = "renewals"

    renewal_id = Column(Integer, primary_key=True, autoincrement=True)
    rent_id = Column(Integer, ForeignKey("rents.rent_id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.user_id"))  # ✅ FK ถูกต้อง
    old_due = Column(DateTime)
    new_due = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)

    # ความสัมพันธ์
    approver = relationship("User", back_populates="renewals_approved")
    rent = relationship("Rent", back_populates="renewals")

    def __repr__(self):
        return f"<Renewal id={self.renewal_id} rent_id={self.rent_id}>"
