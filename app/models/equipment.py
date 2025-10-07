# app/models/equipment.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.orm import relationship
from app.db.db import Base


class Equipment(Base):
    __tablename__ = "equipments"
    __table_args__ = {"extend_existing": True}  # ถ้า table ชื่อนี้มีอยู่แล้ว ให้ แก้ไข/ปรับปรุง table เดิม แทนที่จะสร้างใหม่

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(255), nullable=False)   # ชื่ออุปกรณ์
    code         = Column(String(100), unique=True, nullable=False)  # รหัสอุปกรณ์
    category     = Column(String(100))                   # หมวดหมู่
    detail       = Column(Text)                          # รายละเอียดเพิ่มเติม
    brand        = Column(String(100))                   # ยี่ห้อ
    buy_date     = Column(Date)                          # วันที่ซื้อ
    status       = Column(String(50))                    # สถานะ เช่น available, borrowed

    created_at   = Column(DateTime, default=datetime.utcnow)

    movements = relationship("StockMovement", back_populates="equipment", cascade="all, delete-orphan")

    # 🔗 ความสัมพันธ์กับตาราง EquipmentImage
    images = relationship(
        "EquipmentImage",
        back_populates="equipment",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Equipment id={self.equipment_id} code={self.code} name={self.name}>"
