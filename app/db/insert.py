from app.db.db import Base
Base.metadata.clear()  # ✅ เคลียร์ mapping ซ้ำก่อนทุกครั้ง

from app.db.db import SessionLocal
from app.db.models import Subject, StatusRent, Section, Equipment, EquipmentImage
from datetime import date, datetime, timezone  
from zoneinfo import ZoneInfo 




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
            StatusRent(name="approved", color_code="#8840d1"),
            StatusRent(name="returned", color_code="#2196f3"),
            StatusRent(name="succeed", color_code="#4caf50"),
            StatusRent(name="pending  extend time", color_code="#ff9800"),
            StatusRent(name="approved extend time", color_code="#8840d1"),
            StatusRent(name="cancle extend time", color_code="#f44336"),
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
                name="Projector Epson X123",
                code="PRJ002",
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
            EquipmentImage(equipment_id=1, image_path="images/device/Projector_Epson_X123.jpg", description="Projector Epson X123", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=2, image_path="images/device/Laptop_Dell_Inspiron_15.jpg", description="Laptop Dell Inspiron 15", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=3, image_path="images/device/Camera_Canon_EOS_200D.jpg", description="Camera Canon EOS 200D", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=4, image_path="images/device/ปลั๊กสามตา_3_ช่อง.jpg", description="ปลั๊กสามตา 3 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=5, image_path="images/device/สาย_HDMI_2_เมตร.jpg", description="สาย HDMI 2 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=6, image_path="images/device/Mouse_Logitech_M220.jpg", description="Mouse Logitech M220", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=7, image_path="images/device/Keyboard_Microsoft_Wired.jpg", description="Keyboard Microsoft Wired", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=8, image_path="images/device/USB_Hub_4_Port.jpg", description="USB Hub 4 Port", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=9, image_path="images/device/ปลั๊กพ่วง_5_ช่อง.jpg", description="ปลั๊กพ่วง 5 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=10, image_path="images/device/สาย_VGA_1.5_เมตร.jpg", description="สาย VGA 1.5 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=11, image_path="images/device/สาย_USB-C_1_เมตร.jpg", description="สาย USB-C 1 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=12, image_path="images/device/ชุดหูฟัง_Logitech_H390.jpg", description="ชุดหูฟัง Logitech H390", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=13, image_path="images/device/ไมโครโฟน_USB_Condenser.jpg", description="ไมโครโฟน USB Condenser", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=14, image_path="images/device/Adapter_HDMI_to_VGA.jpg", description="Adapter HDMI to VGA", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=15, image_path="images/device/Mouse_Wireless_HP_X3000.jpg", description="Mouse Wireless HP X3000", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=16, image_path="images/device/Keyboard_Logitech_K120.jpg", description="Keyboard Logitech K120", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=17, image_path="images/device/Flash_Drive_32GB.jpg", description="Flash Drive 32GB", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=18, image_path="images/device/สาย_Audio_35_mm.jpg", description="สาย Audio 3.5 mm", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=19, image_path="images/device/Power_Bank_10000mAh.jpg", description="Power Bank 10000mAh", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=20, image_path="images/device/สาย_LAN_Cat6_5_เมตร.jpg", description="สาย LAN Cat6 5 เมตร", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
            EquipmentImage(equipment_id=21, image_path="images/device/ปลั๊กพ่วง_6_ช่อง.jpg", description="ปลั๊กพ่วง 6 ช่อง", created_at=datetime.now(ZoneInfo("Asia/Bangkok"))),
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
    seed_equipments()
    seed_equipment_images()
