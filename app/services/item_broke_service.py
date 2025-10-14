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
