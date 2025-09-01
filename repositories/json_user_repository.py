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
