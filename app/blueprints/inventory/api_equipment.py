from flask.views import MethodView
from flask import Blueprint, request, Response
from app.db.models import Equipment
from app.db.db import SessionLocal
import json

api_equipment_bp = Blueprint("api_equipment", __name__, url_prefix="/api/equipments")

class EquipmentAPI(MethodView):
    def get(self):
        db = SessionLocal()
        equipments = db.query(Equipment).all()
        result = [
            {"id": e.equipment_id, "name": e.name, "status": e.status}
            for e in equipments
        ]
        return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')

    def post(self):
        db = SessionLocal()
        data = request.get_json()
        eq = Equipment(
            name=data["name"],
            code=data["code"],
            status=data.get("status", "available")
        )
        db.add(eq)
        db.commit()
        db.refresh(eq)
        return Response(
            json.dumps({"message": "เพิ่มอุปกรณ์สำเร็จ", "id": eq.equipment_id}, ensure_ascii=False),
            mimetype='application/json',
            status=201
        )

    def put(self, equipment_id):
        db = SessionLocal()
        eq = db.get(Equipment, equipment_id)
        if not eq:
            return Response(json.dumps({"error": "ไม่พบอุปกรณ์"}, ensure_ascii=False),
                            mimetype='application/json', status=404)

        data = request.get_json()
        for key, value in data.items():
            setattr(eq, key, value)
        db.commit()
        db.refresh(eq)
        return Response(json.dumps({"message": "อัปเดตข้อมูลสำเร็จ"}, ensure_ascii=False),
                        mimetype='application/json')

    def delete(self, equipment_id):
        db = SessionLocal()
        eq = db.get(Equipment, equipment_id)
        if not eq:
            return Response(json.dumps({"error": "ไม่พบอุปกรณ์"}, ensure_ascii=False),
                            mimetype='application/json', status=404)

        db.delete(eq)
        db.commit()
        return Response(json.dumps({"message": "ลบอุปกรณ์เรียบร้อยแล้ว"}, ensure_ascii=False),
                        mimetype='application/json')

# ✅ Register route แบบ class (GET, POST)
api_equipment_bp.add_url_rule("/", view_func=EquipmentAPI.as_view("equipment_api"), methods=["GET", "POST"])

# ✅ Register route สำหรับ PUT / DELETE (ต้องมี parameter id)
api_equipment_bp.add_url_rule("/<int:equipment_id>", view_func=EquipmentAPI.as_view("equipment_api_detail"), methods=["PUT", "DELETE"])
