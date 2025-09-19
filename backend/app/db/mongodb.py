from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from app.core.config import settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


db = MongoDB()


async def get_database():
    return db.client[settings.DOCUMENTDB_DATABASE_NAME]


async def connect_to_mongo():
    """Create database connection"""
    if settings.DOCUMENTDB_CONNECTION_STRING:
        db.client = AsyncIOMotorClient(settings.DOCUMENTDB_CONNECTION_STRING)
    else:
        # Default MongoDB connection for development
        db.client = AsyncIOMotorClient("mongodb://localhost:27017")


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()