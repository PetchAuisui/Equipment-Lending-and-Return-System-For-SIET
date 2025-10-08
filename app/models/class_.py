# app/models/class_.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.db import Base

class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, primary_key=True, autoincrement=True)
    class_no = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    class_location = Column(String, nullable=True)

    # ✅ เพิ่ม foreign key ให้ ORM รู้ว่ามีเจ้าของ (User)
    owner_id = Column(Integer, ForeignKey("users.user_id"))

    # ความสัมพันธ์กลับไปยัง User
    owner = relationship("User", back_populates="classes")

    def __repr__(self):
        return f"<Class id={self.class_id} name={self.class_name}>"
