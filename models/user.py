class User:
    def __init__(self, name, id_card, major, member_type, phone, email, address, password, gender=None, id=None):
        self.id = id
        self.name = name
        self.id_card = id_card
        self.major = major
        self.member_type = member_type
        self.phone = phone
        self.email = email
        self.address = address
        self.password = password
        self.gender = gender

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "id_card": self.id_card,
            "major": self.major,
            "member_type": self.member_type,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "password": self.password,
            "gender": self.gender
        }

    @staticmethod
    def from_dict(d):
        return User(
            id=d.get("id"),
            name=d.get("name"),
            id_card=d.get("id_card"),
            gender=d.get("gender"),
            major=d.get("major"),
            member_type=d.get("member_type"),
            phone=d.get("phone"),
            email=d.get("email"),
            address=d.get("address"),
            password=d.get("password")   
        )
