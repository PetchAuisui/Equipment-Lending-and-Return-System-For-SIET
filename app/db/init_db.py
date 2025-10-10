from app.db import models  # ✅ สำคัญมาก ต้อง import ก่อนสร้างตาราง


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")