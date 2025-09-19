from typing import Optional
from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ItemCreate(ItemBase):
    title: str
    description: str


class ItemUpdate(ItemBase):
    pass


class ItemInDBBase(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    description: str


class Item(ItemInDBBase):
    pass


class ItemInDB(ItemInDBBase):
    pass