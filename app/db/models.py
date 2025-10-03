from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, Index, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship
from app.db.db import Base

# ---------- users ----------
class User(Base):
    __tablename__ = "users"
    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String, nullable=False)
    student_id    = Column(String, unique=True)         # null ได้สำหรับ non-student
    employee_id   = Column(String, unique=True)         # null ได้สำหรับ non-staff
    email         = Column(String, nullable=False, unique=True)
    phone         = Column(String)
    major         = Column(String)
    member_type   = Column(String)                      # student, teacher, staff, ...
    gender        = Column(String)
    password_hash = Column(String, nullable=False)
    role          = Column(String, nullable=False, default="member")   # ✅ เพิ่มคอลัมน์นี้
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    instructor        = relationship("Instructor", back_populates="user", uselist=False)
    rents             = relationship("Rent", back_populates="user")
    stock_movements   = relationship("StockMovement", back_populates="actor")
    returns           = relationship("Return", back_populates="receiver")
    notifications     = relationship("Notification", back_populates="user")
    renewals_approved = relationship("Renewal", back_populates="approver")
    audits            = relationship("Audit", back_populates="actor")

# ---------- subjects ----------
class Subject(Base):
    __tablename__ = "subjects"
    subject_id   = Column(Integer, primary_key=True, autoincrement=True)
    subject_code = Column(String)
    subject_name = Column(String, nullable=False)

    rent = relationship("Rent", back_populates="subject")
    section = relationship("Section", back_populates="subject")
    instructor = relationship("Instructor", back_populates="subject")

class Instructor(Base):
    __tablename__ = "instructors"
    instructor_id   = Column(Integer, primary_key=True, autoincrement=True)
    subject_id      = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    user_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    subject = relationship("Subject", back_populates="instructor")
    user    = relationship("User", back_populates="instructor")

class Section(Base):
    __tablename__ = "sections"
    section_id   = Column(Integer, primary_key=True, autoincrement=True)
    section_name = Column(String, nullable=False)
    subject_id   = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)


    subject = relationship("Section", back_populates="section")

# ---------- classes ----------
class Class(Base):
    __tablename__ = "classes"
    class_id     = Column(Integer, primary_key=True, autoincrement=True)
    class_no = Column(String, nullable=False)
    class_name = Column(String)
    class_location = Column(String)

    rents   = relationship("Rent", back_populates="clazz")

# ---------- equipments (รุ่น) ----------
class Equipment(Base):
    __tablename__ = "equipments"
    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String, nullable=False)
    code         = Column(String, nullable=False, unique=True)
    category     = Column(String)
    detail       = Column(Text)
    brand        = Column(String)
    buy_date     = Column(Date)
    status       = Column(String)                               # available, rented, maintenance
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow)

    rents       = relationship("Rent", back_populates="equipment")
    stock_moves = relationship("StockMovement", back_populates="equipment")
    equipment_Image      = relationship("Equipment_Image", back_populates="equipment")


# ---------- equipment_images ----------
class Equipment_Image(Base):
    __tablename__ = "equipment_images"
    equipment_image_id     = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    image_path   = Column(String, nullable=False)
    description  = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="equipment_Image")


# ---------- stock_movements ----------
class StockMovement(Base):
    __tablename__ = "stock_movements"
    movement_id  = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    history      = Column(Text, nullable=False)
    actor_id     = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="stock_moves")
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
    class_id     = Column(Integer, ForeignKey("classes.class_id"))
    start_date   = Column(DateTime, nullable=False)
    due_date     = Column(DateTime, nullable=False)
    reason       = Column(Text)
    status_id    = Column(Integer, ForeignKey("status_rents.status_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="rents")
    user      = relationship("User", back_populates="rents")
    subject   = relationship("Subject", back_populates="section")
    clazz     = relationship("Class", back_populates="rents")
    status    = relationship("StatusRent", back_populates="rents")
    ret       = relationship("Return", back_populates="rent", uselist=False, cascade="all, delete-orphan")
    renewals  = relationship("Renewal", back_populates="rent")

    __table_args__ = (
        Index("ix_rents_equipment_start", "equipment_id", "start_date"),
    )

# ---------- returns ----------
class Return(Base):
    __tablename__ = "returns"
    return_id   = Column(Integer, primary_key=True, autoincrement=True)
    rent_id     = Column(Integer, ForeignKey("rents.rent_id"), nullable=False, unique=True)
    user_id     = Column(Integer, ForeignKey("users.user_id"), nullable=False)   # receiver
    return_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    rent        = relationship("Rent", back_populates="ret")
    receiver    = relationship("User", back_populates="returns")
    item_brokes = relationship("ItemBroke", back_populates="ret", cascade="all, delete-orphan")

# ---------- item_brokes ----------
class ItemBroke(Base):
    __tablename__ = "item_brokes"
    item_broke_id = Column(Integer, primary_key=True, autoincrement=True)
    return_id     = Column(Integer, ForeignKey("returns.return_id"), nullable=False)
    type          = Column(String, nullable=False)   # enum: broke/lost
    detail        = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)

    ret = relationship("Return", back_populates="item_brokes")
    itemBroke_image_id = relationship("ItemBroke_images", back_populates="itemBroke")

    __table_args__ = (
        CheckConstraint("type in ('broke','lost')", name="ck_item_brokes_type_enum"),
    )

class ItemBroke_images(Base):
    __tablename__ = "ItemBroke_images"
    itemBroke_image_id     = Column(Integer, primary_key=True, autoincrement=True)
    item_broke_id = Column(Integer, ForeignKey("item_brokes.item_broke_id"), nullable=False)
    image_path   = Column(String, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    itemBroke = relationship("item_brokes", back_populates="itemBroke_image_id")


# ---------- notifications ----------
class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    channel         = Column(String, nullable=False)   # email, line, sms
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
    action     = Column(String, nullable=False)   # created, updated, status_change
    actor_id   = Column(Integer, ForeignKey("users.user_id"))
    diff       = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audits")
