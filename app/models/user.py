from dataclasses import dataclass, asdict

@dataclass
class User:
    student_id: str             # Primary Key
    name: str
    major: str
    member_type: str
    phone: str
    email: str
    gender: str
    password_hash: str
    role: str = "member"        # member | admin
    status: str = "active"      # active | suspended

    def to_dict(self):
        return asdict(self)

    def public_dict(self):
        d = asdict(self)
        d.pop("password_hash", None)
        return d
