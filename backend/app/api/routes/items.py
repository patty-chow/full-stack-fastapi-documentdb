from typing import Any
from bson import ObjectId

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
async def read_items(
    current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        items = await crud.get_items(skip=skip, limit=limit)
        count = await Item.count()
    else:
        items = await crud.get_items_by_owner(owner_id=current_user.id, skip=skip, limit=limit)
        count = await Item.find(Item.owner_id == current_user.id).count()

    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
async def read_item(current_user: CurrentUser, id: str) -> Any:
    """
    Get item by ID.
    """
    try:
        item_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    item = await crud.get_item(item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    *, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = await crud.create_item(item_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *,
    current_user: CurrentUser,
    id: str,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    try:
        item_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    item = await crud.get_item(item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    item = await crud.update_item(item_id=item_id, item_in=item_in)
    return item


@router.delete("/{id}")
async def delete_item(
    current_user: CurrentUser, id: str
) -> Message:
    """
    Delete an item.
    """
    try:
        item_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    item = await crud.get_item(item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    await crud.delete_item(item_id=item_id)
    return Message(message="Item deleted successfully")
