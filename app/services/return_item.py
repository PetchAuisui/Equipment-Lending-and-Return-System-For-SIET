# app/services/return_item.py

from app.db.db import SessionLocal
from app.repositories.return_item import ReturnItemRepository
from app.models.equipment import Equipment # เพื่อใช้ในการค้นหาอุปกรณ์
from app.models.return_item import BorrowRecord # เพื่อใช้ในการจัดการ BorrowRecord


class ReturnItemService:
    """
    Service Layer สำหรับจัดการ Business Logic ในกระบวนการคืนอุปกรณ์
    """
    
    def __init__(self, db_session: SessionLocal):
        """
        สร้าง Repository ที่จำเป็นสำหรับการทำงานของ Service นี้
        """
        self.db = db_session
        self.return_repo = ReturnItemRepository(db_session)

    def user_request_return(self, borrow_id: int):
        """
        1. ผู้ใช้กดแจ้งคืนอุปกรณ์ (เปลี่ยนสถานะเป็น 'pending_return')
        
        :param borrow_id: ID ของรายการยืมที่ต้องการแจ้งคืน
        :return: BorrowRecord object ที่ถูกอัปเดต หรือ None ถ้าไม่พบ
        """
        record = self.return_repo.get_by_id(borrow_id)

        if not record:
            return None, "ไม่พบรายการยืมดังกล่าว"

        if record.return_status != 'on_loan':
            return None, "รายการนี้ไม่ได้อยู่ในสถานะที่กำลังยืมอยู่"
        
        # ใช้ Repository ในการอัปเดตสถานะ
        updated_record = self.return_repo.mark_as_pending_return(borrow_id)
        
        # Commit การเปลี่ยนแปลงไปยัง DB
        self.db.commit()
        
        return updated_record, "แจ้งคืนอุปกรณ์เรียบร้อยแล้ว รอผู้ดูแลระบบยืนยัน"
    
    
    def get_pending_returns_list(self):
        """
        ดึงรายการอุปกรณ์ทั้งหมดที่รอ Admin ยืนยันการคืน
        """
        # ใช้ Repository ในการดึงข้อมูลที่ join กันแล้ว
        return self.return_repo.get_pending_returns()

    
    def admin_confirm_return(self, borrow_id: int, admin_id: int):
        """
        2. Admin ยืนยันการคืนอุปกรณ์ (เปลี่ยนสถานะเป็น 'returned' และปลดสถานะอุปกรณ์)

        :param borrow_id: ID ของรายการยืมที่ Admin ต้องการยืนยัน
        :param admin_id: ID ของ Admin ที่ทำการยืนยัน
        :return: BorrowRecord object ที่ถูกอัปเดต หรือ None ถ้าไม่พบ
        """
        record = self.return_repo.get_by_id(borrow_id)

        if not record:
            return None, "ไม่พบรายการยืมที่ต้องการยืนยัน"

        if record.return_status == 'returned':
            return None, "รายการนี้ถูกยืนยันการคืนไปแล้ว"
        
        if record.return_status == 'on_loan':
            return None, "ผู้ใช้ยังไม่ได้แจ้งคืน กรุณาให้ผู้ใช้แจ้งคืนก่อน"
        
        # ใช้ Repository ในการยืนยันการคืนและอัปเดตสถานะอุปกรณ์
        updated_record = self.return_repo.confirm_return(borrow_id, admin_id)
        
        # Commit การเปลี่ยนแปลงไปยัง DB (commit ถูกเรียกใน repo แล้ว แต่เรียกอีกครั้งก็ปลอดภัย)
        # self.db.commit() 
        
        # ดึงชื่ออุปกรณ์เพื่อใช้ในข้อความแจ้งเตือน (Optional)
        equipment = self.db.query(Equipment).filter(Equipment.equipment_id == record.equipment_id).first()
        equipment_name = equipment.name if equipment else "อุปกรณ์"

        return updated_record, f"ยืนยันการคืน {equipment_name} เรียบร้อยแล้ว"