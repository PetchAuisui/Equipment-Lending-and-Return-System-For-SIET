import json
import os
from models.user import User


class UserRepository:
    def __init__(self, json_path="users.json"):
        self.json_path = json_path
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_all(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [User.from_dict(u) for u in data]

    def save_all(self, users):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, ensure_ascii=False, indent=4)

    def find_by_email(self, email):
        users = self.load_all()
        for u in users:
            if u.email == email:
                return u
        return None
