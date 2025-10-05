from app.repositories import lend_device_repository

def get_all_equipments():
    """
    ดึงข้อมูลอุปกรณ์ทั้งหมด
    Returns:
        List ของ dict ทุกแถว
    """
    return lend_device_repository.get_all_equipments_with_images()

def get_grouped_equipments_separated():
    """
    ดึงอุปกรณ์ทั้งหมดแล้วรวมตามชื่อ
    - แยกเป็น available / unavailable
    - amount = จำนวนอุปกรณ์ที่ status='available'
    - เก็บชื่อ, amount, image_path, category, status_color
    Returns:
        dict: {"available": [...], "unavailable": [...]}
    """
    equipments = lend_device_repository.get_all_equipments_with_images()

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

    available_items = []
    unavailable_items = []
    for item in grouped.values():
        # กำหนดสี
        item["status_color"] = "transparent" if item["amount"] > 0 else "yellow"
        # แยก list
        if item["amount"] > 0:
            available_items.append(item)
        else:
            unavailable_items.append(item)

    return {
        "available": available_items,
        "unavailable": unavailable_items
    }
