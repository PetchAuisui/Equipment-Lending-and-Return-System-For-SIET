from app.db.db import SessionLocal
from app.db.models import Subject, StatusRent
from datetime import date, datetime, timezone  
from zoneinfo import ZoneInfo 
from app.db.models import Subject, Section
from app.db.models import Class
from app.db.models import Equipment
from app.db.models import Equipment_Image

def seed_subjects():
    db = SessionLocal()
    try:
        subjects = [
            Subject(subject_code="03206111", subject_name="MEASUREMENT AND EVALUATION OF LEARNING"),
            Subject(subject_code="03376124", subject_name="SOFTWARE DESIGN AND DEVELOPMENT 2"),
            Subject(subject_code="03376125", subject_name="DIGITAL MEDIA FOR LEARNING"),
            Subject(subject_code="03376126", subject_name="APPLICATIONS OF MICROCONTROLLERS"),
            Subject(subject_code="03376150", subject_name="SPECIAL TOPICS IN COMPUTER 1"),
            Subject(subject_code="90641009", subject_name="INTERCULTURAL COMMUNICATION SKILLS IN ENGLISH 1"),
            Subject(subject_code="90642208", subject_name="FROM DEV TO THE MOON"),
        ]
        db.add_all(subjects)
        db.commit()
        print("✅ Subjects inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting subjects:", e)
    finally:
        db.close()

def seed_status_rents():
    db = SessionLocal()
    try:
        status_list = [
            StatusRent(name="pending", color_code="#ff9800"),
            StatusRent(name="approved", color_code="#4caf50"),
            StatusRent(name="returned", color_code="#2196f3"),
        ]
        db.add_all(status_list)
        db.commit()
        print("✅ Status rents inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting status rents:", e)
    finally:
        db.close()

def seed_sections():
    db = SessionLocal()
    try:
        # ดึง Subject จาก DB
        subjects = {subj.subject_code: subj.subject_id for subj in db.query(Subject).all()}

        # สร้าง list ของ Section
        sections_list = [
            # ส่วนใหญ่ Section 1
            Section(section_name="Section 1", subject_id=subjects.get("03206111")),
            Section(section_name="Section 2", subject_id=subjects.get("03206111")),
            Section(section_name="Section 1", subject_id=subjects.get("03376124")),
            Section(section_name="Section 2", subject_id=subjects.get("03376124")),
            Section(section_name="Section 1", subject_id=subjects.get("03376125")),
            Section(section_name="Section 2", subject_id=subjects.get("03376125")),
            Section(section_name="Section 1", subject_id=subjects.get("03376126")),
            Section(section_name="Section 2", subject_id=subjects.get("03376126")),
            Section(section_name="Section 1", subject_id=subjects.get("03376150")),
            Section(section_name="Section 2", subject_id=subjects.get("03376150")),
            # วิชา 90641009 มีหลาย Section
            Section(section_name="Section 906", subject_id=subjects.get("90641009")),
            Section(section_name="Section 907", subject_id=subjects.get("90641009")),
            Section(section_name="Section 908", subject_id=subjects.get("90641009")),
            # วิชา 90642208 มีหลาย Section
            Section(section_name="Section 906", subject_id=subjects.get("90642208")),
            Section(section_name="Section 907", subject_id=subjects.get("90642208")),
            Section(section_name="Section 908", subject_id=subjects.get("90642208")),
        ]

        db.add_all(sections_list)
        db.commit()
        print("✅ Sections inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting sections:", e)
    finally:
        db.close()

def seed_classes():
    db = SessionLocal()
    try:
        classes = [
            Class(class_no="101", class_name="ห้องเพลิน", class_location="หน้าลิฟตึก3"),
            Class(class_no="102", class_name="ห้องมะเฟือง", class_location="หน้าลิฟตึก3"),
            Class(class_no="103", class_name="โรงอาหารคณะครุศาสตร์", class_location="ตึกครุศาสตร์"),
            # ===== ตึก 1 ชั้น 1–9, ห้อง 01–05 =====
            Class(class_no="1101", class_name="Maker", class_location="ตึก 1 ชั้น 1"),
            Class(class_no="1102", class_name=None, class_location="ตึก 1 ชั้น 1"),
            Class(class_no="1103", class_name=None, class_location="ตึก 1 ชั้น 1"),
            Class(class_no="1104", class_name=None, class_location="ตึก 1 ชั้น 1"),
            Class(class_no="1105", class_name=None, class_location="ตึก 1 ชั้น 1"),

            Class(class_no="1201", class_name=None, class_location="ตึก 1 ชั้น 2"),
            Class(class_no="1202", class_name=None, class_location="ตึก 1 ชั้น 2"),
            Class(class_no="1203", class_name=None, class_location="ตึก 1 ชั้น 2"),
            Class(class_no="1204", class_name=None, class_location="ตึก 1 ชั้น 2"),
            Class(class_no="1205", class_name=None, class_location="ตึก 1 ชั้น 2"),

            Class(class_no="1301", class_name=None, class_location="ตึก 1 ชั้น 3"),
            Class(class_no="1302", class_name=None, class_location="ตึก 1 ชั้น 3"),
            Class(class_no="1303", class_name=None, class_location="ตึก 1 ชั้น 3"),
            Class(class_no="1304", class_name=None, class_location="ตึก 1 ชั้น 3"),
            Class(class_no="1305", class_name=None, class_location="ตึก 1 ชั้น 3"),

            Class(class_no="1401", class_name=None, class_location="ตึก 1 ชั้น 4"),
            Class(class_no="1402", class_name=None, class_location="ตึก 1 ชั้น 4"),
            Class(class_no="1403", class_name=None, class_location="ตึก 1 ชั้น 4"),
            Class(class_no="1404", class_name=None, class_location="ตึก 1 ชั้น 4"),
            Class(class_no="1405", class_name=None, class_location="ตึก 1 ชั้น 4"),

            Class(class_no="1501", class_name=None, class_location="ตึก 1 ชั้น 5"),
            Class(class_no="1502", class_name=None, class_location="ตึก 1 ชั้น 5"),
            Class(class_no="1503", class_name=None, class_location="ตึก 1 ชั้น 5"),
            Class(class_no="1504", class_name=None, class_location="ตึก 1 ชั้น 5"),
            Class(class_no="1505", class_name=None, class_location="ตึก 1 ชั้น 5"),

            Class(class_no="1601", class_name=None, class_location="ตึก 1 ชั้น 6"),
            Class(class_no="1602", class_name=None, class_location="ตึก 1 ชั้น 6"),
            Class(class_no="1603", class_name=None, class_location="ตึก 1 ชั้น 6"),
            Class(class_no="1604", class_name=None, class_location="ตึก 1 ชั้น 6"),
            Class(class_no="1605", class_name=None, class_location="ตึก 1 ชั้น 6"),

            Class(class_no="1701", class_name=None, class_location="ตึก 1 ชั้น 7"),
            Class(class_no="1702", class_name=None, class_location="ตึก 1 ชั้น 7"),
            Class(class_no="1703", class_name=None, class_location="ตึก 1 ชั้น 7"),
            Class(class_no="1704", class_name=None, class_location="ตึก 1 ชั้น 7"),
            Class(class_no="1705", class_name=None, class_location="ตึก 1 ชั้น 7"),

            Class(class_no="1801", class_name=None, class_location="ตึก 1 ชั้น 8"),
            Class(class_no="1802", class_name=None, class_location="ตึก 1 ชั้น 8"),
            Class(class_no="1803", class_name=None, class_location="ตึก 1 ชั้น 8"),
            Class(class_no="1804", class_name=None, class_location="ตึก 1 ชั้น 8"),
            Class(class_no="1805", class_name=None, class_location="ตึก 1 ชั้น 8"),

            Class(class_no="1901", class_name=None, class_location="ตึก 1 ชั้น 9"),
            Class(class_no="1902", class_name=None, class_location="ตึก 1 ชั้น 9"),
            Class(class_no="1903", class_name=None, class_location="ตึก 1 ชั้น 9"),
            Class(class_no="1904", class_name=None, class_location="ตึก 1 ชั้น 9"),
            Class(class_no="1905", class_name=None, class_location="ตึก 1 ชั้น 9"),

            # ===== ตึก 2 ชั้น 1–6, ห้อง 01–05 =====
            Class(class_no="2101", class_name=None, class_location="ตึก 2 ชั้น 1"),
            Class(class_no="2102", class_name=None, class_location="ตึก 2 ชั้น 1"),
            Class(class_no="2103", class_name=None, class_location="ตึก 2 ชั้น 1"),
            Class(class_no="2104", class_name=None, class_location="ตึก 2 ชั้น 1"),
            Class(class_no="2105", class_name=None, class_location="ตึก 2 ชั้น 1"),

            Class(class_no="2201", class_name=None, class_location="ตึก 2 ชั้น 2"),
            Class(class_no="2202", class_name=None, class_location="ตึก 2 ชั้น 2"),
            Class(class_no="2203", class_name=None, class_location="ตึก 2 ชั้น 2"),
            Class(class_no="2204", class_name=None, class_location="ตึก 2 ชั้น 2"),
            Class(class_no="2205", class_name=None, class_location="ตึก 2 ชั้น 2"),

            Class(class_no="2301", class_name=None, class_location="ตึก 2 ชั้น 3"),
            Class(class_no="2302", class_name=None, class_location="ตึก 2 ชั้น 3"),
            Class(class_no="2303", class_name=None, class_location="ตึก 2 ชั้น 3"),
            Class(class_no="2304", class_name=None, class_location="ตึก 2 ชั้น 3"),
            Class(class_no="2305", class_name=None, class_location="ตึก 2 ชั้น 3"),

            Class(class_no="2401", class_name=None, class_location="ตึก 2 ชั้น 4"),
            Class(class_no="2402", class_name=None, class_location="ตึก 2 ชั้น 4"),
            Class(class_no="2403", class_name=None, class_location="ตึก 2 ชั้น 4"),
            Class(class_no="2404", class_name=None, class_location="ตึก 2 ชั้น 4"),
            Class(class_no="2405", class_name=None, class_location="ตึก 2 ชั้น 4"),

            Class(class_no="2501", class_name=None, class_location="ตึก 2 ชั้น 5"),
            Class(class_no="2502", class_name=None, class_location="ตึก 2 ชั้น 5"),
            Class(class_no="2503", class_name=None, class_location="ตึก 2 ชั้น 5"),
            Class(class_no="2504", class_name=None, class_location="ตึก 2 ชั้น 5"),
            Class(class_no="2505", class_name=None, class_location="ตึก 2 ชั้น 5"),

            Class(class_no="2601", class_name=None, class_location="ตึก 2 ชั้น 6"),
            Class(class_no="2602", class_name=None, class_location="ตึก 2 ชั้น 6"),
            Class(class_no="2603", class_name=None, class_location="ตึก 2 ชั้น 6"),
            Class(class_no="2604", class_name=None, class_location="ตึก 2 ชั้น 6"),
            Class(class_no="2605", class_name=None, class_location="ตึก 2 ชั้น 6"),

            # ตึก 3 ชั้น 1–6, ห้อง 01–05
            Class(class_no="3101", class_name=None, class_location="ตึก 3 ชั้น 1"),
            Class(class_no="3102", class_name=None, class_location="ตึก 3 ชั้น 1"),
            Class(class_no="3103", class_name=None, class_location="ตึก 3 ชั้น 1"),
            Class(class_no="3104", class_name=None, class_location="ตึก 3 ชั้น 1"),
            Class(class_no="3105", class_name=None, class_location="ตึก 3 ชั้น 1"),

            Class(class_no="3201", class_name=None, class_location="ตึก 3 ชั้น 2"),
            Class(class_no="3202", class_name=None, class_location="ตึก 3 ชั้น 2"),
            Class(class_no="3203", class_name=None, class_location="ตึก 3 ชั้น 2"),
            Class(class_no="3204", class_name=None, class_location="ตึก 3 ชั้น 2"),
            Class(class_no="3205", class_name=None, class_location="ตึก 3 ชั้น 2"),

            Class(class_no="3301", class_name=None, class_location="ตึก 3 ชั้น 3"),
            Class(class_no="3302", class_name=None, class_location="ตึก 3 ชั้น 3"),
            Class(class_no="3303", class_name=None, class_location="ตึก 3 ชั้น 3"),
            Class(class_no="3304", class_name=None, class_location="ตึก 3 ชั้น 3"),
            Class(class_no="3305", class_name=None, class_location="ตึก 3 ชั้น 3"),

            Class(class_no="3401", class_name=None, class_location="ตึก 3 ชั้น 4"),
            Class(class_no="3402", class_name=None, class_location="ตึก 3 ชั้น 4"),
            Class(class_no="3403", class_name=None, class_location="ตึก 3 ชั้น 4"),
            Class(class_no="3404", class_name=None, class_location="ตึก 3 ชั้น 4"),
            Class(class_no="3405", class_name=None, class_location="ตึก 3 ชั้น 4"),

            Class(class_no="3501", class_name=None, class_location="ตึก 3 ชั้น 5"),
            Class(class_no="3502", class_name=None, class_location="ตึก 3 ชั้น 5"),
            Class(class_no="3503", class_name=None, class_location="ตึก 3 ชั้น 5"),
            Class(class_no="3504", class_name=None, class_location="ตึก 3 ชั้น 5"),
            Class(class_no="3505", class_name=None, class_location="ตึก 3 ชั้น 5"),

            Class(class_no="3601", class_name=None, class_location="ตึก 3 ชั้น 6"),
            Class(class_no="3602", class_name=None, class_location="ตึก 3 ชั้น 6"),
            Class(class_no="3603", class_name=None, class_location="ตึก 3 ชั้น 6"),
            Class(class_no="3604", class_name=None, class_location="ตึก 3 ชั้น 6"),
            Class(class_no="3605", class_name=None, class_location="ตึก 3 ชั้น 6"),
        ]

        db.add_all(classes)
        db.commit()
        print(f"✅ Classes inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting classes:", e)
    finally:
        db.close()

def seed_equipments():
    db = SessionLocal()
    try:
        equipments = [
            Equipment(
                name="Projector Epson X123",
                code="PRJ001",
                category="Projector",
                detail="Projector สำหรับห้องเรียน",
                brand="Epson",
                buy_date=date(2021, 3, 15),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Laptop Dell Inspiron 15",
                code="LAP001",
                category="Laptop",
                detail="Laptop สำหรับใช้งานทั่วไป",
                brand="Dell",
                buy_date=date(2022, 1, 10),
                status="rented",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Camera Canon EOS 200D",
                code="CAM001",
                category="Camera",
                detail="กล้อง DSLR สำหรับถ่ายภาพโครงการ",
                brand="Canon",
                buy_date=date(2020, 7, 5),
                status="maintenance",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="ปลั๊กสามตา 3 ช่อง",
                code="PLG001",
                category="Office Supplies",
                detail="ปลั๊กไฟสามช่อง สำหรับใช้ในห้องเรียนหรือสำนักงาน",
                brand="Panasonic",
                buy_date=date(2022, 5, 10),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="สาย HDMI 2 เมตร",
                code="HDM001",
                category="Cables",
                detail="สาย HDMI สำหรับต่อโปรเจคเตอร์หรือจอคอมพิวเตอร์",
                brand="Ugreen",
                buy_date=date(2022, 6, 5),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Mouse Logitech M220",
                code="MOU001",
                category="Peripheral",
                detail="เมาส์ไร้สาย ใช้กับคอมพิวเตอร์",
                brand="Logitech",
                buy_date=date(2021, 8, 12),
                status="rented",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Keyboard Microsoft Wired",
                code="KEY001",
                category="Peripheral",
                detail="คีย์บอร์ดแบบสาย ใช้กับคอมพิวเตอร์",
                brand="Microsoft",
                buy_date=date(2020, 11, 3),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="USB Hub 4 Port",
                code="USB001",
                category="Peripheral",
                detail="USB Hub สำหรับเชื่อมต่ออุปกรณ์หลายชิ้น",
                brand="Anker",
                buy_date=date(2022, 2, 20),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="ปลั๊กพ่วง 5 ช่อง",
                code="PLG002",
                category="Office Supplies",
                detail="ปลั๊กไฟพ่วง 5 ช่อง พร้อมสวิทช์ปิด/เปิด",
                brand="Huntkey",
                buy_date=date(2021, 9, 15),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="สาย VGA 1.5 เมตร",
                code="VGA001",
                category="Cables",
                detail="สาย VGA สำหรับต่อคอมพิวเตอร์",
                brand="Ugreen",
                buy_date=date(2022, 3, 10),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="สาย USB-C 1 เมตร",
                code="USB002",
                category="Cables",
                detail="สาย USB-C สำหรับชาร์จและโอนข้อมูล",
                brand="Anker",
                buy_date=date(2022, 7, 18),
                status="rented",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="ชุดหูฟัง Logitech H390",
                code="AUD001",
                category="Audio",
                detail="หูฟังพร้อมไมโครโฟน สำหรับประชุมออนไลน์",
                brand="Logitech",
                buy_date=date(2021, 11, 5),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="ไมโครโฟน USB Condenser",
                code="AUD002",
                category="Audio",
                detail="ไมโครโฟน USB สำหรับบันทึกเสียง",
                brand="Fifine",
                buy_date=date(2022, 1, 12),
                status="maintenance",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Adapter HDMI to VGA",
                code="HDM002",
                category="Cables",
                detail="อะแดปเตอร์แปลงสัญญาณ HDMI เป็น VGA",
                brand="Ugreen",
                buy_date=date(2021, 6, 8),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Mouse Wireless HP X3000",
                code="MOU002",
                category="Peripheral",
                detail="เมาส์ไร้สาย ใช้กับคอมพิวเตอร์",
                brand="HP",
                buy_date=date(2021, 12, 2),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Keyboard Logitech K120",
                code="KEY002",
                category="Peripheral",
                detail="คีย์บอร์ดแบบสาย ใช้กับคอมพิวเตอร์",
                brand="Logitech",
                buy_date=date(2020, 10, 10),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Flash Drive 32GB",
                code="USB003",
                category="Peripheral",
                detail="USB Flash Drive สำหรับเก็บข้อมูล",
                brand="SanDisk",
                buy_date=date(2021, 5, 20),
                status="rented",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="สาย Audio 3.5 mm",
                code="AUD003",
                category="Cables",
                detail="สาย Audio สำหรับต่อเครื่องเสียง",
                brand="Ugreen",
                buy_date=date(2021, 8, 15),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="Power Bank 10000mAh",
                code="ACC001",
                category="Accessories",
                detail="แบตสำรอง สำหรับชาร์จอุปกรณ์พกพา",
                brand="Xiaomi",
                buy_date=date(2022, 2, 5),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="สาย LAN Cat6 5 เมตร",
                code="CAB001",
                category="Cables",
                detail="สายแลน สำหรับต่อคอมพิวเตอร์และอุปกรณ์เครือข่าย",
                brand="TP-Link",
                buy_date=date(2022, 3, 8),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            ),
            Equipment(
                name="ปลั๊กพ่วง 6 ช่อง",
                code="PLG003",
                category="Office Supplies",
                detail="ปลั๊กไฟพ่วง 6 ช่อง พร้อมสวิทช์ปิด/เปิด",
                brand="Huntkey",
                buy_date=date(2022, 4, 12),
                status="available",
                created_at=datetime.now(ZoneInfo("Asia/Bangkok"))
            )
        ]

        db.add_all(equipments)
        db.commit()
        print(f"✅ {len(equipments)} Equipment records inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting equipments:", e)
    finally:
        db.close()

def seed_equipment_images():
    db = SessionLocal()
    try:
        images = [
            Equipment_Image(equipment_id=1, image_path="images/device/Projector_Epson_X123.jpg", description="Projector Epson X123", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=2, image_path="images/device/Laptop_Dell_Inspiron_15.jpg", description="Laptop Dell Inspiron 15", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=3, image_path="images/device/Camera_Canon_EOS_200D.jpg", description="Camera Canon EOS 200D", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=4, image_path="images/device/ปลั๊กสามตา_3_ช่อง.jpg", description="ปลั๊กสามตา 3 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=5, image_path="images/device/สาย_HDMI_2_เมตร.jpg", description="สาย HDMI 2 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=6, image_path="images/device/Mouse_Logitech_M220.jpg", description="Mouse Logitech M220", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=7, image_path="images/device/Keyboard_Microsoft_Wired.jpg", description="Keyboard Microsoft Wired", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=8, image_path="images/device/USB_Hub_4_Port.jpg", description="USB Hub 4 Port", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=9, image_path="images/device/ปลั๊กพ่วง_5_ช่อง.jpg", description="ปลั๊กพ่วง 5 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=10, image_path="images/device/สาย_VGA_1.5_เมตร.jpg", description="สาย VGA 1.5 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=11, image_path="images/device/สาย_USB-C_1_เมตร.jpg", description="สาย USB-C 1 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=12, image_path="images/device/ชุดหูฟัง_Logitech_H390.jpg", description="ชุดหูฟัง Logitech H390", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=13, image_path="images/device/ไมโครโฟน_USB_Condenser.jpg", description="ไมโครโฟน USB Condenser", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=14, image_path="images/device/Adapter_HDMI_to_VGA.jpg", description="Adapter HDMI to VGA", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=15, image_path="images/device/Mouse_Wireless_HP_X3000.jpg", description="Mouse Wireless HP X3000", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=16, image_path="images/device/Keyboard_Logitech_K120.jpg", description="Keyboard Logitech K120", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=17, image_path="images/device/Flash_Drive_32GB.jpg", description="Flash Drive 32GB", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=18, image_path="images/device/สาย_Audio_35_mm.jpg", description="สาย Audio 3.5 mm", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=19, image_path="images/device/Power_Bank_10000mAh.jpg", description="Power Bank 10000mAh", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=20, image_path="images/device/สาย_LAN_Cat6_5_เมตร.jpg", description="สาย LAN Cat6 5 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            Equipment_Image(equipment_id=21, image_path="images/device/ปลั๊กพ่วง_6_ช่อง.jpg", description="ปลั๊กพ่วง 6 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
        ]
        
        db.add_all(images)
        db.commit()
        print(f"✅ {len(images)} Equipment_Image records inserted successfully")
    except Exception as e:
        db.rollback()
        print("❌ Error inserting equipment images:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_subjects()
    seed_status_rents()
    seed_sections()
    seed_classes()
    seed_equipments()
    seed_equipment_images()
