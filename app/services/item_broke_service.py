from app.repositories.item_broke_repository import ItemBrokeRepository


class ItemBrokeService:
    def __init__(self):
        self.repo = ItemBrokeRepository()

    def list_reports(self):
        return self.repo.list_all()

    def get_report(self, item_broke_id: int):
        return self.repo.get(item_broke_id)

    def set_status(self, item_broke_id: int, status: str):
        return self.repo.update_status(item_broke_id, status)

    def create_report(self, rent_id: int | None, type: str, detail: str, images: list = None, equipment_name: str = None, phone: str = None):
        return self.repo.create(rent_id=rent_id, type=type, detail=detail, images=images, equipment_name=equipment_name, phone=phone)
