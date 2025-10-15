# app/utils/uow.py
from app.db.db import SessionLocal

class UnitOfWork:
    """Context manager สำหรับจัดการ SQLAlchemy session/transaction แบบอัตโนมัติ"""
    def __enter__(self):
        self.session = SessionLocal()
        return self.session

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()