from app.repositories import lend_device_repository

def get_all_equipments():
    """
    ดึงข้อมูลอุปกรณ์ทั้งหมดจาก repository
    Returns:
        List ของ dict/objects ทุกแถว
    """
    return lend_device_repository.get_all_equipments_with_images()


def get_grouped_equipments():
    """
    ดึงอุปกรณ์ทั้งหมดแล้วรวมตามชื่อ
    - amount = จำนวนอุปกรณ์ที่ status='available'
    - เก็บชื่อ, amount, image_path, category, status_color
    Returns:
        List ของ dict ที่รวมชื่อ, amount, image_path, category, status_color
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
                "category": e["category"],  
                "status_color": ""  # จะกำหนดสีตาม amount
            }
        if e["status"] == "available":
            grouped[name]["amount"] += 1

    # กำหนดสี status_color หลังจากรวมเสร็จ
    for item in grouped.values():
        if item["amount"] == 0:
            item["status_color"] = "yellow"  # ถ้าไม่มีอุปกรณ์ available ให้สีเหลือง

    return list(grouped.values())
