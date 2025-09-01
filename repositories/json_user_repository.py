import json
import os
from models.user import User
from repositories.base_repository import BaseUserRepository

DATA_FILE = "users.json"


class JsonUserRepository(BaseUserRepository):
    def load_users(self):
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [User.from_dict(u) for u in data]

    def save_users(self, users):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, ensure_ascii=False, indent=4)

    def find_by_email(self, email):
        for u in self.load_users():
            if u.email == email:
                return u
        return None
    
    def find_by_id_card(self, id_card):
        for u in self.load_users():
            # เผื่อข้อมูลเก่าบางตัวไม่มี id_card
            if getattr(u, "id_card", None) == id_card:
                return u
        return None