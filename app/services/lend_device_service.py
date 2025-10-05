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
    - quantity = จำนวนอุปกรณ์ที่ status='available'
    - เก็บชื่อ, quantity, image_path
    Returns:
        List ของ dict ที่รวมชื่อ, quantity, image_path
    """
    equipments = lend_device_repository.get_all_equipments_with_images()

    grouped = {}
    for e in equipments:
        name = e["name"]
        if name not in grouped:
            grouped[name] = {
                "name": name,
                "quantity": 0,
                "image_path": e["image_path"]
            }
        if e["status"] == "available":
            grouped[name]["quantity"] += 1

    return list(grouped.values())
