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
    
    # Initialize Beanie with the Document models
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
