from app.db.db import SessionLocal
from app.db.models import Subject, StatusRent
from datetime import datetime

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


if __name__ == "__main__":
    seed_subjects()
    seed_status_rents()
