from dataclasses import dataclass
from datetime import datetime
from typing import List

from .. import db
from ..database.models import Rent, Equipment, EquipmentAsset, StatusRent


@dataclass
class BorrowService:
    repo: object  # BorrowRepository

    # -------------------- helpers --------------------
    def _get_or_create_status(self, name: str) -> StatusRent:
        """
        หา StatusRent แบบไม่แคร์ตัวพิมพ์เล็ก/ใหญ่
        ถ้าไม่พบให้สร้างใหม่ โดย normalize เป็นตัวพิมพ์เล็กเสมอ
        """
        norm = (name or "").strip().lower()
        # ค้นหาแบบ case-insensitive
        status = StatusRent.query.filter(StatusRent.name.ilike(norm)).first()
        if not status:
            # mapping สีแบบง่าย ๆ
            palette = {
                "pending":  "#ff9800",
                "approved": "#4caf50",
                "rejected": "#f44336",
                "returned": "#2196f3",
            }
            status = StatusRent(name=norm, color_code=palette.get(norm, "#888888"))
            db.session.add(status)
            db.session.commit()
        return status

    # -------------------- core flows --------------------
    def request_borrow(
        self,
        student_id: int,
        equipment_id: int,
        qty: int,
        start_date: datetime,
        due_date: datetime,
        reason: str = "",
        instructor_id: int|None = None,
    ) -> List[Rent]:
        """
        สร้าง "คำขอยืม" ใหม่ (สถานะเริ่มต้น = pending)
        - จองตามจำนวน qty (ขั้นต่ำ 1)
        - ยัง 'ไม่' เปลี่ยนสถานะ asset เป็น rented จนกว่าจะ approve
        """
        qty = max(1, int(qty or 1))
        pending = self._get_or_create_status("pending")

        eq: Equipment | None = Equipment.query.get(equipment_id)
        if not eq:
            raise ValueError("Equipment not found")
        needs_teacher = bool(getattr(eq, "confirm", 0))
        if needs_teacher and not instructor_id:
            raise ValueError("Instructor ID is required")
        asserts = (EquipmentAsset.query.filter_by(Equipment_id=equipment_id, status="available", is_active=True).limit(qty).all())
        if len(asserts) < qty:
            raise ValueError("Not enough equipment available")
        rents: List[Rent] = []
        for asset in asserts:
            r = Rent(
                equipment_id=equipment_id,
                asset_id=asset.asset_id,
                user_id=student_id,
                start_date=start_date,
                due_date=due_date,
                reason=reason,
                status_id=pending.status_id,  # ✅ เริ่มต้นเป็น pending เสมอ
                teacher_confirmed =instructor_id if needs_teacher else None,
            )
            db.session.add(r)
            rents.append(r)
        db.session.commit()
        return rents
            
                

            

        # หา asset ว่าง
        assets_q = EquipmentAsset.query.filter_by(
            equipment_id=equipment_id,
            status="available",
            is_active=True,
        )
        assets = assets_q.limit(qty).all()
        if len(assets) < qty:
            raise ValueError("Equipment not available")

        rents: List[Rent] = []
        for asset in assets:
            r = Rent(
                equipment_id=equipment_id,
                asset_id=asset.asset_id,
                user_id=student_id,
                start_date=start_date,
                due_date=due_date,
                reason=reason,
                status_id=pending.status_id,  # ✅ เริ่มต้นเป็น pending เสมอ
                teacher_confirmed =instructor_id,
            )
            db.session.add(r)
            rents.append(r)

        db.session.commit()
        return rents

    def approve(self, rent_id: int) -> Rent:
        """
        อนุมัติคำขอ: เปลี่ยนเป็น approved + เปลี่ยนสถานะ asset เป็น rented
        """
        r = self.repo.get(rent_id)
        if not r:
            raise ValueError("Request not found")

        approved = self._get_or_create_status("approved")
        r.status_id = approved.status_id

        # mark asset as rented
        if r.asset:
            r.asset.status = "rented"

        db.session.commit()
        return r

    def reject(self, rent_id: int) -> Rent:
        """
        ปฏิเสธคำขอ: เปลี่ยนเป็น rejected (ไม่แตะต้อง asset)
        """
        r = self.repo.get(rent_id)
        if not r:
            raise ValueError("Request not found")

        rejected = self._get_or_create_status("rejected")
        r.status_id = rejected.status_id

        db.session.commit()
        return r

    def mark_returned(self, rent_id: int) -> Rent:
        """
        คืนของ: เปลี่ยนเป็น returned + ปล่อย asset กลับ available
        """
        r = self.repo.get(rent_id)
        if not r:
            raise ValueError("Request not found")

        returned = self._get_or_create_status("returned")
        r.status_id = returned.status_id

        if r.asset:
            r.asset.status = "available"

        db.session.commit()
        return r