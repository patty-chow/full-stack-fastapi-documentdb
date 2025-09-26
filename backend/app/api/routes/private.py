from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app import crud
from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
    UserCreate,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
async def create_user(user_in: PrivateUserCreate) -> Any:
    """
    Create a new user.
    """
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    
    user = await crud.create_user(user_create=user_create)
    return user
