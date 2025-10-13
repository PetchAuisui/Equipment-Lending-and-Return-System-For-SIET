# =============================================
# app/repositories/history_repository.py
# =============================================
from __future__ import annotations
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, StatusRent, EquipmentImage


class RentHistoryRepository:
    """
    ชั้น Repository สำหรับอ่านประวัติการยืมคืนของผู้ใช้
    """

    def __init__(self, session: Optional[Session] = None):
        self.session: Session = session or SessionLocal()

    # ---------- โค้ดเดิมที่เคยใช้แล้วรูปขึ้น ----------
    def list_by_user(self, user_id: int, returned_only: bool = True) -> List[Dict]:
        """
        ดึงประวัติการยืมของ user_id
        ถ้า returned_only=True → แสดงเฉพาะที่คืนแล้ว (return_date != NULL)
        """
        img_subq = (
            self.session.query(
                EquipmentImage.equipment_id,
                func.min(EquipmentImage.equipment_image_id).label("min_id")
            )
            .group_by(EquipmentImage.equipment_id)
            .subquery()
        )

        stmt = (
            select(
                RentReturn.rent_id,
                RentReturn.start_date,
                RentReturn.due_date,
                RentReturn.return_date,
                RentReturn.reason,
                Equipment.equipment_id,
                Equipment.name.label("equipment_name"),
                Equipment.code.label("equipment_code"),
                Equipment.category,
                StatusRent.name.label("status_name"),
                StatusRent.color_code.label("status_color"),
                EquipmentImage.image_path.label("cover_image"),
            )
            .outerjoin(Equipment, Equipment.equipment_id == RentReturn.equipment_id)
            .outerjoin(StatusRent, StatusRent.status_id == RentReturn.status_id)
            .outerjoin(img_subq, img_subq.c.equipment_id == Equipment.equipment_id)
            .outerjoin(EquipmentImage, EquipmentImage.equipment_image_id == img_subq.c.min_id)
            .where(RentReturn.user_id == user_id)
            .order_by(RentReturn.start_date.desc())
        )

        if returned_only:
            stmt = stmt.where(RentReturn.return_date.isnot(None))

        rows = self.session.execute(stmt).all()
        return [dict(r._mapping) for r in rows]

    # ---------- อินเตอร์เฟซใหม่: ทำงานเทียบเท่าโค้ดเดิม ----------
    def fetch_for_user(self, user_id: int, f) -> List[Dict]:
        """
        รองรับ HistoryFilter แบบโค้ดใหม่
        map ไปใช้ list_by_user() เพื่อคงพฤติกรรมเดิมให้รูปขึ้นแน่ๆ
        """
        returned_only = bool(getattr(f, "returned_only", False))
        rows = self.list_by_user(user_id, returned_only=returned_only)

        # กรองช่วงวันที่/เรียงลำดับตาม f ถ้าต้องการ (optional)
        start_date = getattr(f, "start_date", None)
        end_date   = getattr(f, "end_date", None)
        date_field = getattr(f, "date_field", "start_date") or "start_date"
        order      = (getattr(f, "order", "desc") or "desc").lower()

        if start_date or end_date:
            def in_range(row_dt):
                if row_dt is None:
                    return False
                ok = True
                if start_date:
                    ok = ok and (row_dt >= start_date)
                if end_date:
                    ok = ok and (row_dt <= end_date)
                return ok

            key = "start_date" if date_field == "start_date" else "return_date"
            rows = [r for r in rows if in_range(r.get(key))]

        # เรียง
        key = "start_date" if date_field == "start_date" else "return_date"
        rows.sort(key=lambda r: (r.get(key) or r.get("start_date") or r.get("return_date")), reverse=(order!="asc"))
        return rows

    # ---------- เผื่อมีหน้า all users ใช้งาน ----------
    def fetch_all(self, f) -> List[Dict]:
        """
        แบบง่าย: ดึงทุก user (จะไม่มีชื่อผู้ยืม ถ้าต้องการให้เพิ่ม join User เอง)
        ใช้ pattern เดียวกับ list_by_user แต่ไม่ where user_id
        """
        img_subq = (
            self.session.query(
                EquipmentImage.equipment_id,
                func.min(EquipmentImage.equipment_image_id).label("min_id")
            )
            .group_by(EquipmentImage.equipment_id)
            .subquery()
        )

        stmt = (
            select(
                RentReturn.rent_id,
                RentReturn.user_id,
                RentReturn.start_date,
                RentReturn.due_date,
                RentReturn.return_date,
                RentReturn.reason,
                Equipment.equipment_id,
                Equipment.name.label("equipment_name"),
                Equipment.code.label("equipment_code"),
                Equipment.category,
                StatusRent.name.label("status_name"),
                StatusRent.color_code.label("status_color"),
                EquipmentImage.image_path.label("cover_image"),
            )
            .outerjoin(Equipment, Equipment.equipment_id == RentReturn.equipment_id)
            .outerjoin(StatusRent, StatusRent.status_id == RentReturn.status_id)
            .outerjoin(img_subq, img_subq.c.equipment_id == Equipment.equipment_id)
            .outerjoin(EquipmentImage, EquipmentImage.equipment_image_id == img_subq.c.min_id)
        )

        # filter คืนแล้ว
        if getattr(f, "returned_only", False):
            stmt = stmt.where(RentReturn.return_date.isnot(None))

        # filter ช่วงวันที่
        start_date = getattr(f, "start_date", None)
        end_date   = getattr(f, "end_date", None)
        field_col  = RentReturn.start_date if getattr(f, "date_field", "start_date") == "start_date" else RentReturn.return_date
        if start_date:
            stmt = stmt.where(field_col >= start_date)
        if end_date:
            stmt = stmt.where(field_col <= end_date)

        # order
        order = (getattr(f, "order", "desc") or "desc").lower()
        stmt = stmt.order_by(field_col.asc() if order == "asc" else field_col.desc())

        rows = self.session.execute(stmt).all()
        return [dict(r._mapping) for r in rows]
