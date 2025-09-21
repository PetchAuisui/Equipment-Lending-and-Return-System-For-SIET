# app/repositories/user_repository.py
from typing import Optional, Dict
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.db import SessionLocal
class UserRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    # ---------- helper ----------
    def _row_to_dict(self, row) -> Dict:
        return dict(row._mapping) if row else None

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
        cols = ", ".join(data.keys())
        vals = ", ".join(f":{k}" for k in data.keys())
        sql = text(f"INSERT INTO users ({cols}) VALUES ({vals}) RETURNING *")
        try:
            row = self.session.execute(sql, data).first()
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise
        return self._row_to_dict(row)

    def upsert_by_unique(self, data: Dict) -> Dict:
        # ลองหา record เดิมก่อน
        row = self.find_by_email(data.get("email"))
        if not row and data.get("student_id"):
            row = self.find_by_student_id(data["student_id"])
        if not row and data.get("employee_id"):
            row = self.find_by_employee_id(data["employee_id"])

        if row:
            # update
            sets = ", ".join(f"{k} = :{k}" for k in data.keys())
            sql = text(f"UPDATE users SET {sets} WHERE id = :id RETURNING *")
            data["id"] = row["id"]
            row = self.session.execute(sql, data).first()
        else:
            # insert
            row = self.add(data)

        self.session.commit()
        return self._row_to_dict(row)