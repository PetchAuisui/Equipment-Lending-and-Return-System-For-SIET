# init_db.py
from db import Base, engine
import models  # สำคัญ: เพื่อให้ Base เห็นทุกตาราง

if __name__ == "__main__":
    print("Creating database and tables ...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
