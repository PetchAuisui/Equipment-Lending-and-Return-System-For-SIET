from app.db.db import SessionLocal
from app.db.models import Subject, StatusRent
from datetime import datetime
from app.db.models import Subject, Section


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


if __name__ == "__main__":
    seed_subjects()
    seed_status_rents()
