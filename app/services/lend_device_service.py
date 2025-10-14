from app.repositories.lend_device_repository import LendDeviceRepository

def get_grouped_equipments_separated():
    repo = LendDeviceRepository()
    equipments = repo.get_all_equipments_with_images()

    grouped = {}

    for e in equipments:
        name = e["name"]
        code = e.get("code")
        status = str(e.get("status", "")).lower()

        # ✅ ถ้ายังไม่มี key นี้ให้สร้างก่อน
        if name not in grouped:
            grouped[name] = {
                "equipment_id": e.get("equipment_id"),
                "name": name,
                "amount": 0,                 # จำนวน "พร้อมใช้งาน"
                "total": 0,                  # ✅ เพิ่มจำนวนรวมทั้งหมด
                "image": e["image_path"],
                "category": e.get("category", ""),
                "brand": e.get("brand", ""),
                "detail": e.get("detail", ""),
                "buy_date": e.get("buy_date", ""),
                "confirm": e.get("confirm", False),
                "status": status,
                "codes": []
            }

        # ✅ นับทุกสถานะ (รวม)
        grouped[name]["total"] += 1

        # ✅ นับเฉพาะที่พร้อมใช้งาน
        if status in ["available", "พร้อมใช้งาน"]:
            grouped[name]["amount"] += 1
            if code:
                grouped[name]["codes"].append(code)

    available_items = []
    unavailable_items = []

    for item in grouped.values():
        item["status_color"] = "transparent" if item["amount"] > 0 else "yellow"
        if item["amount"] > 0:
            available_items.append(item)
        else:
            unavailable_items.append(item)

    repo.close()
    return {"available": available_items, "unavailable": unavailable_items}
