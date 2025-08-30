class User:
    def __init__(self, name, id_card, major, member_type, phone, email, address, password):
        self.name = name
        self.id_card = id_card
        self.major = major
        self.member_type = member_type
        self.phone = phone
        self.email = email
        self.address = address
        self.password = password  # แนะนำ hash ใน production

    def to_dict(self):
        return {
            "name": self.name,
            "id_card": self.id_card,
            "major": self.major,
            "member_type": self.member_type,
            "phone": self.phone,
            "email": self.email,
            "address": self.address
        }
