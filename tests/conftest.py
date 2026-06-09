import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.modules.users.model import User, UserRole

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
async def engine():
    # clean slate each test session
    if os.path.exists("test.db"):
        os.remove("test.db")
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest_asyncio.fixture(scope="session")
async def session_db(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def member_user(session_db: AsyncSession):
    user = User(
        email="member@test.com",
        password_hash=hash_password("password123"),
        display_name="Test Member",
        role=UserRole.member,
    )
    session_db.add(user)
    await session_db.commit()
    await session_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="session")
async def gym_owner_user(session_db: AsyncSession):
    user = User(
        email="owner@test.com",
        password_hash=hash_password("password123"),
        display_name="Gym Owner",
        role=UserRole.gym_owner,
    )
    session_db.add(user)
    await session_db.commit()
    await session_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="session")
async def client(engine, member_user, gym_owner_user):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def member_token(client):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com",
        "password": "password123",
    })
    return resp.json()["data"]["access_token"]


@pytest_asyncio.fixture(scope="session")
async def owner_token(client):
    resp = await client.post("/api/auth/login", json={
        "email": "owner@test.com",
        "password": "password123",
    })
    return resp.json()["data"]["access_token"]
