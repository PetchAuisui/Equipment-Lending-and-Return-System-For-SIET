from models.user import User

class UserService:
    def __init__(self, repository):
        self.repository = repository
        self.users = self.repository.load_users()

    def validate_data(self, data):
        required_fields = ["name","id_card","major","member_type","phone","email","address","password","confirm_password"]
        for field in required_fields:
            if field not in data:
                return f"Missing field: {field}"

        if data["password"] != data["confirm_password"]:
            return "Password and Confirm-Password do not match"

        if not data["email"].endswith("@kmitl.ac.th"):
            return "Email must end with @kmitl.ac.th"

        for u in self.users:
            if u.email == data["email"]:
                return "Email already registered"
            if u.id_card == data["id_card"]:
                return "ID card already registered"

        return None

    def register(self, data):
        error = self.validate_data(data)
        if error:
            return {"error": error}, 400

        user = User(
            name=data["name"],
            id_card=data["id_card"],
            major=data["major"],
            member_type=data["member_type"],
            phone=data["phone"],
            email=data["email"],
            address=data["address"],
            password=data["password"]
        )
        self.users.append(user)
        self.repository.save_users(self.users)
        return {"message": "Register successful", "user": user.to_dict()}, 201

    def get_all_users(self):
        return [u.to_dict() for u in self.users]
