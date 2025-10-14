# app/controllers/admin_history_controller.py
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Callable, Optional, List, Dict
from flask import request, render_template
from sqlalchemy import text

class AdminHistoryController:
    """
    Class-based controller สำหรับหน้า 'ประวัติยืม-คืนทั้งหมด'
    - ไม่แก้ service/repository เดิม
    - ใช้ factory ที่ส่งมาจาก routes.py เพื่อสร้าง service/repo ทุกครั้ง
    - ผูก endpoint ใหม่ไว้ใต้ blueprint เดิม (เช่น /admin/history/oop และ /admin/history/oop/filter)
    """

    def __init__(
        self,
        bp,                                   # Blueprint ที่สร้างไว้แล้ว (admin_history_bp)
        hist_svc_factory: Callable,           # -> BorrowHistoryService
        user_repo_factory: Callable,          # -> UserRepository
        staff_guard: Callable,                # decorator @staff_required
    ):
        self.bp = bp
        self._hist_svc = hist_svc_factory
        self._user_repo = user_repo_factory

        # register routes (apply staff_guard)
        self.bp.add_url_rule("/oop",        view_func=staff_guard(self.index),  endpoint="oop_index")
        self.bp.add_url_rule("/oop/filter", view_func=staff_guard(self.filter), endpoint="oop_filter")

    # ---------------- public handlers ----------------
    def index(self):
        """แสดงทั้งหมด (ไม่กรอง) — /admin/history/oop"""
        items = self._collect_items()
        items.sort(key=lambda x: (self._as_dt(x.get("start_date")) or datetime.min), reverse=True)
        return render_template(
            "pages_history/admin_all_history.html",
            items=items,
            q_start="",
            q_end="",
            q_identity="",
        )

    def filter(self):
        """
        กรองช่วงวันที่ (ยึด Rent.start_date) + รหัสประจำตัว
        URL: /admin/history/oop/filter?start=YYYY-MM-DD&end=YYYY-MM-DD&identity=...
        """
        q_start    = request.args.get("start") or ""
        q_end      = request.args.get("end") or ""
        q_identity = (request.args.get("identity") or "").strip()

        start_dt = self._parse_ui_date(q_start)
        end_dt   = self._parse_ui_date(q_end)
        if end_dt:
            # inclusive สิ้นวัน
            end_dt = end_dt + timedelta(days=1) - timedelta(microseconds=1)

        items = self._collect_items()

        # 🆕 ฟิลเตอร์รหัสประจำตัว (student_id / employee_id) — partial match, case-insensitive
        if q_identity:
            qi = q_identity.lower()
            items = [
                r for r in items
                if qi in str(r.get("student_id") or "").lower()
                or qi in str(r.get("employee_id") or "").lower()
            ]

        # ฟิลเตอร์ช่วงวันที่ (ตาม start_date)
        if start_dt or end_dt:
            filtered: List[Dict] = []
            for row in items:
                sdt = self._as_dt(row.get("start_date"))
                if not sdt:
                    continue
                if start_dt and sdt < start_dt:
                    continue
                if end_dt and sdt > end_dt:
                    continue
                filtered.append(row)
            items = filtered

        # เรียงล่าสุดก่อน
        items.sort(key=lambda x: (self._as_dt(x.get("start_date")) or datetime.min), reverse=True)
        return render_template(
            "pages_history/admin_all_history.html",
            items=items,
            q_start=q_start,
            q_end=q_end,
            q_identity=q_identity,
        )

    # ---------------- internals ----------------
    def _collect_items(self) -> List[Dict]:
        """
        ดึง users ทั้งหมด แล้วรวม histories ของแต่ละ user
        ใช้ service/repo เดิมทั้งหมด (ผ่าน factory)
        """
        repo = self._user_repo()
        svc  = self._hist_svc()

        users = repo.session.execute(
            text("SELECT user_id, name, email, student_id, employee_id FROM users")
        ).fetchall()

        all_items: List[Dict] = []
        for u in users:
            u = dict(u._mapping)
            histories = svc.get_for_user(u["user_id"], returned_only=False)  # คืน list[dict]
            for h in histories:
                row = dict(h)
                row.update({
                    "user_name": u["name"],
                    "student_id": u["student_id"],
                    "employee_id": u["employee_id"],
                })
                all_items.append(row)
        return all_items

    @staticmethod
    def _parse_ui_date(s: Optional[str]) -> Optional[datetime]:
        if not s:
            return None
        try:
            return datetime.strptime(s.strip(), "%Y-%m-%d")
        except Exception:
            return None

    @staticmethod
    def _as_dt(v) -> Optional[datetime]:
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        for fmt in ("%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(str(v), fmt)
            except Exception:
                continue
        return None
