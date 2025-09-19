from app.crud.base import CRUDBase
from app.schemas.item import Item, ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    pass


crud_item = CRUDItem(Item, "items")