import logging
import asyncio

from app.core.db import connect_to_mongo, init_db, close_mongo_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    await connect_to_mongo()
    await init_db()
    await close_mongo_connection()


def main() -> None:
    logger.info("Creating initial data")
    asyncio.run(init())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
