from app.repositories.item_broke_repository import ItemBrokeRepository
from pprint import pprint

if __name__ == '__main__':
    repo = ItemBrokeRepository()
    try:
        rows = repo.list_all()
        print('rows count:', len(rows))
        for i, r in enumerate(rows[:5]):
            ca = r.get('created_at')
            print(i, 'id=', r.get('item_broke_id'), 'created_at=', ca, 'type=', type(ca))
    except Exception as e:
        print('ERROR during repository check:', e)
    finally:
        try:
            repo.close()
        except Exception:
            pass
