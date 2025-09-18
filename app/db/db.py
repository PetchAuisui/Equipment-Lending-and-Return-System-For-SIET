from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///app.db"   # เปลี่ยนเป็น "sqlite:///instance/app.db" ถ้าจัดเก็บในโฟลเดอร์ instance/

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},  # เผื่อใช้กับ Flask
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()
