from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from pydantic.types import ObjectId


# User Models
class UserBase(Document):
    email: Indexed(EmailStr, unique=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(Document):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdate(Document):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserUpdateMe(Document):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(Document):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    hashed_password: str

    class Settings:
        name = "users"


class UserPublic(UserBase):
    id: ObjectId = Field(alias="_id")


class UsersPublic(Document):
    data: list[UserPublic]
    count: int


# Item Models
class ItemBase(Document):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "items"


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class Item(ItemBase):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    owner_id: ObjectId = Field(index=True)

    class Settings:
        name = "items"


class ItemPublic(ItemBase):
    id: ObjectId = Field(alias="_id")
    owner_id: ObjectId


class ItemsPublic(Document):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(Document):
    message: str


# JSON payload containing access token
class Token(Document):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(Document):
    sub: Optional[str] = None


class NewPassword(Document):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
