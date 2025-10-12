from __future__ import annotations
from typing import Optional, Dict, Iterable
from datetime import datetime, timezone
import json

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
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

    def _dialect(self) -> str:
        try:
            return (self.session.bind.dialect.name or "").lower()
        except Exception:
            return ""

    def _is_sqlite(self) -> bool:
        return self._dialect() == "sqlite"

    def _is_postgres(self) -> bool:
        d = self._dialect()
        return d in {"postgresql", "postgres"}

    def _now(self) -> datetime:
        # ใช้ UTC aware datetime
        return datetime.now(timezone.utc)

    def _get_by_id(self, user_id: int) -> Optional[Dict]:
        sql = text("SELECT * FROM users WHERE user_id = :uid LIMIT 1")
        row = self.session.execute(sql, {"uid": user_id}).first()
        return self._row_to_dict(row)

    # ===== ensure ตาราง user_audits (กันล้ม ถ้ายังไม่มี) =====
    def _ensure_user_audits_table(self) -> None:
        if self._is_sqlite():
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS user_audits (
                    audit_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    action     TEXT NOT NULL,
                    actor_id   INTEGER,
                    diff       TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
        elif self._is_postgres():
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS user_audits (
                    audit_id   SERIAL PRIMARY KEY,
                    user_id    INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    action     VARCHAR NOT NULL,
                    actor_id   INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    diff       JSON,
                    created_at TIMESTAMPTZ NOT NULL
                )
            """)
        else:
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS user_audits (
                    audit_id   INTEGER PRIMARY KEY,
                    user_id    INTEGER NOT NULL,
                    action     VARCHAR(255) NOT NULL,
                    actor_id   INTEGER,
                    diff       TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
        self.session.execute(create_sql)

    def _insert_user_audit(
        self,
        *,
        target_user_id: int,
        action: str,
        actor_id: Optional[int],
        before: Optional[Dict],
        after: Optional[Dict],
    ) -> None:
        """เขียน log ลง user_audits ตาม schema ใหม่ และตัดฟิลด์อ่อนไหวออก"""
        def _clean(d: Optional[Dict]) -> Optional[Dict]:
            if d is None:
                return None
            return {k: v for k, v in d.items() if k not in AUDIT_EXCLUDE_FIELDS}

        payload = {"before": _clean(before), "after": _clean(after)}
        ts = self._now()

        # expression ของ JSON ต่อ dialect
        if self._is_sqlite():
            diff_expr = ":diff"            # TEXT/JSON (SQLite)
        elif self._is_postgres():
            diff_expr = ":diff::json"      # JSON (Postgres)
        else:
            diff_expr = "CAST(:diff AS VARCHAR)"

        sql = text(f"""
            INSERT INTO user_audits (user_id, action, actor_id, diff, created_at)
            VALUES (:user_id, :action, :actor_id, {diff_expr}, :ts)
        """)
        params = {
            "user_id": target_user_id,
            "action": action,
            "actor_id": actor_id,
            "diff": json.dumps(payload, default=str),
            "ts": ts,
        }

        try:
            self._ensure_user_audits_table()
            self.session.execute(sql, params)
        except OperationalError as e:
            # กันเคส race condition/no table
            msg = str(e).lower()
            if ("no such table" in msg and "user_audits" in msg) or ("relation" in msg and "user_audits" in msg and "does not exist" in msg):
                self._ensure_user_audits_table()
                self.session.execute(sql, params)
            else:
                raise

    # ---------- readers ----------
    def find_by_id(self, user_id: int) -> Optional[Dict]:
        return self._get_by_id(user_id)

    def find_by_identity(self, identity: str) -> Optional[Dict]:
        row = self.find_by_student_id(identity)
        return row or self.find_by_employee_id(identity)

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
        d = self._sanitize(dict(data))
        now_ = self._now()
        d.setdefault("created_at", now_)
        d.setdefault("updated_at", now_)

        cols = ", ".join(d.keys())
        vals = ", ".join(f":{k}" for k in d.keys())
        sql = text(f"INSERT INTO users ({cols}) VALUES ({vals}) RETURNING *")

        try:
            row = self.session.execute(sql, d).first()
            new_row = self._row_to_dict(row)

            if audit and new_row:
                self._insert_user_audit(
                    target_user_id=new_row["user_id"],
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
        before = self._get_by_id(user_id)
        if not before:
            return None

        d = self._sanitize(dict(changes))
        if not d:
            return before

        # ตัดค่าที่ไม่เปลี่ยนออก
        changeset = {k: v for k, v in d.items() if before.get(k) != v}
        if not changeset:
            return before

        changeset["updated_at"] = self._now()
        safe_keys = [k for k in changeset.keys() if k not in {"user_id", "id", "created_at"}]
        sets = ", ".join(f"{k} = :{k}" for k in safe_keys)

        sql = text(f"UPDATE users SET {sets} WHERE user_id = :id RETURNING *")
        changeset["id"] = user_id

        row = self.session.execute(sql, changeset).first()
        after = self._row_to_dict(row)

        self._insert_user_audit(
            target_user_id=user_id,
            action="updated",
            actor_id=actor_id,
            before=before,
            after=after,
        )
        self.session.commit()
        return after

    def delete_user(self, user_id: int, *, actor_id: Optional[int]) -> bool:
        before = self._get_by_id(user_id)
        if not before:
            return False

        self.session.execute(text("DELETE FROM users WHERE user_id = :uid"), {"uid": user_id})

        self._insert_user_audit(
            target_user_id=user_id,
            action="deleted",
            actor_id=actor_id,
            before=before,
            after=None,
        )
        self.session.commit()
        return True

    def upsert_by_unique(self, data: Dict, *, actor_id: Optional[int] = None) -> Dict:
        d = self._sanitize(dict(data))

        row = self.find_by_email(d.get("email")) if d.get("email") else None
        if not row and d.get("student_id"):
            row = self.find_by_student_id(d["student_id"])
        if not row and d.get("employee_id"):
            row = self.find_by_employee_id(d["employee_id"])

        if row:
            user_id = row["user_id"]
            updated = self.update_user(user_id, d, actor_id=actor_id)
            return updated or row

        return self.add(d, actor_id=actor_id, audit=True)

    def list_users(self, page: int = 1, per_page: int = 10, q: Optional[str] = None) -> Dict:
        offset = (page - 1) * per_page
        is_sqlite = self._is_sqlite()

        if q:
            like = f"%{q}%"
            if is_sqlite:
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
                rows = self.session.execute(sql, {"kw": like, "limit": per_page, "offset": offset}).fetchall()

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

        return {"rows": [self._row_to_dict(r) for r in rows], "total": int(total or 0)}
