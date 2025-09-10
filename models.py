# models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from db import Base

# ---------- users ----------
class User(Base):
    __tablename__ = "users"
    user_id       = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String, nullable=False)
    email         = Column(String, nullable=False, unique=True)     # enforce @kmitl.ac.th in app layer
    phone         = Column(String)
    major         = Column(String)
    member_type   = Column(String)                                   # student, staff, etc.
    gender        = Column(String)
    password_hash = Column(String, nullable=False)                   # store hash only
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    # relationships
    classes = relationship("Class", back_populates="owner")
    rents   = relationship("Rent", back_populates="user")
    stock_movements = relationship("StockMovement", back_populates="actor")
    returns = relationship("Return", back_populates="receiver")

# ---------- subjects ----------
class Subject(Base):
    __tablename__ = "subjects"
    subject_id   = Column(Integer, primary_key=True, autoincrement=True)
    subject_code = Column(String)
    subject_name = Column(String, nullable=False)

    classes = relationship("Class", back_populates="subject")

# ---------- classes ----------
class Class(Base):
    __tablename__ = "classes"
    class_id     = Column(Integer, primary_key=True, autoincrement=True)
    subject_id   = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    section_name = Column(String, nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # owner/lecturer

    subject = relationship("Subject", back_populates="classes")
    owner   = relationship("User", back_populates="classes")
    rents   = relationship("Rent", back_populates="clazz")

# ---------- equipments ----------
class Equipment(Base):
    __tablename__ = "equipments"
    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String, nullable=False)
    code         = Column(String, nullable=False, unique=True)      # asset code / barcode
    category     = Column(String)
    detail       = Column(Text)
    brand        = Column(String)
    buy_date     = Column(Date)
    status       = Column(String)                                    # available, rented, maintenance...
    is_active    = Column(Boolean, nullable=False, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow)

    rents           = relationship("Rent", back_populates="equipment")
    stock_moves     = relationship("StockMovement", back_populates="equipment")
    images          = relationship("EquipmentImage", back_populates="equipment")

# ---------- stock_movements ----------
class StockMovement(Base):
    __tablename__ = "stock_movements"
    movement_id  = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    history      = Column(Text, nullable=False)                      # description of movement
    actor_id     = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="stock_moves")
    actor     = relationship("User", back_populates="stock_movements")

# ---------- equipment_images ----------
class EquipmentImage(Base):
    __tablename__ = "equipment_images"
    image_id     = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    image_path   = Column(String, nullable=False)
    description  = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="images")

# ---------- status_rents ----------
class StatusRent(Base):
    __tablename__ = "status_rents"
    status_id  = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String, nullable=False, unique=True)         # Pending, Approved, Borrowing, ...
    color_code = Column(String)                                      # #RRGGBB

    rents = relationship("Rent", back_populates="status")

# ---------- rents ----------
class Rent(Base):
    __tablename__ = "rents"
    rent_id      = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipments.equipment_id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    class_id     = Column(Integer, ForeignKey("classes.class_id"))
    start_date   = Column(DateTime, nullable=False)
    due_date     = Column(DateTime, nullable=False)
    reason       = Column(Text)
    status_id    = Column(Integer, ForeignKey("status_rents.status_id"), nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    equipment = relationship("Equipment", back_populates="rents")
    user      = relationship("User", back_populates="rents")
    clazz     = relationship("Class", back_populates="rents")
    status    = relationship("StatusRent", back_populates="rents")
    ret       = relationship("Return", back_populates="rent", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_rents_equipment_start", "equipment_id", "start_date"),
    )

# ---------- returns ----------
class Return(Base):
    __tablename__ = "returns"
    return_id   = Column(Integer, primary_key=True, autoincrement=True)
    rent_id     = Column(Integer, ForeignKey("rents.rent_id"), nullable=False, unique=True)  # 1:1 with rents
    image_path  = Column(String)
    user_id     = Column(Integer, ForeignKey("users.user_id"), nullable=False)               # receiver
    return_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    rent     = relationship("Rent", back_populates="ret")
    receiver = relationship("User", back_populates="returns")
    item_brokes = relationship("ItemBroke", back_populates="ret", cascade="all, delete-orphan")

# ---------- item_brokes ----------
class ItemBroke(Base):
    __tablename__ = "item_brokes"
    item_broke_id = Column(Integer, primary_key=True, autoincrement=True)
    return_id     = Column(Integer, ForeignKey("returns.return_id"), nullable=False)
    type          = Column(String, nullable=False)     # enum: broke/lost
    detail        = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)

    ret = relationship("Return", back_populates="item_brokes")

    __table_args__ = (
        CheckConstraint("type in ('broke','lost')", name="ck_item_brokes_type_enum"),
    )
