from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.models.status_rents import StatusRent


class Rent(Base):
    __tablename__ = "rents"

    rent_id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # ✅ ได้แล้ว
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"))
    class_id = Column(Integer, ForeignKey("classes.class_id"))
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    reason = Column(Text)
    status_id = Column(Integer, ForeignKey("status_rents.status_id"))
    created_at = Column(DateTime)

    # ความสัมพันธ์
    equipment = relationship("Equipment", backref="rents")
    user = relationship("User", back_populates="rents")  # ✅ เชื่อมกับ users
    status = relationship("StatusRent", backref="rents")
    return_record = relationship("Return", back_populates="rent", uselist=False)
    renewals = relationship("Renewal", back_populates="rent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rent(id={self.rent_id}, equipment_id={self.equipment_id}, user_id={self.user_id})>"
