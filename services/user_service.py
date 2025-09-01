from models.user import User


class UserService:
    def __init__(self, repository):
        self.repository = repository
        self.users = self.repository.load_users()

    def validate_data(self, data):
        required_fields = [
            "name", "id_card", "major", "member_type", "phone", "email",
            "address", "password", "confirm_password", "gender"]
        for field in required_fields:
            if field not in data:
                return f"Missing field: {field}"

        if data["password"] != data["confirm_password"]:
            return "Password and Confirm-Password do not match"

        if not data["email"].endswith("@kmitl.ac.th"):
            return "Email must end with @kmitl.ac.th"

        # ใช้ repo ช่วยเช็กซ้ำ เพื่อให้เช็กกับข้อมูลที่เซฟจริง
        if self.repository.find_by_email(data["email"]):
            return "Email already registered"
        if self.repository.find_by_id_card(data["id_card"]):
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
            password=data["password"],
            gender=data["gender"]   
        )

        # อัปเดต list ในเมมโมรี + บันทึกลงไฟล์
        self.users.append(user)
        self.repository.save_users(self.users)

        out = user.to_dict()
        out.pop("password", None)
        return {"message": "Register successful", "user": out}, 201

    def get_all_users(self):
        # รีโหลดล่าสุดจากไฟล์เพื่อให้ตรงกับความจริง
        users = self.repository.load_users()
        safe = []
        for u in users:
            d = u.to_dict()
            d.pop("password", None)
            safe.append(d)
        return safe
