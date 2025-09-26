# app/models/lend.py
# 📌 ใช้สำหรับสร้าง class แทน "อุปกรณ์ที่สามารถยืมได้" ในระบบ

class Lend:
    def __init__(self, image_path, name, amount):
        # เก็บ path ของรูปอุปกรณ์
        self.image = image_path
        # เก็บชื่ออุปกรณ์
        self.name = name
        # เก็บจำนวนคงเหลือ
        self.amount = amount

    def __repr__(self):
        # ใช้สำหรับ debug เวลา print object
        return f"<Lend name={self.name} amount={self.amount}>"
