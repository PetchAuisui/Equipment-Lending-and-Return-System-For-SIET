from typing import Optional, Dict, Iterable
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.db import SessionLocal

# อนุญาตเฉพาะฟิลด์เหล่านี้เวลา build SQL
ALLOWED_FIELDS: Iterable[str] = {
    "student_id", "employee_id", "name", "email", "phone",
    "major", "member_type", "gender", "password_hash", "role",
    "created_at", "updated_at",
}

class UserRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    # ---------- helper ----------
    def _row_to_dict(self, row) -> Optional[Dict]:
        return dict(row._mapping) if row else None

    def _sanitize(self, data: Dict) -> Dict:
        """กรองเฉพาะฟิลด์ที่อนุญาต"""
        return {k: v for k, v in data.items() if k in ALLOWED_FIELDS}

    def _is_sqlite(self) -> bool:
        try:
            return (self.session.bind.dialect.name or "").lower() == "sqlite"
        except Exception:
            return False

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
        ไม่งั้น insert ใหม่
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
            user_id = row["user_id"]  
            d["updated_at"] = datetime.utcnow()
            # ไม่อัปเดตคีย์หลัก/created_at
            safe_keys = [k for k in d.keys() if k not in {"user_id", "id", "created_at"}]
            sets = ", ".join(f"{k} = :{k}" for k in safe_keys)

            sql = text(f"UPDATE users SET {sets} WHERE user_id = :user_id RETURNING *") 
            d["user_id"] = user_id
            row = self.session.execute(sql, d).first()
            self.session.commit()
            return self._row_to_dict(row)

        # --- insert ---
        return self.add(d)

    def list_users(self, page: int = 1, per_page: int = 10, q: Optional[str] = None) -> Dict:
        """
        ดึง user ทั้งหมด รองรับค้นหา + แบ่งหน้า
        return {"rows": [...], "total": int}
        """
        offset = (page - 1) * per_page
        is_sqlite = self._is_sqlite()

        if q:
            like = f"%{q}%"
            if is_sqlite:
                # ✅ SQLite: ไม่มี ILIKE → ใช้ LIKE แบบไม่แคร์ตัวพิมพ์
                sql = text("""
                    SELECT * FROM users
                    WHERE name       LIKE :kw COLLATE NOCASE
                       OR email      LIKE :kw COLLATE NOCASE
                       OR phone      LIKE :kw COLLATE NOCASE
                       OR student_id LIKE :kw COLLATE NOCASE
                       OR employee_id LIKE :kw COLLATE NOCASE
                    ORDER BY user_id ASC
                    LIMIT :limit OFFSET :offset
                """)
                rows = self.session.execute(sql, {"kw": like, "limit": per_page, "offset": offset}).fetchall()

                count_sql = text("""
                    SELECT COUNT(*) FROM users
                    WHERE name       LIKE :kw COLLATE NOCASE
                       OR email      LIKE :kw COLLATE NOCASE
                       OR phone      LIKE :kw COLLATE NOCASE
                       OR student_id LIKE :kw COLLATE NOCASE
                       OR employee_id LIKE :kw COLLATE NOCASE
                """)
                total = self.session.execute(count_sql, {"kw": like}).scalar()
            else:
                # ✅ Postgres / อื่น ๆ ที่รองรับ ILIKE
                sql = text("""
                    SELECT * FROM users
                    WHERE name ILIKE :kw OR email ILIKE :kw OR phone ILIKE :kw
                       OR student_id ILIKE :kw OR employee_id ILIKE :kw
                    ORDER BY user_id ASC
                    LIMIT :limit OFFSET :offset
                """)
                rows = self.session.execute(sql, {"kw": like, "limit": per_page, "offset": offset}).fetchall()

                count_sql = text("""
                    SELECT COUNT(*) FROM users
                    WHERE name ILIKE :kw OR email ILIKE :kw OR phone ILIKE :kw
                       OR student_id ILIKE :kw OR employee_id ILIKE :kw
                """)
                total = self.session.execute(count_sql, {"kw": like}).scalar()
        else:
            sql = text("""
                SELECT * FROM users
                ORDER BY user_id ASC
                LIMIT :limit OFFSET :offset
            """)
            rows = self.session.execute(sql, {"limit": per_page, "offset": offset}).fetchall()

            count_sql = text("SELECT COUNT(*) FROM users")
            total = self.session.execute(count_sql).scalar()

        return {
            "rows": [self._row_to_dict(r) for r in rows],
            "total": total or 0
        }
