from __future__ import annotations
from typing import Optional, Dict, Iterable
from datetime import datetime
import json

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.db import SessionLocal

# อนุญาตเฉพาะฟิลด์เหล่านี้เวลา build SQL
ALLOWED_FIELDS: Iterable[str] = {
    "student_id", "employee_id", "name", "email", "phone",
    "major", "member_type", "gender", "password_hash", "role",
    "created_at", "updated_at",
}

# ฟิลด์ที่ไม่ต้องการเก็บลง audits.diff
AUDIT_EXCLUDE_FIELDS = {"password_hash"}


class UserRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    # ---------- helpers ----------
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

    def _get_by_id(self, user_id: int) -> Optional[Dict]:
        sql = text("SELECT * FROM users WHERE user_id = :uid LIMIT 1")
        row = self.session.execute(sql, {"uid": user_id}).first()
        return self._row_to_dict(row)

    def _insert_audit(
        self,
        *,
        entity_id: int,
        action: str,
        actor_id: Optional[int],
        before: Optional[Dict],
        after: Optional[Dict],
    ) -> None:
        """เขียน log ลง audits โดยตัดฟิลด์อ่อนไหวออก"""
        def _clean(d: Optional[Dict]) -> Optional[Dict]:
            if d is None:
                return None
            return {k: v for k, v in d.items() if k not in AUDIT_EXCLUDE_FIELDS}

        payload = {"before": _clean(before), "after": _clean(after)}
        ts = datetime.utcnow()

        # รองรับทั้ง SQLite และ Postgres
        if self._is_sqlite():
            diff_expr = ":diff"                      # SQLite JSON column รับ text ได้
        else:
            diff_expr = "CAST(:diff AS JSON)"        # Postgres/DB อื่น ๆ

        sql = text(f"""
            INSERT INTO audits (entity_id, action, actor_id, diff, created_at)
            VALUES (:entity_id, :action, :actor_id, {diff_expr}, :ts)
        """)
        self.session.execute(sql, {
            "entity_id": entity_id,
            "action": action,
            "actor_id": actor_id,
            "diff": json.dumps(payload, default=str),
            "ts": ts,
        })

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
    def add(self, data: Dict, *, actor_id: Optional[int] = None, audit: bool = True) -> Dict:
        """สร้างผู้ใช้ใหม่ + เติม created_at/updated_at อัตโนมัติ + บันทึก audit 'created'"""
        d = self._sanitize(dict(data))
        d.setdefault("created_at", datetime.utcnow())
        d.setdefault("updated_at", datetime.utcnow())

        cols = ", ".join(d.keys())
        vals = ", ".join(f":{k}" for k in d.keys())
        sql = text(f"INSERT INTO users ({cols}) VALUES ({vals}) RETURNING *")

        try:
            row = self.session.execute(sql, d).first()
            new_row = self._row_to_dict(row)

            if audit and new_row:
                self._insert_audit(
                    entity_id=new_row["user_id"],
                    action="created",
                    actor_id=actor_id,
                    before=None,
                    after=new_row,
                )

            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

        return new_row

    def update_user(self, user_id: int, changes: Dict, *, actor_id: Optional[int]) -> Optional[Dict]:
        """
        อัปเดตผู้ใช้ตาม user_id แล้วเขียน audit 'updated'
        คืนค่า row หลังอัปเดต หรือ None ถ้าหาไม่เจอ
        """
        before = self._get_by_id(user_id)
        if not before:
            return None

        d = self._sanitize(dict(changes))
        if not d:
            return before  # ไม่มีอะไรจะอัปเดต

        d["updated_at"] = datetime.utcnow()
        safe_keys = [k for k in d.keys() if k not in {"user_id", "id", "created_at"}]
        sets = ", ".join(f"{k} = :{k}" for k in safe_keys)

        sql = text(f"UPDATE users SET {sets} WHERE user_id = :id RETURNING *")
        d["id"] = user_id

        row = self.session.execute(sql, d).first()
        after = self._row_to_dict(row)

        self._insert_audit(
            entity_id=user_id,
            action="updated",
            actor_id=actor_id,
            before=before,
            after=after,
        )
        self.session.commit()
        return after

    def delete_user(self, user_id: int, *, actor_id: Optional[int]) -> bool:
        """
        ลบผู้ใช้ตาม user_id + เขียน audit 'deleted'
        คืน True ถ้าลบได้, False ถ้าไม่พบ
        """
        before = self._get_by_id(user_id)
        if not before:
            return False

        # ลบ
        sql = text("DELETE FROM users WHERE user_id = :uid")
        self.session.execute(sql, {"uid": user_id})

        # audit ลบ (after = None)
        self._insert_audit(
            entity_id=user_id,
            action="deleted",
            actor_id=actor_id,
            before=before,
            after=None,
        )
        self.session.commit()
        return True

    def upsert_by_unique(self, data: Dict, *, actor_id: Optional[int] = None) -> Dict:
        """
        อัปเดตตาม uniq (email/student_id/employee_id) ถ้ามี
        ไม่งั้น insert ใหม่ (และเขียน audit ให้สอดคล้อง)
        """
        d = self._sanitize(dict(data))

        # หา record เดิมก่อน
        row = self.find_by_email(d.get("email")) if d.get("email") else None
        if not row and d.get("student_id"):
            row = self.find_by_student_id(d["student_id"])
        if not row and d.get("employee_id"):
            row = self.find_by_employee_id(d["employee_id"])

        if row:
            user_id = row["user_id"]
            # ใช้ update_user เพื่อให้ได้ audit 'updated'
            updated = self.update_user(user_id, d, actor_id=actor_id)
            return updated or row

        # insert ใหม่ (audit 'created')
        return self.add(d, actor_id=actor_id, audit=True)

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
                # SQLite: ไม่มี ILIKE → ใช้ LIKE + NOCASE
                sql = text("""
                    SELECT * FROM users
                    WHERE name        LIKE :kw COLLATE NOCASE
                       OR email       LIKE :kw COLLATE NOCASE
                       OR phone       LIKE :kw COLLATE NOCASE
                       OR student_id  LIKE :kw COLLATE NOCASE
                       OR employee_id LIKE :kw COLLATE NOCASE
                    ORDER BY user_id ASC
                    LIMIT :limit OFFSET :offset
                """)
                rows = self.session.execute(sql, {
                    "kw": like, "limit": per_page, "offset": offset
                }).fetchall()

                count_sql = text("""
                    SELECT COUNT(*) FROM users
                    WHERE name        LIKE :kw COLLATE NOCASE
                       OR email       LIKE :kw COLLATE NOCASE
                       OR phone       LIKE :kw COLLATE NOCASE
                       OR student_id  LIKE :kw COLLATE NOCASE
                       OR employee_id LIKE :kw COLLATE NOCASE
                """)
                total = self.session.execute(count_sql, {"kw": like}).scalar()
            else:
                # Postgres / อื่น ๆ ที่รองรับ ILIKE
                sql = text("""
                    SELECT * FROM users
                    WHERE name ILIKE :kw OR email ILIKE :kw OR phone ILIKE :kw
                       OR student_id ILIKE :kw OR employee_id ILIKE :kw
                    ORDER BY user_id ASC
                    LIMIT :limit OFFSET :offset
                """)
                rows = self.session.execute(sql, {
                    "kw": like, "limit": per_page, "offset": offset
                }).fetchall()

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
            rows = self.session.execute(sql, {
                "limit": per_page, "offset": offset
            }).fetchall()

            count_sql = text("SELECT COUNT(*) FROM users")
            total = self.session.execute(count_sql).scalar()

        return {
            "rows": [self._row_to_dict(r) for r in rows],
            "total": total or 0
        }
