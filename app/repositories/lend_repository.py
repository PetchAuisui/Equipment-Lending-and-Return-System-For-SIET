# app/repository/lend_repository.py
from app.extensions import db

def create_lend_record(user_id, equipment_id, quantity):
    sql = """
    INSERT INTO lend (user_id, equipment_id, quantity)
    VALUES (?, ?, ?)
    """
    db.session.execute(sql, (user_id, equipment_id, quantity))
    db.session.commit()

def get_lend_by_user(user_id):
    sql = "SELECT * FROM lend WHERE user_id = ?"
    return db.session.execute(sql, (user_id,)).fetchall()
