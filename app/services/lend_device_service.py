# app/services/lend_device_service.py
from typing import Dict, List
from app.repositories.lend_device_repository import LendDeviceRepository

class LendDeviceService:
    """
    จัดการข้อมูลอุปกรณ์สำหรับหน้าระบบยืมอุปกรณ์
    - ดึงอุปกรณ์ทั้งหมดพร้อมรูปภาพ
    - รวมตามชื่อ
    - แยกเป็น available / unavailable
    - นับจำนวน (amount)
    - กำหนด status_color
    """

    def __init__(self, repo: LendDeviceRepository | None = None):
        self.repo = repo or LendDeviceRepository()

    def get_all_equipments(self) -> List[dict]:
        """ดึงข้อมูลอุปกรณ์ทั้งหมด (พร้อมรูปภาพ)"""
        return self.repo.get_all_equipments_with_images()

    def get_grouped_equipments_separated(self) -> Dict[str, List[dict]]:
        """รวมข้อมูลอุปกรณ์ตามชื่อ และแยกเป็น available / unavailable"""
        equipments = self.repo.get_all_equipments_with_images()

        grouped = {}
        for e in equipments:
            name = e["name"]
            if name not in grouped:
                grouped[name] = {
                    "name": name,
                    "amount": 0,
                    "image": e["image_path"],
                    "category": e.get("category", ""),
                    "status_color": ""
                }
            if e["status"] == "available":
                grouped[name]["amount"] += 1

        available_items, unavailable_items = [], []
        for item in grouped.values():
            # สี: ถ้ามีเหลือให้ยืม -> โปร่งใส, ถ้าไม่มี -> เหลือง
            item["status_color"] = "transparent" if item["amount"] > 0 else "yellow"
            if item["amount"] > 0:
                available_items.append(item)
            else:
                unavailable_items.append(item)

        return {"available": available_items, "unavailable": unavailable_items}
