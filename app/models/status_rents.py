# app/models/status_rents.py
from sqlalchemy import Column, Integer, String
from app.db.db import Base

class StatusRent(Base):
    __tablename__ = "status_rents"

    status_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # เช่น "ยืมอยู่", "คืนแล้ว", "เกินกำหนด"

    def __repr__(self):
        return f"<StatusRent(id={self.status_id}, name='{self.name}')>"
