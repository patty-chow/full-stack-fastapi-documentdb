from typing import Any, List
from bson import ObjectId

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import (
    get_current_active_superuser,
    get_current_active_user,
    get_current_user,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    users = await crud.get_users(skip=skip, limit=limit)
    return UsersPublic(data=users, count=len(users))


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(*, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = await crud.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = await crud.create_user(user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, user_in: UserUpdateMe, current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = await crud.get_user_by_email(email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    user = await crud.update_user(user_id=current_user.id, user_in=UserUpdate(**user_data))
    return user


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    *, body: UpdatePassword, current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    await current_user.update({"$set": {"hashed_password": hashed_password}})
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
async def delete_user_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    await current_user.delete()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = await crud.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = await crud.create_user(user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: str, current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific user by id.
    """
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = await crud.get_user_by_id(user_id=user_object_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    user_id: str,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db_user = await crud.get_user_by_id(user_id=user_object_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = await crud.get_user_by_email(email=user_in.email)
        if existing_user and existing_user.id != user_object_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = await crud.update_user(user_id=user_object_id, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    current_user: User = Depends(get_current_user), user_id: str = None
) -> Message:
    """
    Delete a user.
    """
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = await crud.get_user_by_id(user_id=user_object_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    
    # Delete user's items
    items = await crud.get_items_by_owner(owner_id=user_object_id)
    for item in items:
        await crud.delete_item(item_id=item.id)
    
    await user.delete()
    return Message(message="User deleted successfully")
