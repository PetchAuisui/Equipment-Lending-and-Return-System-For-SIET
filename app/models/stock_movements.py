# app/models/stock_movements.py
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)

    history = Column(Text, nullable=True)
    actor_id = Column(Integer, nullable=True)
    actor_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    equipment = relationship("Equipment", back_populates="movements", lazy="joined")
   # ✅ เพิ่ม ForeignKey ที่ชี้ไปยัง users.user_id
    actor_id = Column(Integer, ForeignKey("users.user_id"))

    # ความสัมพันธ์กลับไปที่ User
    actor = relationship("User", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement id={self.id} type={self.movement_type}>"