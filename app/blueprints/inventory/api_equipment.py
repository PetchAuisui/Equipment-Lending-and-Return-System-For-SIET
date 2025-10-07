from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.services.equipment_service import EquipmentService

api_equipment_bp = Blueprint("api_equipment", __name__, url_prefix="/api/equipments")

class EquipmentAPI(MethodView):
    def __init__(self):
        self.service = EquipmentService()

    def get(self, equipment_id=None):
        if equipment_id:
            eq = self.service.get_equipment(equipment_id)
            if not eq:
                return jsonify({"error": "ไม่พบอุปกรณ์"}), 404
            return jsonify({
                "id": eq.equipment_id,
                "name": eq.name,
                "brand": eq.brand,
                "category": eq.category,
                "status": eq.status
            })
        all_eq = self.service.get_all_equipment()
        return jsonify([
            {"id": e.equipment_id, "name": e.name, "status": e.status}
            for e in all_eq
        ])

    def post(self):
        data = request.get_json()
        eq = self.service.create_equipment(data)
        return jsonify({"message": "เพิ่มอุปกรณ์สำเร็จ", "id": eq.equipment_id}), 201

    def put(self, equipment_id):
        data = request.get_json()
        updated = self.service.update_equipment(equipment_id, data)
        if not updated:
            return jsonify({"error": "ไม่พบอุปกรณ์"}), 404
        return jsonify({"message": "อัปเดตข้อมูลสำเร็จ"})

    def delete(self, equipment_id):
        deleted = self.service.delete_equipment(equipment_id)
        if not deleted:
            return jsonify({"error": "ไม่พบอุปกรณ์"}), 404
        return jsonify({"message": "ลบอุปกรณ์เรียบร้อยแล้ว"})

# ✅ Register routes
api_equipment_bp.add_url_rule(
    "/", view_func=EquipmentAPI.as_view("equipment_list"), methods=["GET", "POST"]
)
api_equipment_bp.add_url_rule(
    "/<int:equipment_id>", view_func=EquipmentAPI.as_view("equipment_detail"), methods=["GET", "PUT", "DELETE"]
)
