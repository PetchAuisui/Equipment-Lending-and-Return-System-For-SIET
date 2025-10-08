from app.repositories import lend_device_repository  # ✅ มีอยู่แล้ว

def get_all_equipments():
    return lend_device_repository.get_all_equipments_with_images()

def get_grouped_equipments_separated():
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
                "status_color": "",
                "codes": []     # ✅ เพิ่มบรรทัดนี้ (เตรียม list เก็บรหัส)
            }

        # ✅ เพิ่มบรรทัดนี้ (เก็บ code จากแต่ละอุปกรณ์)
        if e.get("code"):
            grouped[name]["codes"].append(e["code"])

        if e["status"] == "available":
            grouped[name]["amount"] += 1

    available_items = []
    unavailable_items = []
    for item in grouped.values():
        item["status_color"] = "transparent" if item["amount"] > 0 else "yellow"
        if item["amount"] > 0:
            available_items.append(item)
        else:
            unavailable_items.append(item)

    return {
        "available": available_items,
        "unavailable": unavailable_items
    }
