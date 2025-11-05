"""
Pytest configuration and fixtures.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from main import app
from app.config import get_settings
from app.models import User, Message, Conversation, File


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Initialize test database."""
    settings = get_settings()
    # Use test database
    test_mongo_uri = settings.mongo_uri.replace("/librechat", "/librechat_test")

    client = AsyncIOMotorClient(test_mongo_uri)
    database = client.get_default_database()

    # Initialize Beanie with test database
    await init_beanie(
        database=database,
        document_models=[
            User,
            Message,
            Conversation,
            File,
        ],
    )

    yield database

    # Cleanup: drop test database
    await client.drop_database("librechat_test")
    client.close()


@pytest.fixture
async def client(test_db) -> AsyncGenerator:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    from app.utils.auth import hash_password

    user = User(
        username="testuser",
        email="test@example.com",
        name="Test User",
        password=hash_password("password123"),
        emailVerified=True,
    )
    await user.insert()

    yield user

    # Cleanup
    await user.delete()


@pytest.fixture
async def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


@pytest.fixture
async def auth_headers(auth_token):
    """Get authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}
