from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def login(self, email, password):
        user = self.user_repo.find_by_email(email)
        if not user:
            return {"error": "Email not found"}, 404
        if user.password != password:
            return {"error": "Incorrect password"}, 401

        data = user.to_dict()
        data.pop("password", None)   # ไม่ส่งรหัสกลับ
        return {"message": "Login successful", "user": data}, 200
