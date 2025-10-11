สร้าง database ใช้คำสั่ง python3 -m app.db.init_db แก้ไขไฟล์ app/db/init_db.py ลบ app.db ก่อนแก้
เพิ่มข้อมูล       ใช้คำสั่ง python3 -m app.db.insert  แก้ไขไฟล์ app/db/inside.py

![alt text](<ER diagarm-2.png>)

# Database Schema - Equipment Lending and Return System

## User
- **user_id** (Integer, PK, autoincrement)  
- **name** (String, not null)  
- **student_id** (String, unique, null allowed)  
- **employee_id** (String, unique, null allowed)  
- **email** (String, unique, not null)  
- **phone** (String)  
- **major** (String)  
- **member_type** (String, เช่น student, teacher, staff)  
- **gender** (String)  
- **password_hash** (String, not null)  
- **role** (String, default "member", not null)  
- **created_at** (DateTime)  
- **updated_at** (DateTime)  

**Relationships:**  
- 1 User ↔ 1 Instructor  
- 1 User ↔ N Rent, StockMovement, Return, Notification, Renewal, Audit  

## Subject
- **subject_id** (Integer, PK, autoincrement)  
- **subject_code** (String)  
- **subject_name** (String, not null)  

**Relationships:**  
- 1 Subject ↔ N Rent  
- 1 Subject ↔ N Section  
- 1 Subject ↔ N Instructor  

## Section
- **section_id** (Integer, PK, autoincrement)  
- **section_name** (String)  
- **subject_id** (Integer, FK → Subject.subject_id)  

**Relationships:**  
- N Section ↔ 1 Subject  

## Instructor
- **instructor_id** (Integer, PK, autoincrement)  
- **subject_id** (Integer, FK → Subject.subject_id)  
- **user_id** (Integer, FK → User.user_id)  

**Relationships:**  
- 1 Instructor ↔ 1 User  
- 1 Instructor ↔ 1 Subject  

## Class
- **class_id** (Integer, PK, autoincrement)  
- **class_no** (String, not null)  
- **class_name** (String)  
- **class_location** (String)  

**Relationships:**  
- 1 Class ↔ N Rent  

## Equipment
- **equipment_id** (Integer, PK, autoincrement)  
- **name** (String, not null)  
- **code** (String, unique, not null)  
- **category** (String)  
- **detail** (Text)  
- **brand** (String)  
- **buy_date** (Date)  
- **status** (String: available, rented, maintenance)  
- **created_at** (DateTime)  
- **updated_at** (DateTime)  

**Relationships:**  
- 1 Equipment ↔ N Rent  
- 1 Equipment ↔ N StockMovement  
- 1 Equipment ↔ N Equipment_Image  

## Equipment_Image
- **equipment_image_id** (Integer, PK, autoincrement)  
- **equipment_id** (Integer, FK → Equipment.equipment_id)  
- **image_path** (String, not null)  
- **description** (Text)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 Equipment_Image ↔ 1 Equipment  

## StockMovement
- **movement_id** (Integer, PK, autoincrement)  
- **equipment_id** (Integer, FK → Equipment.equipment_id)  
- **history** (Text, not null)  
- **actor_id** (Integer, FK → User.user_id)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 StockMovement ↔ 1 Equipment  
- 1 StockMovement ↔ 1 User  

## StatusRent
- **status_id** (Integer, PK, autoincrement)  
- **name** (String, unique, not null)  
- **color_code** (String)  

**Relationships:**  
- 1 StatusRent ↔ N Rent  

## Rent
- **rent_id** (Integer, PK, autoincrement)  
- **equipment_id** (Integer, FK → Equipment.equipment_id)  
- **user_id** (Integer, FK → User.user_id)  
- **subject_id** (Integer, FK → Subject.subject_id)  
- **class_id** (Integer, FK → Class.class_id)  
- **start_date** (DateTime, not null)  
- **due_date** (DateTime, not null)  
- **reason** (Text)  
- **status_id** (Integer, FK → StatusRent.status_id, not null)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 Rent ↔ 1 Equipment  
- 1 Rent ↔ 1 User  
- 1 Rent ↔ 1 Subject  
- 1 Rent ↔ 1 Class  
- 1 Rent ↔ 1 StatusRent  
- 1 Rent ↔ 1 Return  
- 1 Rent ↔ N Renewal  

## Return
- **return_id** (Integer, PK, autoincrement)  
- **rent_id** (Integer, FK → Rent.rent_id, unique, not null)  
- **user_id** (Integer, FK → User.user_id, receiver)  
- **return_date** (DateTime, default=datetime.utcnow)  

**Relationships:**  
- 1 Return ↔ 1 Rent  
- 1 Return ↔ 1 User  
- 1 Return ↔ N ItemBroke  

## ItemBroke
- **item_broke_id** (Integer, PK, autoincrement)  
- **return_id** (Integer, FK → Return.return_id)  
- **type** (String: broke/lost)  
- **detail** (Text)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 ItemBroke ↔ 1 Return  
- 1 ItemBroke ↔ N ItemBroke_images  

## ItemBroke_images
- **itemBroke_image_id** (Integer, PK, autoincrement)  
- **item_broke_id** (Integer, FK → ItemBroke.item_broke_id)  
- **image_path** (String, not null)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 ItemBroke_images ↔ 1 ItemBroke  

## Notification
- **notification_id** (Integer, PK, autoincrement)  
- **user_id** (Integer, FK → User.user_id)  
- **channel** (String, not null, เช่น email, line, sms)  
- **template** (String)  
- **payload** (JSON)  
- **send_at** (DateTime, not null)  
- **status** (String, default="scheduled")  
- **created_at** (DateTime)  

**Relationships:**  
- 1 Notification ↔ 1 User  

## Renewal
- **renewal_id** (Integer, PK, autoincrement)  
- **rent_id** (Integer, FK → Rent.rent_id)  
- **old_due** (DateTime)  
- **new_due** (DateTime)  
- **approved_by** (Integer, FK → User.user_id)  
- **created_at** (DateTime)  
- **note** (Text)  

**Relationships:**  
- 1 Renewal ↔ 1 Rent  
- 1 Renewal ↔ 1 User (approver)  

## Audit
- **audit_id** (Integer, PK, autoincrement)  
- **entity_id** (Integer)  
- **action** (String: created/updated/status_change)  
- **actor_id** (Integer, FK → User.user_id)  
- **diff** (JSON)  
- **created_at** (DateTime)  

**Relationships:**  
- 1 Audit ↔ 1 User (actor)  
