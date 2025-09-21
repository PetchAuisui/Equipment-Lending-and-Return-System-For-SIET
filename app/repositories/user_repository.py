from typing import Optional, Dict, Iterable
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.db import SessionLocal

# เพื่อกัน key แปลก ๆ หลุดเข้ามาเวลา build SQL
ALLOWED_FIELDS: Iterable[str] = {
    "student_id", "employee_id", "name", "email", "phone",
    "major", "member_type", "gender", "password_hash", "role",
    "created_at", "updated_at",
}

class UserRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    # ---------- helper ----------
    def _row_to_dict(self, row) -> Dict | None:
        return dict(row._mapping) if row else None

    def _sanitize(self, data: Dict) -> Dict:
        """กรองเฉพาะฟิลด์ที่อนุญาต"""
        return {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

    # ---------- readers ----------
    def find_by_email(self, email: str) -> Optional[Dict]:
        sql = text("SELECT * FROM users WHERE email = :email LIMIT 1")
        row = self.session.execute(sql, {"email": email}).first()
        return self._row_to_dict(row)

    def find_by_student_id(self, student_id: str) -> Optional[Dict]:
        sql = text("SELECT * FROM users WHERE student_id = :sid LIMIT 1")
        row = self.session.execute(sql, {"sid": student_id}).first()
        return self._row_to_dict(row)

    def find_by_employee_id(self, employee_id: str) -> Optional[Dict]:
        sql = text("SELECT * FROM users WHERE employee_id = :eid LIMIT 1")
        row = self.session.execute(sql, {"eid": employee_id}).first()
        return self._row_to_dict(row)

    # ---------- writers ----------
    def add(self, data: Dict) -> Dict:
        """สร้างผู้ใช้ใหม่ + เติม created_at/updated_at อัตโนมัติ"""
        d = self._sanitize(dict(data))
        # ถ้าไม่ได้ส่งมา ให้เติมเอง
        d.setdefault("created_at", datetime.utcnow())
        d.setdefault("updated_at", datetime.utcnow())

        cols = ", ".join(d.keys())
        vals = ", ".join(f":{k}" for k in d.keys())
        sql = text(f"INSERT INTO users ({cols}) VALUES ({vals}) RETURNING *")

        try:
            row = self.session.execute(sql, d).first()
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

        return self._row_to_dict(row)

    def upsert_by_unique(self, data: Dict) -> Dict:
        """
        อัปเดตตาม uniq (email/student_id/employee_id) ถ้ามี
        ไม่งั้น insert ใหม่ (ซึ่ง add() จะเติมเวลาให้เอง)
        """
        d = self._sanitize(dict(data))

        # หา record เดิมก่อน
        row = self.find_by_email(d.get("email")) if d.get("email") else None
        if not row and d.get("student_id"):
            row = self.find_by_student_id(d["student_id"])
        if not row and d.get("employee_id"):
            row = self.find_by_employee_id(d["employee_id"])

        if row:
            # --- update ---
            user_id = row["id"]
            d["updated_at"] = datetime.utcnow()  # อัปเดตเวลาแก้ไขทุกครั้ง
            # ไม่อัปเดต id/created_at
            safe_keys = [k for k in d.keys() if k not in {"id", "created_at"}]
            sets = ", ".join(f"{k} = :{k}" for k in safe_keys)

            sql = text(f"UPDATE users SET {sets} WHERE id = :id RETURNING *")
            d["id"] = user_id
            row = self.session.execute(sql, d).first()
            self.session.commit()
            return self._row_to_dict(row)

        # --- insert ---
        return self.add(d)