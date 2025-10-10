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

    # relationships
    instructor          = relationship("Instructor", back_populates="user", uselist=False)
    rents               = relationship("Rent", back_populates="user")
    stock_movements     = relationship("StockMovement", back_populates="actor")
    notifications       = relationship("Notification", back_populates="user")
    renewals_approved   = relationship("Renewal", back_populates="approver")
    audits              = relationship("Audit", back_populates="actor")
    equipments_checked  = relationship("Equipment", back_populates="checker")


# ---------- subjects ----------
class Subject(Base):
    __tablename__ = "subjects"

    subject_id   = Column(Integer, primary_key=True, autoincrement=True)
    subject_code = Column(String)
    subject_name = Column(String, nullable=False)

    rents       = relationship("Rent", back_populates="subject")
    sections    = relationship("Section", back_populates="subject")
    instructors = relationship("Instructor", back_populates="subject")


# ---------- instructors ----------
class Instructor(Base):
    __tablename__ = "instructors"

    instructor_id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id    = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    subject = relationship("Subject", back_populates="instructors")
    user    = relationship("User", back_populates="instructor")


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
    __table_args__ = {"extend_existing": True}

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String, nullable=False)
    code         = Column(String, nullable=False, unique=True)
    category     = Column(String)
    confirm      = Column(Boolean, default=False)
    detail       = Column(Text)
    brand        = Column(String)
    buy_date     = Column(Date)
    return_date  = Column(Date)
    check_by     = Column(Integer, ForeignKey("users.user_id"))
    status       = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)

    # relationships
    rents            = relationship("Rent", back_populates="equipment")
    stock_movements  = relationship("StockMovement", back_populates="equipment")
    equipment_images = relationship("EquipmentImage", back_populates="equipment")
    checker          = relationship("User", back_populates="equipments_checked")


# ---------- equipment_images ----------
class EquipmentImage(Base):
    __tablename__ = "equipment_images"
    __table_args__ = {"extend_existing": True}

    equipment_image_id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id       = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    image_path         = Column(String, nullable=False)
    description        = Column(Text)
    created_at         = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="equipment_images")


# ---------- stock_movements ----------
class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = {"extend_existing": True}

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

    rents = relationship("Rent", back_populates="status")


# ---------- rents ----------
class Rent(Base):
    __tablename__ = "rents"

    rent_id      = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    subject_id   = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    start_date   = Column(DateTime, nullable=False)
    due_date     = Column(DateTime, nullable=False)
    reason       = Column(Text)
    status_id    = Column(Integer, ForeignKey("status_rents.status_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment   = relationship("Equipment", back_populates="rents")
    user        = relationship("User", back_populates="rents")
    subject     = relationship("Subject", back_populates="rents")
    status      = relationship("StatusRent", back_populates="rents")
    renewals    = relationship("Renewal", back_populates="rent")
    item_brokes = relationship("ItemBroke", back_populates="rent")


# ---------- item_brokes ----------
class ItemBroke(Base):
    __tablename__ = "item_brokes"

    item_broke_id = Column(Integer, primary_key=True, autoincrement=True)
    rent_id       = Column(Integer, ForeignKey("rents.rent_id"), nullable=False)
    type          = Column(String, nullable=False)
    detail        = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)

    rent              = relationship("Rent", back_populates="item_brokes")
    item_broke_images = relationship("ItemBrokeImage", back_populates="item_broke")


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
    rent_id     = Column(Integer, ForeignKey("rents.rent_id"), nullable=False)
    old_due     = Column(DateTime, nullable=False)
    new_due     = Column(DateTime, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.user_id"))
    created_at  = Column(DateTime, default=datetime.utcnow)
    note        = Column(Text)

    rent     = relationship("Rent", back_populates="renewals")
    approver = relationship("User", back_populates="renewals_approved")


# ---------- audits ----------
class Audit(Base):
    __tablename__ = "audits"

    audit_id   = Column(Integer, primary_key=True, autoincrement=True)
    entity_id  = Column(Integer, nullable=False)
    action     = Column(String, nullable=False)
    actor_id   = Column(Integer, ForeignKey("users.user_id"))
    diff       = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audits")
