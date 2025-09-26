from collections.abc import Generator
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection, init_db
from app.main import app
from app.models import Item, User
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
async def db():
    """Initialize MongoDB connection for tests"""
    await connect_to_mongo()
    await init_db()
    yield
    # Clean up test data
    await Item.delete_all()
    await User.delete_all()
    await close_mongo_connection()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
async def normal_user_token_headers(client: TestClient) -> dict[str, str]:
    return await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER
    )
