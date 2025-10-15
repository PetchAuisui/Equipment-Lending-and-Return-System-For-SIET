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

    def update_type(self, item_broke_id: int, new_type: str) -> bool:
        return self.repo.update_type(item_broke_id, new_type)

    def create_report(self, rent_id: int | None, type: str, detail: str, images: list = None, equipment_name: str = None):
        return self.repo.create(rent_id=rent_id, type=type, detail=detail, images=images, equipment_name=equipment_name)

    def delete_report(self, item_broke_id: int) -> bool:
        return self.repo.delete(item_broke_id)
    # (original service API: list_reports/get_report/set_status/create_report/delete_report)
