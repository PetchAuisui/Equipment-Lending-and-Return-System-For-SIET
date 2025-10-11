"""
# app/models/stock_movements.py
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = {"extend_existing": True}  # ถ้า table ชื่อนี้มีอยู่แล้ว ให้ แก้ไข/ปรับปรุง table เดิม แทนที่จะสร้างใหม่


    movement_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)

    history = Column(Text, nullable=True)
    actor_id = Column(Integer, nullable=True)
    actor_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    equipment = relationship("Equipment", back_populates="movements", lazy="joined")
"""
# app/models/stock_movements.py
"""
Shortcut module to reference StockMovement model from app.db.models
โดยไฟล์นี้ไม่ประกาศ class ใหม่ — เพื่อป้องกันการซ้ำของ SQLAlchemy mapping
"""

from app.db.models import StockMovement
