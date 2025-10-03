สร้าง database ใช้คำสั่ง python3 -m app.db.init_db แก้ไขไฟล์ app/db/init_db.py ลบ app.db ก่อนแก้
เพิ่มข้อมูล       ใช้คำสั่ง python3 -m app.db.insert  แก้ไขไฟล์ app/db/inside.py

![alt text](<ER diagarm.png>)

str = string
int = intreger
nn = not null

table User
    user_id       = id
    name          = ชื่อ str nn
    student_id    = รหัสนักศึกษา str uniqe
    employee_id   = รหัสพนักงาน str uniqe
    email         = email str uniqe nn
    phone         = เบอร์โทร str
    major         = สาขา str
    member_type   = ตำเหน่ง str (student, teacher, staff, )
    gender        = เพศ str
    password_hash = รหัส str nn
    role          = Column(String, nullable=False, default="member")   # ✅ เพิ่มคอลัมน์นี้
    created_at    = เวลาสร้าง DateTime
    updated_at    = เวลาเเก้ไข เเก้ต่อ

table Subject 
    subject_id   = id
    subject_code = รหัสวิชา
    subject_name = ชื่อวิชา

table Section
    section_id   = id
    section_name = ชื่อ sec 1 2 
    subject_id   = FK เชื่อมไป subject

table Instructor
    instructors_id   = id
    subject_id       = FK เชื่อมไป subject
    user_id          = FK เชื่อมไป user