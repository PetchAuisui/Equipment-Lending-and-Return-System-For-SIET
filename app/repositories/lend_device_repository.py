from app.models.lend_device import device

def get_all_equipment_mock():
    equipments = [
        device("images/hdmi.jpg", "สาย HDMI", 3),
        device("images/hdmi.jpg", "เมาส์", 5),
        device("images/hdmi.jpg", "คีย์บอร์ด", 2),
        device("images/hdmi.jpg", "คีย์บอร์ด", 2)
    ]
    return equipments
