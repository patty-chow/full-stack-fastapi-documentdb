from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.user import User, UserCreate
from app.crud import crud_user

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve users.
    """
    users = await crud_user.get_multi(skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
async def create_user(user_in: UserCreate):
    """
    Create new user.
    """
    user = await crud_user.create(obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str):
    """
    Get user by ID.
    """
    user = await crud_user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_in: UserCreate):
    """
    Update a user.
    """
    user = await crud_user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await crud_user.update(db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user.
    """
    user = await crud_user.get(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud_user.remove(id=user_id)
    return {"message": "User deleted successfully"}