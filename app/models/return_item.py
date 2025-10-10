# app/models/return_item.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.db.db import Base
from datetime import datetime

class BorrowRecord(Base):
    """
    Model สำหรับบันทึกการยืมและคืนอุปกรณ์ (Borrowing and Returning Record)
    ที่รองรับกระบวนการยืนยันการคืนโดย Admin
    """
    __tablename__ = 'borrow_records'

    # Primary Key ของรายการยืม-คืน
    borrow_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key ไปยังอุปกรณ์และผู้ใช้
    equipment_id = Column(Integer, ForeignKey('equipments.equipment_id'), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    
    # รายละเอียดการยืม
    borrow_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # ✅ ฟิลด์สำคัญที่เพิ่มเข้ามา: สถานะการคืน
    # 'on_loan': กำลังยืมอยู่
    # 'pending_return': ผู้ใช้กดคืนแล้ว รอกดยืนยันจาก Admin
    # 'returned': Admin ยืนยันการคืนเรียบร้อยแล้ว
    return_status = Column(String(50), default='on_loan', nullable=False)
    
    # วันที่ผู้ใช้กดแจ้งคืน
    user_return_date = Column(DateTime, nullable=True) 
    
    # วันที่ Admin ยืนยันการคืนจริง (ใช้เพื่อปลดสถานะอุปกรณ์)
    admin_confirm_date = Column(DateTime, nullable=True)
    
    # ID ของ Admin ผู้ที่ยืนยันการคืน
    admin_confirm_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    # รายละเอียดอื่น ๆ
    purpose = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)

    def __repr__(self):
        return f"<BorrowRecord(id={self.borrow_id}, status={self.return_status})>"