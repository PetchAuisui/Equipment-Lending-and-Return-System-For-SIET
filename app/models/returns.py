from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class Return(Base):
    __tablename__ = "returns"

    return_id = Column(Integer, primary_key=True, autoincrement=True)
    rent_id = Column(Integer, ForeignKey("rents.rent_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    return_date = Column(DateTime, default=datetime.utcnow)

    # ความสัมพันธ์
    receiver = relationship("User", back_populates="returns")
    rent = relationship("Rent", back_populates="return_record")

    def __repr__(self):
        return f"<Return id={self.return_id} rent_id={self.rent_id}>"
