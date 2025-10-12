from __future__ import annotations
from typing import List, Dict
from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_

# ⬇️ เปลี่ยนแหล่งอิมพอร์ตโมเดลตามโครงสร้างใหม่
from app.db.models import (
    User,            # ผู้ยืม / ผู้รับคืน / อาจารย์ที่รับรอง (ใช้ alias)
    Equipment,
    RentReturn,      # ตารางหลัก (start_date, due_date, return_date, status_id, user_id, check_by, teacher_confirmed, ...)
    StatusRent,
)

from app.services.history_service import HistoryFilter


class RentHistoryRepository:
    def __init__(self, session: Session):
        self.session = session

    # ---------- helpers ----------
    @staticmethod
    def _row_to_dict(row) -> Dict:
        return {
            "user_name":        row.user_name,
            "student_id":       row.student_id,
            "employee_id":      row.employee_id,
            "equipment_name":   row.equipment_name,
            "start_date":       row.start_date,
            "due_date":         row.due_date,
            "return_date":      row.return_date,
            "status_name":      row.status_name,
            "status_color":     row.status_color,
            "receiver_name":    getattr(row, "receiver_name", None),
            "instructor_name":  getattr(row, "instructor_name", None),
        }

    def _apply_date_filter(self, query, f: HistoryFilter):
        # เลือก field สำหรับกรองช่วงวันที่
        field = RentReturn.start_date if f.date_field == "start_date" else RentReturn.return_date
        conds = []
        if f.start_date:
            conds.append(field >= f.start_date)
        if f.end_date:
            conds.append(field <= f.end_date)
        if conds:
            query = query.filter(and_(*conds))
        return query

    # ---------- main readers ----------
    def fetch_all(self, f: HistoryFilter) -> List[Dict]:
        """
        รวมประวัติทุกผู้ใช้ (JOIN ครบ) ตามสคีมาใหม่ที่ใช้ RentReturn ตารางเดียว
        """
        borrower   = aliased(User)  # ผู้ยืม
        receiver   = aliased(User)  # ผู้รับคืน (RentReturn.check_by)
        instructor = aliased(User)  # อาจารย์ที่รับรอง (RentReturn.teacher_confirmed)

        q = (
            self.session.query(
                borrower.name.label("user_name"),
                borrower.student_id,
                borrower.employee_id,
                Equipment.name.label("equipment_name"),
                RentReturn.start_date,
                RentReturn.due_date,
                RentReturn.return_date,
                StatusRent.name.label("status_name"),
                StatusRent.color_code.label("status_color"),
                receiver.name.label("receiver_name"),
                instructor.name.label("instructor_name"),
            )
            .join(RentReturn, RentReturn.user_id == borrower.user_id)
            .join(Equipment, Equipment.equipment_id == RentReturn.equipment_id)
            .join(StatusRent, StatusRent.status_id == RentReturn.status_id)
            .outerjoin(receiver,   receiver.user_id   == RentReturn.check_by)
            .outerjoin(instructor, instructor.user_id == RentReturn.teacher_confirmed)
        )

        if f.returned_only:
            q = q.filter(RentReturn.return_date.isnot(None))

        q = self._apply_date_filter(q, f)

        # เรียงลำดับ
        if f.order == "asc":
            order_exp = (RentReturn.start_date.asc() if f.date_field == "start_date"
                         else RentReturn.return_date.asc())
        else:
            order_exp = (RentReturn.start_date.desc() if f.date_field == "start_date"
                         else RentReturn.return_date.desc())
        q = q.order_by(order_exp)

        return [self._row_to_dict(r) for r in q.all()]

    def fetch_for_user(self, user_id: int, f: HistoryFilter) -> List[Dict]:
        borrower   = aliased(User)
        receiver   = aliased(User)
        instructor = aliased(User)

        q = (
            self.session.query(
                borrower.name.label("user_name"),
                borrower.student_id,
                borrower.employee_id,
                Equipment.name.label("equipment_name"),
                RentReturn.start_date,
                RentReturn.due_date,
                RentReturn.return_date,
                StatusRent.name.label("status_name"),
                StatusRent.color_code.label("status_color"),
                receiver.name.label("receiver_name"),
                instructor.name.label("instructor_name"),
            )
            .join(RentReturn, RentReturn.user_id == borrower.user_id)
            .join(Equipment, Equipment.equipment_id == RentReturn.equipment_id)
            .join(StatusRent, StatusRent.status_id == RentReturn.status_id)
            .outerjoin(receiver,   receiver.user_id   == RentReturn.check_by)
            .outerjoin(instructor, instructor.user_id == RentReturn.teacher_confirmed)
            .filter(borrower.user_id == user_id)
        )

        if f.returned_only:
            q = q.filter(RentReturn.return_date.isnot(None))

        q = self._apply_date_filter(q, f)

        if f.order == "asc":
            order_exp = (RentReturn.start_date.asc() if f.date_field == "start_date"
                         else RentReturn.return_date.asc())
        else:
            order_exp = (RentReturn.start_date.desc() if f.date_field == "start_date"
                         else RentReturn.return_date.desc())
        q = q.order_by(order_exp)

        return [self._row_to_dict(r) for r in q.all()]
