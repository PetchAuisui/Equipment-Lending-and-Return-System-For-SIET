from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from app.db.db import Base

class Equipment(Base):
    __tablename__ = "equipments"
    __table_args__ = {"extend_existing": True}  # ป้องกัน error หาก table ถูก define ซ้ำ

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    category = Column(String)
    detail = Column(Text)
    brand = Column(String)
    buy_date = Column(Date)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return f"<Equipment id={self.equipment_id} name={self.name} code={self.code}>"
