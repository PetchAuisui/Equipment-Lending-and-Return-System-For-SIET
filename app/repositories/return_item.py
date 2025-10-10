# app/repositories/return_item.py

# ❌ บรรทัดเดิม:
# from app.repositories.base_repository import BaseRepository 
# ✅ แก้ไขเป็น:
from app.repositories.base_repository import BaseJsonRepository 
from app.models.return_item import BorrowRecord
from app.models.equipment import Equipment 
from app.db.db import SessionLocal
from sqlalchemy.orm import joinedload
from datetime import datetime


class ReturnItemRepository(BaseJsonRepository): # 👈 เปลี่ยนการสืบทอด
    """
    Repository สำหรับจัดการการคืนอุปกรณ์ (Return Item)
    
    โดยจะจัดการกับ BorrowRecord Model เป็นหลัก
    """
    def __init__(self, db_session: SessionLocal):
        """กำหนด Model หลักที่ Repository นี้จะใช้งาน"""
        # ใช้งาน BaseJsonRepository
        super().__init__(db_session, BorrowRecord)

    # ... (เมธอดอื่น ๆ ยังคงเหมือนเดิม) ...
    # get_pending_returns
    # get_latest_loan
    # mark_as_pending_return
    # confirm_return
    
    def get_pending_returns(self):
        """
        ดึงรายการอุปกรณ์ที่ผู้ใช้แจ้งคืนแล้วและกำลังรอ Admin ยืนยัน
        """
        return (
            self.db_session.query(BorrowRecord)
            .options(joinedload(BorrowRecord.equipment), 
                     joinedload(BorrowRecord.user)) 
            .filter(BorrowRecord.return_status == 'pending_return')
            .order_by(BorrowRecord.user_return_date.asc())
            .all()
        )

    def get_latest_loan(self, equipment_id: int):
        """
        ดึงรายการยืมล่าสุดของอุปกรณ์ที่ยังไม่มีการคืน (return_status != 'returned')
        """
        return (
            self.db_session.query(BorrowRecord)
            .filter(BorrowRecord.equipment_id == equipment_id)
            .filter(BorrowRecord.return_status.in_(['on_loan', 'pending_return']))
            .order_by(BorrowRecord.borrow_date.desc())
            .first()
        )

    def mark_as_pending_return(self, borrow_id: int):
        """
        อัปเดตสถานะการยืมเป็น 'pending_return' (ผู้ใช้แจ้งคืน)
        """
        record = self.get_by_id(borrow_id)
        if record:
            record.return_status = 'pending_return'
            record.user_return_date = datetime.utcnow()
            self.db_session.commit()
            return record
        return None

    def confirm_return(self, borrow_id: int, admin_id: int):
        """
        Admin ยืนยันการคืน:
        1. อัปเดตสถานะ BorrowRecord เป็น 'returned'
        2. อัปเดตสถานะ Equipment เป็น 'available'
        """
        record = self.get_by_id(borrow_id)
        if record:
            # 1. อัปเดต BorrowRecord
            record.return_status = 'returned'
            record.admin_confirm_date = datetime.utcnow()
            record.admin_confirm_id = admin_id
            
            # 2. อัปเดตสถานะ Equipment
            equipment = (
                self.db_session.query(Equipment)
                .filter(Equipment.equipment_id == record.equipment_id)
                .first()
            )
            if equipment:
                equipment.status = 'available'
            
            self.db_session.commit()
            return record
        return None
