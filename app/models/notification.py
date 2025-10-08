from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from app.db.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # ✅
    channel = Column(String)
    template = Column(String)
    payload = Column(JSON)
    send_at = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="notifications")  # ✅
