# Full Stack FastAPI with DocumentDB Migration Walkthrough

This walkthrough demonstrates how to convert the existing PostgreSQL-based FastAPI template to use DocumentDB (MongoDB-compatible database) instead.

## Overview

DocumentDB is a MongoDB-compatible database engine designed for scalability and performance. Since it's MongoDB-compatible, we can use the same drivers and patterns as MongoDB while benefiting from DocumentDB's enhanced features.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- Basic understanding of FastAPI, React, and MongoDB/DocumentDB

## Migration Steps

### Step 1: Update Backend Dependencies

First, we need to replace PostgreSQL-related dependencies with MongoDB/DocumentDB ones.

#### Update `backend/pyproject.toml`:

```toml
[project]
name = "app"
version = "0.1.0"
description = ""
requires-python = ">=3.10,<4.0"
dependencies = [
    "fastapi[standard]<1.0.0,>=0.114.2",
    "python-multipart<1.0.0,>=0.0.7",
    "email-validator<3.0.0.0,>=2.1.0.post1",
    "passlib[bcrypt]<2.0.0,>=1.7.4",
    "tenacity<9.0.0,>=8.2.3",
    "pydantic>2.0",
    "emails<1.0,>=0.6",
    "jinja2<4.0.0,>=3.1.4",
    # Replace PostgreSQL dependencies with MongoDB/DocumentDB
    "motor<4.0.0,>=3.3.2",  # Async MongoDB driver
    "beanie<2.0.0,>=1.23.6",  # ODM for MongoDB
    "pymongo<5.0.0,>=4.6.0",  # MongoDB driver
    "bcrypt==4.3.0",
    "pydantic-settings<3.0.0,>=2.2.1",
    "sentry-sdk[fastapi]<2.0.0,>=1.40.6",
    "pyjwt<3.0.0,>=2.8.0",
]

[tool.uv]
dev-dependencies = [
    "pytest<8.0.0,>=7.4.3",
    "pytest-asyncio<0.24.0,>=0.23.2",  # For async testing
    "mypy<2.0.0,>=1.8.0",
    "ruff<1.0.0,>=0.2.2",
    "pre-commit<4.0.0,>=3.6.2",
    "types-passlib<2.0.0.0,>=1.7.7.20240106",
    "coverage<8.0.0,>=7.4.3",
]
```

### Step 2: Update Configuration

#### Replace `backend/app/core/config.py`:

```python
import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    
    # DocumentDB/MongoDB Configuration
    DOCUMENTDB_HOST: str = "localhost"
    DOCUMENTDB_PORT: int = 27017
    DOCUMENTDB_USER: str = ""
    DOCUMENTDB_PASSWORD: str = ""
    DOCUMENTDB_DB: str = "app"
    DOCUMENTDB_AUTH_SOURCE: str = "admin"

    @computed_field
    @property
    def MONGODB_URL(self) -> str:
        if self.DOCUMENTDB_USER and self.DOCUMENTDB_PASSWORD:
            return f"mongodb://{self.DOCUMENTDB_USER}:{self.DOCUMENTDB_PASSWORD}@{self.DOCUMENTDB_HOST}:{self.DOCUMENTDB_PORT}/{self.DOCUMENTDB_DB}?authSource={self.DOCUMENTDB_AUTH_SOURCE}"
        return f"mongodb://{self.DOCUMENTDB_HOST}:{self.DOCUMENTDB_PORT}/{self.DOCUMENTDB_DB}"

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("DOCUMENTDB_PASSWORD", self.DOCUMENTDB_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        return self


settings = Settings()
```

### Step 3: Update Database Models

#### Replace `backend/app/models.py`:

```python
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
```

### Step 4: Update Database Connection

#### Replace `backend/app/core/db.py`:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models import User, Item


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    return db.client


async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.DOCUMENTDB_DB]
    
    # Initialize Beanie with the Product (Document) class
    await init_beanie(
        database=db.database,
        document_models=[User, Item],
    )


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()


async def init_db() -> None:
    """Initialize database with initial data"""
    # Check if superuser exists
    user = await User.find_one(User.email == settings.FIRST_SUPERUSER)
    if not user:
        from app.crud import create_user
        from app.models import UserCreate
        
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await create_user(user_create=user_in)
```

### Step 5: Update CRUD Operations

#### Replace `backend/app/crud.py`:

```python
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
```

### Step 6: Update Docker Configuration

#### Update `docker-compose.yml`:

```yaml
services:
  documentdb:
    image: mongo:7.0
    restart: always
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
    volumes:
      - app-db-data:/data/db
    env_file:
      - .env
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${DOCUMENTDB_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${DOCUMENTDB_PASSWORD}
      - MONGO_INITDB_DATABASE=${DOCUMENTDB_DB}
    ports:
      - "27017:27017"

  adminer:
    image: adminer
    restart: always
    networks:
      - traefik-public
      - default
    depends_on:
      - documentdb
    environment:
      - ADMINER_DESIGN=pepa-linha-dark
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.constraint-label=traefik-public
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-http.rule=Host(`adminer.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-http.entrypoints=http
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-http.middlewares=https-redirect
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-https.rule=Host(`adminer.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-https.entrypoints=https
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-https.tls=true
      - traefik.http.routers.${STACK_NAME?Variable not set}-adminer-https.tls.certresolver=le
      - traefik.http.services.${STACK_NAME?Variable not set}-adminer.loadbalancer.server.port=8080

  prestart:
    image: '${DOCKER_IMAGE_BACKEND?Variable not set}:${TAG-latest}'
    build:
      context: ./backend
    networks:
      - traefik-public
      - default
    depends_on:
      documentdb:
        condition: service_healthy
        restart: true
    command: bash scripts/prestart.sh
    env_file:
      - .env
    environment:
      - DOMAIN=${DOMAIN}
      - FRONTEND_HOST=${FRONTEND_HOST?Variable not set}
      - ENVIRONMENT=${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY?Variable not set}
      - FIRST_SUPERUSER=${FIRST_SUPERUSER?Variable not set}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
      - DOCUMENTDB_HOST=documentdb
      - DOCUMENTDB_PORT=27017
      - DOCUMENTDB_USER=${DOCUMENTDB_USER?Variable not set}
      - DOCUMENTDB_PASSWORD=${DOCUMENTDB_PASSWORD?Variable not set}
      - DOCUMENTDB_DB=${DOCUMENTDB_DB}
      - SENTRY_DSN=${SENTRY_DSN}

  backend:
    image: '${DOCKER_IMAGE_BACKEND?Variable not set}:${TAG-latest}'
    restart: always
    networks:
      - traefik-public
      - default
    depends_on:
      documentdb:
        condition: service_healthy
        restart: true
      prestart:
        condition: service_completed_successfully
    env_file:
      - .env
    environment:
      - DOMAIN=${DOMAIN}
      - FRONTEND_HOST=${FRONTEND_HOST?Variable not set}
      - ENVIRONMENT=${ENVIRONMENT}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - SECRET_KEY=${SECRET_KEY?Variable not set}
      - FIRST_SUPERUSER=${FIRST_SUPERUSER?Variable not set}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
      - DOCUMENTDB_HOST=documentdb
      - DOCUMENTDB_PORT=27017
      - DOCUMENTDB_USER=${DOCUMENTDB_USER?Variable not set}
      - DOCUMENTDB_PASSWORD=${DOCUMENTDB_PASSWORD?Variable not set}
      - DOCUMENTDB_DB=${DOCUMENTDB_DB}
      - SENTRY_DSN=${SENTRY_DSN}

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]
      interval: 10s
      timeout: 5s
      retries: 5

    build:
      context: ./backend
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.constraint-label=traefik-public
      - traefik.http.services.${STACK_NAME?Variable not set}-backend.loadbalancer.server.port=8000
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-http.rule=Host(`api.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-http.entrypoints=http
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-https.rule=Host(`api.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-https.entrypoints=https
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-https.tls=true
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-https.tls.certresolver=le
      - traefik.http.routers.${STACK_NAME?Variable not set}-backend-http.middlewares=https-redirect

  frontend:
    image: '${DOCKER_IMAGE_FRONTEND?Variable not set}:${TAG-latest}'
    restart: always
    networks:
      - traefik-public
      - default
    build:
      context: ./frontend
      args:
        - VITE_API_URL=https://api.${DOMAIN?Variable not set}
        - NODE_ENV=production
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.constraint-label=traefik-public
      - traefik.http.services.${STACK_NAME?Variable not set}-frontend.loadbalancer.server.port=80
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-http.rule=Host(`dashboard.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-http.entrypoints=http
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.rule=Host(`dashboard.${DOMAIN?Variable not set}`)
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.entrypoints=https
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.tls=true
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-https.tls.certresolver=le
      - traefik.http.routers.${STACK_NAME?Variable not set}-frontend-http.middlewares=https-redirect

volumes:
  app-db-data:

networks:
  traefik-public:
    external: true
```

### Step 7: Update Environment Variables

#### Update `.env` file:

```env
# Project Configuration
PROJECT_NAME="FastAPI DocumentDB Project"
STACK_NAME="fastapi-documentdb-project"
SECRET_KEY="your-secret-key-here"
ENVIRONMENT="local"
DOMAIN="localhost"

# DocumentDB Configuration
DOCUMENTDB_HOST="localhost"
DOCUMENTDB_PORT=27017
DOCUMENTDB_USER="admin"
DOCUMENTDB_PASSWORD="your-documentdb-password"
DOCUMENTDB_DB="app"
DOCUMENTDB_AUTH_SOURCE="admin"

# User Configuration
FIRST_SUPERUSER="admin@example.com"
FIRST_SUPERUSER_PASSWORD="your-admin-password"

# Frontend Configuration
FRONTEND_HOST="http://localhost:5173"
BACKEND_CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

# Email Configuration (optional)
SMTP_HOST=""
SMTP_USER=""
SMTP_PASSWORD=""
EMAILS_FROM_EMAIL="info@example.com"

# Docker Configuration
DOCKER_IMAGE_BACKEND="fastapi-documentdb-backend"
DOCKER_IMAGE_FRONTEND="fastapi-documentdb-frontend"
TAG="latest"

# Sentry (optional)
SENTRY_DSN=""
```

### Step 8: Update API Routes

You'll need to update all API routes to use async/await patterns and the new CRUD functions. Here's an example for the users route:

#### Update `backend/app/api/routes/users.py`:

```python
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app import crud
from app.api.deps import get_current_active_superuser, get_current_active_user
from app.models import User, UserCreate, UserUpdate, UserPublic, UsersPublic

router = APIRouter()


@router.get("/", response_model=UsersPublic)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.get_users(skip=skip, limit=limit)
    return UsersPublic(data=users, count=len(users))


@router.post("/", response_model=UserPublic)
async def create_user(
    *,
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
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
    return user


@router.put("/me", response_model=UserPublic)
async def update_user_me(
    *,
    user_in: UserUpdateMe,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    user = await crud.update_user(user_id=current_user.id, user_in=UserUpdate(**user_data))
    return user


@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_superuser),
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
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    *,
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = await crud.get_user_by_id(user_id=user_object_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = await crud.update_user(user_id=user_object_id, user_in=user_in)
    return user
```

### Step 9: Update Dependencies

#### Update `backend/app/api/deps.py`:

```python
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from bson import ObjectId

from app import crud
from app.core import security
from app.core.config import settings
from app.models import User, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_current_user(
    token: str = Depends(reusable_oauth2),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    try:
        user_id = ObjectId(token_data.sub)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await crud.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not crud.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
```

### Step 10: Update Main Application

#### Update `backend/app/main.py`:

```python
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection, init_db


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await init_db()
    yield
    # Shutdown
    await close_mongo_connection()


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
```

### Step 11: Remove Alembic Migrations

Since DocumentDB doesn't use migrations like SQL databases, you can remove the Alembic-related files:

- Remove `backend/alembic.ini`
- Remove `backend/app/alembic/` directory
- Remove Alembic from dependencies

### Step 12: Update Tests

Update your tests to work with the async DocumentDB setup. You'll need to use `pytest-asyncio` and update the test fixtures.

## Testing the Migration

1. **Start the services:**
   ```bash
   docker compose up -d
   ```

2. **Check the logs:**
   ```bash
   docker compose logs backend
   docker compose logs documentdb
   ```

3. **Test the API:**
   - Visit `http://localhost:8000/docs` for the API documentation
   - Test user registration and login
   - Test item creation and retrieval

## Key Differences from PostgreSQL Version

1. **No Migrations**: DocumentDB doesn't require schema migrations
2. **ObjectId vs UUID**: Using MongoDB's ObjectId instead of UUID
3. **Async Operations**: All database operations are now async
4. **No Foreign Keys**: Using references instead of foreign key constraints
5. **Flexible Schema**: DocumentDB allows for more flexible document structures

## Benefits of DocumentDB

1. **MongoDB Compatibility**: Can use existing MongoDB tools and drivers
2. **Scalability**: Better horizontal scaling capabilities
3. **Performance**: Optimized for document-based workloads
4. **Flexibility**: Schema-less design allows for rapid iteration

## Next Steps

1. **Customize Models**: Add your specific business logic and models
2. **Add Indexes**: Create appropriate indexes for your queries
3. **Implement Caching**: Add Redis or similar for caching
4. **Add Monitoring**: Implement proper logging and monitoring
5. **Security**: Review and enhance security measures

This walkthrough provides a complete migration path from PostgreSQL to DocumentDB while maintaining the same functionality and user experience.
