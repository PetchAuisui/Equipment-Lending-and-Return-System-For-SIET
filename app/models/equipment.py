from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.db import Base

class Equipment(Base):
    __tablename__ = "equipments"

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(255), nullable=False)
    code         = Column(String(100), unique=True, nullable=False)
    category     = Column(String(100))
    detail       = Column(Text)
    brand        = Column(String(100))
    buy_date     = Column(Date)
    status       = Column(String(50))
    is_active    = Column(Boolean, default=True)

    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔗 ผูกกับตารางรูปภาพ (ไม่สร้างคอลัมน์ใหม่ใน DB — แค่บอก ORM)
    images = relationship(
        "EquipmentImage",
        back_populates="equipment",
        cascade="all, delete-orphan",
        lazy="selectin",   # หรือปล่อยให้ joinedload ทำงานใน query ก็ได้
    )

    def __repr__(self):
        return f"<Equipment {self.code} - {self.name}>"