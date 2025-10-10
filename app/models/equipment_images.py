"""from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.db import Base

class EquipmentImage(Base):
    __tablename__ = "equipment_images"
    __table_args__ = {"extend_existing": True} # ถ้า table ชื่อนี้มีอยู่แล้ว ให้ แก้ไข/ปรับปรุง table เดิม แทนที่จะสร้างใหม่

    # PK จริงในตาราง DB = equipment_image_id
    image_id = Column("equipment_image_id", Integer, primary_key=True, autoincrement=True)

    equipment_id = Column(
        Integer,
        ForeignKey("equipments.equipment_id", ondelete="CASCADE"),
        nullable=False
    )
    image_path = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ฝั่งกลับไปหา Equipment
    equipment = relationship("Equipment", back_populates="images")

    def __repr__(self):
        return f"<EquipmentImage {self.image_path}>"
"""

