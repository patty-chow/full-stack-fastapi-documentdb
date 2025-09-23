from typing import List, Optional
from bson import ObjectId

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item, ItemCreate, ItemUpdate,
    User, UserCreate, UserUpdate, UserUpdateMe
)


# User CRUD operations
async def create_user(user_create: UserCreate) -> User:
    hashed_password = get_password_hash(user_create.password)
    user_data = user_create.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    user = User(**user_data)
    await user.insert()
    return user


async def update_user(user_id: ObjectId, user_in: UserUpdate) -> Optional[User]:
    user = await User.get(user_id)
    if not user:
        return None
    
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
    
    await user.update({"$set": user_data})
    return user


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)


async def get_user_by_id(user_id: ObjectId) -> Optional[User]:
    return await User.get(user_id)


async def authenticate(email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    return await User.find_all().skip(skip).limit(limit).to_list()


def is_active(user: User) -> bool:
    return user.is_active


def is_superuser(user: User) -> bool:
    return user.is_superuser


# Item CRUD operations
async def create_item(item_in: ItemCreate, owner_id: ObjectId) -> Item:
    item_data = item_in.model_dump()
    item_data["owner_id"] = owner_id
    
    item = Item(**item_data)
    await item.insert()
    return item


async def get_item(item_id: ObjectId) -> Optional[Item]:
    return await Item.get(item_id)


async def get_items_by_owner(owner_id: ObjectId, skip: int = 0, limit: int = 100) -> List[Item]:
    return await Item.find(Item.owner_id == owner_id).skip(skip).limit(limit).to_list()


async def get_items(skip: int = 0, limit: int = 100) -> List[Item]:
    return await Item.find_all().skip(skip).limit(limit).to_list()


async def update_item(item_id: ObjectId, item_in: ItemUpdate) -> Optional[Item]:
    item = await Item.get(item_id)
    if not item:
        return None
    
    item_data = item_in.model_dump(exclude_unset=True)
    await item.update({"$set": item_data})
    return item


async def delete_item(item_id: ObjectId) -> bool:
    item = await Item.get(item_id)
    if not item:
        return False
    
    await item.delete()
    return True
