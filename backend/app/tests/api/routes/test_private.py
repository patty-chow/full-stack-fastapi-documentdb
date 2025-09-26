from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import User


async def test_create_user(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "pollo@listo.com",
            "password": "password123",
            "full_name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    data = r.json()

    # Get user from database using Beanie
    from bson import ObjectId
    user = await User.get(ObjectId(data["id"]))

    assert user
    assert user.email == "pollo@listo.com"
    assert user.full_name == "Pollo Listo"
