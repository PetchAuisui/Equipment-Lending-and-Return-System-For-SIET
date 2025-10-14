from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.db import Base


# ---------- users ----------
class User(Base):
    __tablename__ = "users"

    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String, nullable=False)
    student_id    = Column(String, unique=True)
    employee_id   = Column(String, unique=True)
    email         = Column(String, nullable=False, unique=True)
    phone         = Column(String)
    major         = Column(String)
    member_type   = Column(String)
    gender        = Column(String)
    password_hash = Column(String, nullable=False)
    role          = Column(String, nullable=False, default="member")
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    instructors        = relationship("Instructor", back_populates="user")
    stock_movements    = relationship("StockMovement", back_populates="actor")
    notifications      = relationship("Notification", back_populates="user")
    
    # ✅ เพิ่ม foreign_keys ให้ชัดเจนทั้งสองด้าน
    rent_checked       = relationship("RentReturn", back_populates="checker", foreign_keys="RentReturn.check_by")
    rent_requests      = relationship("RentReturn", back_populates="user", foreign_keys="RentReturn.user_id")
    teacher_confirmed = relationship("RentReturn",back_populates="teacher_confirm",foreign_keys="RentReturn.teacher_confirmed")
    renewals_approved  = relationship("Renewal", back_populates="approver")
    audits_made        = relationship("UserAudit",back_populates="actor",foreign_keys="UserAudit.actor_id",cascade="all, delete-orphan")
    audits_received    = relationship("UserAudit",back_populates="target_user",foreign_keys="UserAudit.user_id",cascade="all, delete-orphan")






# ---------- subjects ----------
class Subject(Base):
    __tablename__ = "subjects"

    subject_id   = Column(Integer, primary_key=True, autoincrement=True)
    subject_code = Column(String)
    subject_name = Column(String, nullable=False)

    instructors = relationship("Instructor", back_populates="subject")
    sections    = relationship("Section", back_populates="subject")
    rent_returns = relationship("RentReturn", back_populates="subject")


# ---------- instructors ----------
class Instructor(Base):
    __tablename__ = "instructors"

    instructor_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id    = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    subject = relationship("Subject", back_populates="instructors")
    user    = relationship("User", back_populates="instructors")


# ---------- sections ----------
class Section(Base):
    __tablename__ = "sections"

    section_id   = Column(Integer, primary_key=True, autoincrement=True)
    section_name = Column(String, nullable=False)
    subject_id   = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)

    subject = relationship("Subject", back_populates="sections")


# ---------- equipments ----------
class Equipment(Base):
    __tablename__ = "equipments"

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String, nullable=False)
    code         = Column(String, nullable=False, unique=True)
    category     = Column(String)
    confirm      = Column(Boolean, default=False)
    detail       = Column(Text)
    brand        = Column(String)
    buy_date     = Column(Date)
    status       = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment_images = relationship("EquipmentImage", back_populates="equipment")
    stock_movements  = relationship("StockMovement", back_populates="equipment")
    rent_returns     = relationship("RentReturn", back_populates="equipment")


# ---------- equipment_images ----------
class EquipmentImage(Base):
    __tablename__ = "equipment_images"

    equipment_image_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id       = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    image_path         = Column(String, nullable=False)
    description        = Column(Text)
    created_at         = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="equipment_images")


# ---------- stock_movements ----------
class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id  = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    history      = Column(Text, nullable=False)
    actor_id     = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="stock_movements")
    actor     = relationship("User", back_populates="stock_movements")


# ---------- status_rents ----------
class StatusRent(Base):
    __tablename__ = "status_rents"

    status_id  = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String, nullable=False, unique=True)
    color_code = Column(String)

    rent_returns = relationship("RentReturn", back_populates="status")


# ---------- rent_returns ----------
class RentReturn(Base):
    __tablename__ = "rent_returns"

    rent_id      = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject_id   = Column(Integer, ForeignKey("subjects.subject_id"))
    start_date   = Column(DateTime, nullable=False)
    due_date     = Column(DateTime, nullable=False)
    teacher_confirmed = Column(Integer, ForeignKey("users.user_id"))
    reason       = Column(Text)
    return_date  = Column(DateTime)
    check_by     = Column(Integer, ForeignKey("users.user_id"))
    status_id    = Column(Integer, ForeignKey("status_rents.status_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="rent_returns")
    user      = relationship("User", foreign_keys=[user_id], back_populates="rent_requests")
    teacher_confirm = relationship("User", foreign_keys=[teacher_confirmed], back_populates="teacher_confirmed")
    checker   = relationship("User", foreign_keys=[check_by], back_populates="rent_checked")
    subject   = relationship("Subject", back_populates="rent_returns")
    status    = relationship("StatusRent", back_populates="rent_returns")
    item_brokes = relationship("ItemBroke", back_populates="rent_return")
    renewals = relationship("Renewal", back_populates="rent_return")




# ---------- item_brokes ----------
class ItemBroke(Base):
    __tablename__ = "item_brokes"

    item_broke_id = Column(Integer, primary_key=True, autoincrement=True)
    rent_id       = Column(Integer, ForeignKey("rent_returns.rent_id"), nullable=False)
    type          = Column(String, nullable=False)
    detail        = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)

    rent_return        = relationship("RentReturn", back_populates="item_brokes")
    item_broke_images  = relationship("ItemBrokeImage", back_populates="item_broke")


# ---------- item_broke_images ----------
class ItemBrokeImage(Base):
    __tablename__ = "item_broke_images"

    item_broke_image_id = Column(Integer, primary_key=True, autoincrement=True)
    item_broke_id       = Column(Integer, ForeignKey("item_brokes.item_broke_id"), nullable=False)
    image_path          = Column(String, nullable=False)
    created_at          = Column(DateTime, default=datetime.utcnow)

    item_broke = relationship("ItemBroke", back_populates="item_broke_images")


# ---------- notifications ----------
class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    channel         = Column(String, nullable=False)
    template        = Column(String)
    payload         = Column(JSON)
    send_at         = Column(DateTime, nullable=False)
    status          = Column(String, nullable=False, default="scheduled")
    created_at      = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ---------- renewals ----------
class Renewal(Base):
    __tablename__ = "renewals"

    renewal_id  = Column(Integer, primary_key=True, autoincrement=True)
    rent_id     = Column(Integer, ForeignKey("rent_returns.rent_id"), nullable=False)
    old_due     = Column(DateTime, nullable=False)
    new_due     = Column(DateTime, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.user_id"))
    status      = Column(String, nullable=False, default="pending")
    created_at  = Column(DateTime, default=datetime.utcnow)
    note        = Column(Text)

    rent_return = relationship("RentReturn", back_populates="renewals")
    approver    = relationship("User", back_populates="renewals_approved")


# ---------- audits ----------
class UserAudit(Base):
    __tablename__ = "user_audits"

    audit_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # เป้าหมายที่ถูกแก้ไข
    action     = Column(String, nullable=False)  # เช่น created/updated/deleted/profile_change
    actor_id   = Column(Integer, ForeignKey("users.user_id"))                  # คนที่ลงมือ
    diff       = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ↔ เชื่อมกลับไปยัง User ทั้งสองบทบาท
    actor      = relationship("User",foreign_keys=[actor_id],back_populates="audits_made")
    target_user= relationship("User",foreign_keys=[user_id],back_populates="audits_received")
