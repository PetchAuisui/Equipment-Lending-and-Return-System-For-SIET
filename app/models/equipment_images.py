# app/models/equipment_images.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class EquipmentImage(Base):
    __tablename__ = "equipment_images"  # ← ชื่อตารางต้องเป็น equipment_images

    image_id     = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False, index=True)
    image_path   = Column(String(255), nullable=False)  # เก็บ path relative ต่อ static/
    description  = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)

    # ความสัมพันธ์ย้อนกลับไปหา Equipment (อ้างชื่อเป็นสตริง ไม่ต้อง import Equipment ตรงๆ)
    equipment = relationship("Equipment", back_populates="images")

    def __repr__(self):
        return f"<EquipmentImage {self.image_id} for eq {self.equipment_id}>"
