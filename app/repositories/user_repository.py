# app/repositories/user_repository.py
from typing import Dict, Optional
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.db.db import SessionLocal
from app.db.models import User as UserORM
from app.models.user import User

# อนุญาตให้บันทึกเฉพาะ field ที่มีจริงในตาราง users
ALLOWED_FIELDS = {
    "student_id", "employee_id", "name", "email", "phone",
    "major", "member_type", "gender", "password_hash", "role"
}

class UserRepository:
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    def _to_domain(self, o: UserORM) -> User:
        return User(
            student_id=o.student_id,
            name=o.name,
            major=o.major,
            member_type=o.member_type,
            phone=o.phone,
            email=o.email,
            gender=o.gender,
            password_hash=o.password_hash,
            role=o.role,
        )

    def find_by_email(self, email: str) -> Optional[User]:
        row = self.session.query(UserORM).filter(UserORM.email == email).first()
        return self._to_domain(row) if row else None

    def find_by_student_id(self, student_id: str) -> Optional[User]:
        row = self.session.query(UserORM).filter(UserORM.student_id == student_id).first()
        return self._to_domain(row) if row else None

    def upsert(self, data: Dict) -> User:
        # ✅ กรองให้เหลือเฉพาะ field ที่ตาราง users มีจริง
        d = {k: v for k, v in dict(data).items() if k in ALLOWED_FIELDS}

        row = self.session.query(UserORM).filter(
            or_(UserORM.student_id == d["student_id"], UserORM.email == d["email"])
        ).first()

        if row:
            for k, v in d.items():
                setattr(row, k, v)
        else:
            row = UserORM(**d)
            self.session.add(row)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise

        return self._to_domain(row)
