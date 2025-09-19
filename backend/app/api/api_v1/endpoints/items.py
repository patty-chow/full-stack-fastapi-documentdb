from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.item import Item, ItemCreate
from app.crud import crud_item

router = APIRouter()


@router.get("/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 100):
    """
    Retrieve items.
    """
    items = await crud_item.get_multi(skip=skip, limit=limit)
    return items


@router.post("/", response_model=Item)
async def create_item(item_in: ItemCreate):
    """
    Create new item.
    """
    item = await crud_item.create(obj_in=item_in)
    return item


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: str):
    """
    Get item by ID.
    """
    item = await crud_item.get(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: str, item_in: ItemCreate):
    """
    Update an item.
    """
    item = await crud_item.get(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = await crud_item.update(db_obj=item, obj_in=item_in)
    return item


@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """
    Delete an item.
    """
    item = await crud_item.get(id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await crud_item.remove(id=item_id)
    return {"message": "Item deleted successfully"}