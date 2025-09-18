from app.db.db import Base, engine
from app.db import models  # 👈 ต้อง import ให้ Base เห็น models

if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")