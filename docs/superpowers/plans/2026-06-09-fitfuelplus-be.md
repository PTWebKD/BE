# FitFuel+ Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete FastAPI backend for FitFuel+ with 55+ REST endpoints covering auth, users, gym, food, gear, gamification, fitcoin, social, and notifications.

**Architecture:** Feature-based modular — each of 9 modules owns model.py / schema.py / router.py / service.py. Business rules are enforced in the service layer; DB constraints act as a secondary safety net.

**Tech Stack:** Python 3.11, FastAPI 0.111, SQLAlchemy 2.0 async, asyncpg, Alembic, python-jose, passlib[bcrypt], Pydantic v2, Uvicorn, pytest + pytest-asyncio + httpx

---

## File Map

```
database/          ← BE repo root (D:\doanWEDKD\database)
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── dependencies.py
│   └── modules/
│       ├── users/     model.py schema.py router.py service.py
│       ├── auth/      model.py schema.py router.py service.py
│       ├── gym/       model.py schema.py router.py service.py
│       ├── food/      model.py schema.py router.py service.py
│       ├── gear/      model.py schema.py router.py service.py
│       ├── gamification/ model.py schema.py router.py service.py
│       ├── fitcoin/   model.py schema.py router.py service.py
│       ├── social/    model.py schema.py router.py service.py
│       └── notifications/ model.py schema.py router.py service.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_gear.py
│   └── test_food.py
├── alembic/
│   ├── alembic.ini
│   └── env.py
├── .env.example
└── requirements.txt
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/modules/__init__.py` (and each sub-package `__init__.py`)
- Create: `alembic.ini`
- Create: `alembic/env.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy[asyncio]==2.0.29
asyncpg==0.29.0
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic-settings==2.2.1
pydantic[email]==2.7.1
httpx==0.27.0
pytest==8.1.1
pytest-asyncio==0.23.6
aiosqlite==0.20.0
```

- [ ] **Step 2: Write .env.example**

```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/fitfuel
SECRET_KEY=changeme_at_least_32_chars_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173,https://fitfuel.vercel.app
```

- [ ] **Step 3: Create __init__.py files**

Create empty `app/__init__.py`, `app/core/__init__.py`, `app/modules/__init__.py`, and `app/modules/<each_module>/__init__.py`.

- [ ] **Step 4: Create alembic.ini**

Run: `alembic init alembic` inside `database/` directory, then update `alembic.ini`:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://postgres:password@localhost:5432/fitfuel
```

- [ ] **Step 5: Write alembic/env.py**

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.core.config import settings
from app.core.database import Base
# import all models so Base.metadata is populated
from app.modules.users.model import *  # noqa
from app.modules.gym.model import *    # noqa
from app.modules.food.model import *   # noqa
from app.modules.gear.model import *   # noqa
from app.modules.gamification.model import *  # noqa
from app.modules.fitcoin.model import *  # noqa
from app.modules.social.model import *   # noqa
from app.modules.notifications.model import *  # noqa

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 6: Commit**

```
git add requirements.txt .env.example alembic/ app/
git commit -m "chore: scaffold BE project structure"
```

---

### Task 2: Core Layer

**Files:**
- Create: `app/core/config.py`
- Create: `app/core/database.py`
- Create: `app/core/security.py`
- Create: `app/core/dependencies.py`

- [ ] **Step 1: Write app/core/config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/fitfuel"
    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env"}

settings = Settings()
```

- [ ] **Step 2: Write app/core/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 3: Write app/core/security.py**

```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {**data, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return {}
```

- [ ] **Step 4: Write app/core/dependencies.py**

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .security import decode_token

bearer = HTTPBearer(auto_error=False)

def err(code: str, msg: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"success": False, "error": code, "message": msg})

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.users.model import User
    if not credentials:
        err("UNAUTHORIZED", "Token required", 401)
    payload = decode_token(credentials.credentials)
    if not payload:
        err("UNAUTHORIZED", "Invalid or expired token", 401)
    result = await db.execute(select(User).where(User.user_id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        err("UNAUTHORIZED", "User not found", 401)
    return user

def require_role(*roles: str):
    async def _guard(user=Depends(get_current_user)):
        if user.role.value not in roles:
            err("FORBIDDEN", f"Role {list(roles)} required", 403)
        return user
    return _guard

require_member   = require_role("member")
require_vendor   = require_role("vendor")
require_gym_owner = require_role("gym_owner")
require_any      = get_current_user
```

- [ ] **Step 5: Write app/main.py**

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings
from .modules.auth.router import router as auth_router
from .modules.users.router import router as users_router
from .modules.gym.router import router as gym_router
from .modules.food.router import router as food_router
from .modules.gear.router import router as gear_router
from .modules.gamification.router import router as gamification_router
from .modules.fitcoin.router import router as fitcoin_router
from .modules.social.router import router as social_router
from .modules.notifications.router import router as notif_router

app = FastAPI(title="FitFuel+ API", version="1.0.0", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={
        "success": False, "error": "INTERNAL_ERROR", "message": str(exc)
    })

app.include_router(auth_router,         prefix="/api/auth",          tags=["Auth"])
app.include_router(users_router,        prefix="/api/users",         tags=["Users"])
app.include_router(gym_router,          prefix="/api/gym",           tags=["Gym"])
app.include_router(food_router,         prefix="/api/food",          tags=["Food"])
app.include_router(gear_router,         prefix="/api/gear",          tags=["Gear"])
app.include_router(gamification_router, prefix="/api/gamification",  tags=["Gamification"])
app.include_router(fitcoin_router,      prefix="/api/fitcoin",       tags=["FitCoin"])
app.include_router(social_router,       prefix="/api/social",        tags=["Social"])
app.include_router(notif_router,        prefix="/api/notifications",  tags=["Notifications"])

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

- [ ] **Step 6: Write tests/conftest.py**

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.modules.users.model import User, UserRole

TEST_DB = "sqlite+aiosqlite:///./test.db"

@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()

@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

@pytest_asyncio.fixture
async def client(engine):
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

@pytest_asyncio.fixture
async def member_user(db_session):
    user = User(
        email="member@test.com",
        password_hash=hash_password("password123"),
        display_name="Test Member",
        role=UserRole.member,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def member_token(client, member_user):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com", "password": "password123"
    })
    return resp.json()["data"]["access_token"]
```

- [ ] **Step 7: Commit**

```
git add app/core/ app/main.py tests/conftest.py
git commit -m "feat: add core layer (config, db, security, deps) and main app"
```

---

### Task 3: Users Module

**Files:**
- Create: `app/modules/users/model.py`
- Create: `app/modules/users/schema.py`
- Create: `app/modules/users/service.py`
- Create: `app/modules/users/router.py`

- [ ] **Step 1: Write app/modules/users/model.py**

```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class UserRole(str, enum.Enum):
    member    = "member"
    vendor    = "vendor"
    gym_owner = "gym_owner"

class FitnessGoal(str, enum.Enum):
    bulk     = "bulk"
    cut      = "cut"
    maintain = "maintain"

class User(Base):
    __tablename__ = "users"

    user_id         = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    phone           = Column(String(15), unique=True)
    password_hash   = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole), nullable=False, default=UserRole.member)
    display_name    = Column(String(100), nullable=False)
    avatar_url      = Column(String(500))
    fitness_goal    = Column(Enum(FitnessGoal))
    xp_total        = Column(Integer, default=0, nullable=False)
    current_level   = Column(Integer, default=1, nullable=False)
    current_streak  = Column(Integer, default=0, nullable=False)
    fitcoin_balance = Column(Numeric(12, 2), default=0, nullable=False)
    tdee            = Column(Integer)
    referred_by     = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)

    passport   = relationship("FitnessPassport", back_populates="user", uselist=False)
    gear_items = relationship("GearItem", foreign_keys="GearItem.lister_id", back_populates="lister")

class FitnessPassport(Base):
    __tablename__ = "fitness_passport"

    passport_id     = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    total_sessions  = Column(Integer, default=0, nullable=False)
    total_volume    = Column(Numeric(12, 2), default=0, nullable=False)
    longest_streak  = Column(Integer, default=0, nullable=False)
    body_weight_log = Column(JSONB, default=list)
    body_photos     = Column(JSONB, default=list)
    milestone_badges= Column(JSONB, default=list)
    is_public       = Column(Boolean, default=True, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="passport")

class Follow(Base):
    __tablename__ = "follows"

    follower_id  = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    following_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 2: Write app/modules/users/schema.py**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .model import UserRole, FitnessGoal

class UserOut(BaseModel):
    user_id: int
    email: str
    display_name: str
    role: UserRole
    avatar_url: Optional[str]
    fitness_goal: Optional[FitnessGoal]
    xp_total: int
    current_level: int
    current_streak: int
    fitcoin_balance: Decimal
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url:   Optional[str] = None
    fitness_goal: Optional[FitnessGoal] = None
    phone:        Optional[str] = None
    tdee:         Optional[int] = None

class PassportOut(BaseModel):
    passport_id:    int
    total_sessions: int
    total_volume:   Decimal
    longest_streak: int
    is_public:      bool
    body_weight_log: list
    milestone_badges: list
    model_config = {"from_attributes": True}

class FollowOut(BaseModel):
    follower_id:  int
    following_id: int
    created_at:   datetime
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Write app/modules/users/service.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .model import User, FitnessPassport, Follow
from .schema import UserUpdate
from app.core.dependencies import err

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        err("NOT_FOUND", "User not found", 404)
    return user

async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    return user

async def get_or_create_passport(db: AsyncSession, user_id: int) -> FitnessPassport:
    result = await db.execute(select(FitnessPassport).where(FitnessPassport.user_id == user_id))
    passport = result.scalar_one_or_none()
    if not passport:
        passport = FitnessPassport(user_id=user_id)
        db.add(passport)
        await db.flush()
    return passport

async def follow_user(db: AsyncSession, follower_id: int, following_id: int):
    if follower_id == following_id:
        err("VALIDATION_ERROR", "Cannot follow yourself")
    existing = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already following")
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    await db.flush()
    return follow

async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int):
    result = await db.execute(
        select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
    )
    follow = result.scalar_one_or_none()
    if not follow:
        err("NOT_FOUND", "Not following this user", 404)
    await db.delete(follow)
```

- [ ] **Step 4: Write app/modules/users/router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from .schema import UserOut, UserUpdate, PassportOut
from .model import User
from . import service

router = APIRouter()

def ok(data):
    return {"success": True, "data": data}

@router.get("/me", response_model=dict)
async def get_me(user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump())

@router.put("/me", response_model=dict)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_user(db, user, data)
    return ok(UserOut.model_validate(updated).model_dump())

@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await service.get_user_by_id(db, user_id)
    return ok(UserOut.model_validate(user).model_dump())

@router.get("/me/passport", response_model=dict)
async def get_my_passport(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    passport = await service.get_or_create_passport(db, user.user_id)
    return ok(PassportOut.model_validate(passport).model_dump())

@router.post("/{user_id}/follow", response_model=dict)
async def follow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.follow_user(db, current_user.user_id, user_id)
    return ok({"followed": user_id})

@router.delete("/{user_id}/follow", response_model=dict)
async def unfollow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.unfollow_user(db, current_user.user_id, user_id)
    return ok({"unfollowed": user_id})
```

- [ ] **Step 5: Commit**

```
git add app/modules/users/
git commit -m "feat: add users module (profile, passport, follow)"
```

---

### Task 4: Auth Module

**Files:**
- Create: `app/modules/auth/schema.py`
- Create: `app/modules/auth/service.py`
- Create: `app/modules/auth/router.py`
- Create: `app/modules/auth/model.py` (GuestOTP model)

- [ ] **Step 1: Write app/modules/auth/model.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.database import Base

class GuestOTP(Base):
    __tablename__ = "guest_otps"

    id         = Column(Integer, primary_key=True)
    phone      = Column(String(15), nullable=False, index=True)
    otp_code   = Column(String(6), nullable=False)
    attempts   = Column(Integer, default=0, nullable=False)
    used       = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 2: Write app/modules/auth/schema.py**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterIn(BaseModel):
    email:        EmailStr
    password:     str
    display_name: str
    phone:        Optional[str] = None
    referred_by:  Optional[int] = None

class LoginIn(BaseModel):
    email:    EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"

class OTPRequestIn(BaseModel):
    phone: str

class OTPVerifyIn(BaseModel):
    phone:    str
    otp_code: str
```

- [ ] **Step 3: Write app/modules/auth/service.py**

```python
import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import err
from app.modules.users.model import User, UserRole, FitnessPassport
from .model import GuestOTP
from .schema import RegisterIn, LoginIn

OTP_TTL_MINUTES = 5
OTP_MAX_ATTEMPTS = 3

async def register(db: AsyncSession, data: RegisterIn) -> dict:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=UserRole.member,
        phone=data.phone,
        referred_by=data.referred_by,
    )
    db.add(user)
    await db.flush()
    passport = FitnessPassport(user_id=user.user_id)
    db.add(passport)
    await db.flush()
    token = create_access_token({"sub": str(user.user_id), "role": user.role.value, "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user_id": user.user_id}

async def login(db: AsyncSession, data: LoginIn) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        err("UNAUTHORIZED", "Invalid email or password", 401)
    token = create_access_token({"sub": str(user.user_id), "role": user.role.value, "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user_id": user.user_id, "role": user.role.value}

async def request_otp(db: AsyncSession, phone: str) -> dict:
    code = "".join(random.choices(string.digits, k=6))
    expires = datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)
    otp = GuestOTP(phone=phone, otp_code=code, expires_at=expires)
    db.add(otp)
    await db.flush()
    # In production: send SMS. For dev, return the code.
    return {"message": "OTP sent", "dev_otp": code}

async def verify_otp(db: AsyncSession, phone: str, code: str) -> dict:
    result = await db.execute(
        select(GuestOTP)
        .where(GuestOTP.phone == phone, GuestOTP.used == False)
        .order_by(GuestOTP.created_at.desc())
    )
    otp = result.scalar_one_or_none()
    if not otp:
        err("OTP_EXPIRED", "No active OTP for this phone")
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        err("OTP_MAX_ATTEMPTS", "Maximum OTP attempts exceeded")
    if datetime.now(timezone.utc) > otp.expires_at.replace(tzinfo=timezone.utc):
        err("OTP_EXPIRED", "OTP has expired")
    otp.attempts += 1
    if otp.otp_code != code:
        await db.flush()
        err("UNAUTHORIZED", f"Invalid OTP. {OTP_MAX_ATTEMPTS - otp.attempts} attempts remaining", 401)
    otp.used = True
    await db.flush()
    return {"verified": True, "phone": phone}
```

- [ ] **Step 4: Write app/modules/auth/router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schema import RegisterIn, LoginIn, OTPRequestIn, OTPVerifyIn
from . import service

router = APIRouter()

def ok(data):
    return {"success": True, "data": data}

@router.post("/register")
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    result = await service.register(db, data)
    return ok(result)

@router.post("/login")
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await service.login(db, data)
    return ok(result)

@router.post("/guest/otp/request")
async def request_otp(data: OTPRequestIn, db: AsyncSession = Depends(get_db)):
    result = await service.request_otp(db, data.phone)
    return ok(result)

@router.post("/guest/otp/verify")
async def verify_otp(data: OTPVerifyIn, db: AsyncSession = Depends(get_db)):
    result = await service.verify_otp(db, data.phone, data.otp_code)
    return ok(result)
```

- [ ] **Step 5: Write tests/test_auth.py**

```python
import pytest

@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/auth/register", json={
        "email": "new@test.com",
        "password": "secret123",
        "display_name": "New User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    body = {"email": "dup@test.com", "password": "x", "display_name": "D"}
    await client.post("/api/auth/register", json=body)
    resp = await client.post("/api/auth/register", json=body)
    assert resp.status_code == 400
    assert resp.json()["error"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_login_success(client, member_user):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com", "password": "password123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]

@pytest.mark.asyncio
async def test_login_wrong_password(client, member_user):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com", "password": "wrong"
    })
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_otp_flow(client):
    req = await client.post("/api/auth/guest/otp/request", json={"phone": "0901234567"})
    assert req.status_code == 200
    code = req.json()["data"]["dev_otp"]
    verify = await client.post("/api/auth/guest/otp/verify", json={
        "phone": "0901234567", "otp_code": code
    })
    assert verify.json()["data"]["verified"] is True
```

- [ ] **Step 6: Run tests**

```
cd database
pytest tests/test_auth.py -v
```

Expected: 5 tests pass.

- [ ] **Step 7: Commit**

```
git add app/modules/auth/ tests/test_auth.py
git commit -m "feat: add auth module (register, login, guest OTP)"
```

---

### Task 5: Gear Module

**Files:**
- Create: `app/modules/gear/model.py`
- Create: `app/modules/gear/schema.py`
- Create: `app/modules/gear/service.py`
- Create: `app/modules/gear/router.py`
- Create: `tests/test_gear.py`

- [ ] **Step 1: Write app/modules/gear/model.py**

```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class GearCategory(str, enum.Enum):
    Weights     = "Weights"
    Apparel     = "Apparel"
    Supplements = "Supplements"
    Accessories = "Accessories"
    Cardio      = "Cardio"
    Recovery    = "Recovery"

class ListingType(str, enum.Enum):
    sell = "sell"
    rent = "rent"
    both = "both"

class LifecycleAction(str, enum.Enum):
    listed   = "listed"
    sold     = "sold"
    rented   = "rented"
    returned = "returned"
    relisted = "relisted"

class GearTxnType(str, enum.Enum):
    sale   = "sale"
    rental = "rental"

class GearTxnStatus(str, enum.Enum):
    pending   = "pending"
    active    = "active"
    completed = "completed"
    disputed  = "disputed"

class GearItem(Base):
    __tablename__ = "gear_items"

    gear_id          = Column(String(20), primary_key=True)
    current_owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    lister_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    lister_role      = Column(String(20), nullable=False, default="gym_owner")
    category         = Column(Enum(GearCategory), nullable=False)
    name             = Column(String(200), nullable=False)
    description      = Column(Text)
    condition_rating = Column(Integer, nullable=False)
    condition_notes  = Column(Text)
    images           = Column(JSONB, default=list)
    listing_type     = Column(Enum(ListingType), nullable=False, default=ListingType.rent)
    sell_price       = Column(Numeric(12, 2))
    rent_price_day   = Column(Numeric(10, 2))
    rent_price_week  = Column(Numeric(10, 2))
    deposit_amount   = Column(Numeric(12, 2))
    qr_code_url      = Column(String(500))
    verified         = Column(Boolean, default=False, nullable=False)
    is_available     = Column(Boolean, default=True, nullable=False)
    avg_rating       = Column(Numeric(2, 1), default=0, nullable=False)
    total_reviews    = Column(Integer, default=0, nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    lister       = relationship("User", foreign_keys=[lister_id], back_populates="gear_items")
    lifecycle    = relationship("GearLifecycle", back_populates="gear_item", order_by="GearLifecycle.timestamp")
    transactions = relationship("GearTransaction", back_populates="gear_item")

class GearLifecycle(Base):
    __tablename__ = "gear_lifecycle"

    lifecycle_id     = Column(Integer, primary_key=True)
    gear_id          = Column(String(20), ForeignKey("gear_items.gear_id"), nullable=False, index=True)
    owner_id         = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action           = Column(Enum(LifecycleAction), nullable=False)
    condition_at_time= Column(Integer)
    notes            = Column(Text)
    photos           = Column(JSONB, default=list)
    price_snapshot   = Column(Numeric(12, 2))
    timestamp        = Column(DateTime, default=datetime.utcnow, nullable=False)

    gear_item = relationship("GearItem", back_populates="lifecycle")

class GearTransaction(Base):
    __tablename__ = "gear_transactions"

    transaction_id = Column(Integer, primary_key=True)
    gear_id        = Column(String(20), ForeignKey("gear_items.gear_id"), nullable=False)
    seller_id      = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    buyer_id       = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    type           = Column(Enum(GearTxnType), nullable=False)
    amount         = Column(Numeric(12, 2), nullable=False)
    deposit        = Column(Numeric(12, 2), default=0, nullable=False)
    fitcoin_used   = Column(Numeric(12, 2), default=0, nullable=False)
    rental_start   = Column(Date)
    rental_end     = Column(Date)
    status         = Column(Enum(GearTxnStatus), nullable=False, default=GearTxnStatus.pending)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    gear_item = relationship("GearItem", back_populates="transactions")
```

- [ ] **Step 2: Write app/modules/gear/schema.py**

```python
from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .model import GearCategory, ListingType, GearTxnStatus

class GearItemCreate(BaseModel):
    name:             str
    category:         GearCategory
    description:      Optional[str] = None
    condition_rating: int
    listing_type:     ListingType = ListingType.rent
    sell_price:       Optional[Decimal] = None
    rent_price_day:   Optional[Decimal] = None
    rent_price_week:  Optional[Decimal] = None
    deposit_amount:   Optional[Decimal] = None
    images:           List[str] = []

class GearItemOut(BaseModel):
    gear_id:          str
    lister_id:        int
    lister_role:      str
    name:             str
    category:         GearCategory
    description:      Optional[str]
    condition_rating: int
    listing_type:     ListingType
    sell_price:       Optional[Decimal]
    rent_price_day:   Optional[Decimal]
    deposit_amount:   Optional[Decimal]
    verified:         bool
    is_available:     bool
    avg_rating:       Decimal
    created_at:       datetime
    model_config = {"from_attributes": True}

class RentIn(BaseModel):
    rental_start: date
    rental_end:   date

class LifecycleOut(BaseModel):
    lifecycle_id:     int
    action:           str
    condition_at_time: Optional[int]
    notes:            Optional[str]
    price_snapshot:   Optional[Decimal]
    timestamp:        datetime
    model_config = {"from_attributes": True}

class TransactionOut(BaseModel):
    transaction_id: int
    gear_id:        str
    type:           str
    amount:         Decimal
    deposit:        Decimal
    rental_start:   Optional[date]
    rental_end:     Optional[date]
    status:         GearTxnStatus
    created_at:     datetime
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Write app/modules/gear/service.py**

```python
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import GearItem, GearLifecycle, GearTransaction, ListingType, LifecycleAction, GearTxnType, GearTxnStatus
from .schema import GearItemCreate, RentIn

DEPOSIT_RATE = Decimal("0.5")  # BR-13: 50% deposit

def _gen_gear_id() -> str:
    uid = uuid.uuid4().hex[:8].upper()
    return f"GEAR-{uid[:4]}-{uid[4:]}"

async def list_gear(db: AsyncSession, category: str = None, search: str = None) -> list:
    q = select(GearItem).where(GearItem.is_available == True)
    if category:
        q = q.where(GearItem.category == category)
    if search:
        q = q.where(GearItem.name.ilike(f"%{search}%"))
    result = await db.execute(q.order_by(GearItem.created_at.desc()))
    return result.scalars().all()

async def get_gear(db: AsyncSession, gear_id: str) -> GearItem:
    result = await db.execute(select(GearItem).where(GearItem.gear_id == gear_id))
    item = result.scalar_one_or_none()
    if not item:
        err("NOT_FOUND", "Gear item not found", 404)
    return item

async def create_gear(db: AsyncSession, user: User, data: GearItemCreate) -> GearItem:
    # BR-11B: member can only list for rent
    if user.role.value == "member" and data.listing_type != ListingType.rent:
        err("MEMBER_CANNOT_SELL", "Members can only list gear for rent (BR-11B)")
    # BR-13: deposit must be >= 50% of sell_price or computed from rent
    if data.deposit_amount is not None:
        reference = data.sell_price or (data.rent_price_day * 30 if data.rent_price_day else None)
        if reference and data.deposit_amount < reference * DEPOSIT_RATE:
            err("DEPOSIT_REQUIRED", f"Deposit must be >= 50% of item value (BR-13)")
    gear_id = _gen_gear_id()
    item = GearItem(
        gear_id=gear_id,
        current_owner_id=user.user_id,
        lister_id=user.user_id,
        lister_role=user.role.value,
        **data.model_dump(exclude={"images"}),
        images=data.images,
    )
    db.add(item)
    await db.flush()
    # append lifecycle entry (BR-37: only INSERT)
    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.listed,
        condition_at_time=data.condition_rating,
        price_snapshot=data.sell_price or data.rent_price_day,
    )
    db.add(lc)
    await db.flush()
    return item

async def rent_gear(db: AsyncSession, user: User, gear_id: str, data: RentIn) -> GearTransaction:
    item = await get_gear(db, gear_id)
    if not item.is_available:
        err("VALIDATION_ERROR", "Gear is not available for rent")
    if item.listing_type not in (ListingType.rent, ListingType.both):
        err("VALIDATION_ERROR", "This gear is not listed for rent")
    if item.current_owner_id == user.user_id:
        err("VALIDATION_ERROR", "Cannot rent your own gear")
    days = (data.rental_end - data.rental_start).days
    if days <= 0:
        err("VALIDATION_ERROR", "rental_end must be after rental_start")
    daily = item.rent_price_day or Decimal("0")
    total = daily * days
    deposit = item.deposit_amount or (total * DEPOSIT_RATE)
    txn = GearTransaction(
        gear_id=gear_id,
        seller_id=item.current_owner_id,
        buyer_id=user.user_id,
        type=GearTxnType.rental,
        amount=total,
        deposit=deposit,
        rental_start=data.rental_start,
        rental_end=data.rental_end,
        status=GearTxnStatus.active,
    )
    db.add(txn)
    item.is_available = False
    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.rented,
        price_snapshot=total,
    )
    db.add(lc)
    await db.flush()
    return txn

async def return_gear(db: AsyncSession, user: User, gear_id: str) -> GearItem:
    item = await get_gear(db, gear_id)
    result = await db.execute(
        select(GearTransaction)
        .where(GearTransaction.gear_id == gear_id,
               GearTransaction.buyer_id == user.user_id,
               GearTransaction.status == GearTxnStatus.active)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        err("NOT_FOUND", "No active rental found for this gear", 404)
    txn.status = GearTxnStatus.completed
    item.is_available = True
    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.returned,
    )
    db.add(lc)
    await db.flush()
    return item

async def get_my_listings(db: AsyncSession, user_id: int) -> list:
    result = await db.execute(
        select(GearItem).where(GearItem.lister_id == user_id).order_by(GearItem.created_at.desc())
    )
    return result.scalars().all()

async def get_my_rentals(db: AsyncSession, user_id: int) -> list:
    result = await db.execute(
        select(GearTransaction).where(
            GearTransaction.buyer_id == user_id,
            GearTransaction.status == GearTxnStatus.active,
        )
    )
    return result.scalars().all()

async def get_lifecycle(db: AsyncSession, gear_id: str) -> list:
    await get_gear(db, gear_id)
    result = await db.execute(
        select(GearLifecycle).where(GearLifecycle.gear_id == gear_id).order_by(GearLifecycle.timestamp)
    )
    return result.scalars().all()
```

- [ ] **Step 4: Write app/modules/gear/router.py**

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_any
from app.modules.users.model import User
from .schema import GearItemCreate, GearItemOut, RentIn, LifecycleOut, TransactionOut
from . import service

router = APIRouter()

def ok(data):
    return {"success": True, "data": data}

@router.get("/")
async def list_gear(
    category: Optional[str] = Query(None),
    search:   Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_gear(db, category, search)
    return ok([GearItemOut.model_validate(i).model_dump() for i in items])

@router.get("/my/listings")
async def my_listings(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = await service.get_my_listings(db, user.user_id)
    return ok([GearItemOut.model_validate(i).model_dump() for i in items])

@router.get("/my/rentals")
async def my_rentals(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    txns = await service.get_my_rentals(db, user.user_id)
    return ok([TransactionOut.model_validate(t).model_dump() for t in txns])

@router.get("/{gear_id}")
async def get_gear(gear_id: str, db: AsyncSession = Depends(get_db)):
    item = await service.get_gear(db, gear_id)
    return ok(GearItemOut.model_validate(item).model_dump())

@router.post("/")
async def create_gear(
    data: GearItemCreate,
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    item = await service.create_gear(db, user, data)
    return ok(GearItemOut.model_validate(item).model_dump())

@router.post("/{gear_id}/rent")
async def rent_gear(
    gear_id: str,
    data: RentIn,
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    txn = await service.rent_gear(db, user, gear_id, data)
    return ok(TransactionOut.model_validate(txn).model_dump())

@router.post("/{gear_id}/return")
async def return_gear(
    gear_id: str,
    user: User = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    item = await service.return_gear(db, user, gear_id)
    return ok(GearItemOut.model_validate(item).model_dump())

@router.get("/{gear_id}/lifecycle")
async def get_lifecycle(gear_id: str, db: AsyncSession = Depends(get_db)):
    events = await service.get_lifecycle(db, gear_id)
    return ok([LifecycleOut.model_validate(e).model_dump() for e in events])
```

- [ ] **Step 5: Write tests/test_gear.py**

```python
import pytest

@pytest.mark.asyncio
async def test_member_cannot_sell(client, member_token):
    resp = await client.post("/api/gear/", json={
        "name": "Test Barbell",
        "category": "Weights",
        "condition_rating": 4,
        "listing_type": "sell",
        "sell_price": 500000,
    }, headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "MEMBER_CANNOT_SELL"

@pytest.mark.asyncio
async def test_member_can_list_for_rent(client, member_token):
    resp = await client.post("/api/gear/", json={
        "name": "Test Dumbbell",
        "category": "Weights",
        "condition_rating": 3,
        "listing_type": "rent",
        "rent_price_day": 50000,
    }, headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["listing_type"] == "rent"
    assert data["lister_role"] == "member"

@pytest.mark.asyncio
async def test_list_gear_public(client):
    resp = await client.get("/api/gear/")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)

@pytest.mark.asyncio
async def test_gear_not_found(client):
    resp = await client.get("/api/gear/GEAR-XXXX-XXXX")
    assert resp.status_code == 404
```

- [ ] **Step 6: Run tests**

```
pytest tests/test_gear.py -v
```

Expected: 4 tests pass.

- [ ] **Step 7: Commit**

```
git add app/modules/gear/ tests/test_gear.py
git commit -m "feat: add gear module with BR-11B and BR-13 enforcement"
```

---

### Task 6: Food Module

**Files:**
- Create: `app/modules/food/model.py`
- Create: `app/modules/food/schema.py`
- Create: `app/modules/food/service.py`
- Create: `app/modules/food/router.py`

- [ ] **Step 1: Write app/modules/food/model.py**

```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class OrderStatus(str, enum.Enum):
    pending    = "pending"
    confirmed  = "confirmed"
    preparing  = "preparing"
    delivering = "delivering"
    delivered  = "delivered"
    cancelled  = "cancelled"

class FoodProduct(Base):
    __tablename__ = "food_products"

    product_id    = Column(Integer, primary_key=True)
    vendor_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name          = Column(String(200), nullable=False)
    description   = Column(Text)
    price         = Column(Numeric(10, 2), nullable=False)
    calories      = Column(Integer, nullable=False, default=0)
    protein_g     = Column(Numeric(5, 1), default=0, nullable=False)
    carb_g        = Column(Numeric(5, 1), default=0, nullable=False)
    fat_g         = Column(Numeric(5, 1), default=0, nullable=False)
    ingredients   = Column(JSONB, default=list)
    allergens     = Column(JSONB, default=list)
    images        = Column(JSONB, default=list)
    category      = Column(String(50))
    badge         = Column(String(50))
    is_available  = Column(Boolean, default=True, nullable=False)
    avg_rating    = Column(Numeric(2, 1), default=0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    orders  = relationship("FoodOrder", back_populates="product")
    reviews = relationship("FoodReview", back_populates="product")

class FoodOrder(Base):
    __tablename__ = "food_orders"

    order_id         = Column(Integer, primary_key=True)
    user_id          = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    guest_phone      = Column(String(15))
    vendor_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    items            = Column(JSONB, nullable=False)
    subtotal         = Column(Numeric(12, 2), nullable=False)
    delivery_fee     = Column(Numeric(10, 2), nullable=False, default=15000)
    total_amount     = Column(Numeric(12, 2), nullable=False)
    fitcoin_used     = Column(Numeric(12, 2), nullable=False, default=0)
    delivery_address = Column(String(500), nullable=False)
    delivery_time    = Column(String(50))
    status           = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    payment_method   = Column(String(50))
    is_meal_prep     = Column(Boolean, default=False, nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("FoodProduct", back_populates="orders", foreign_keys=[vendor_id], viewonly=True)

class FoodReview(Base):
    __tablename__ = "food_reviews"

    review_id    = Column(Integer, primary_key=True)
    product_id   = Column(Integer, ForeignKey("food_products.product_id", ondelete="CASCADE"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating       = Column(Integer, nullable=False)
    comment      = Column(Text)
    photos       = Column(JSONB, default=list)
    helpful_votes= Column(Integer, default=0, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("FoodProduct", back_populates="reviews")
```

- [ ] **Step 2: Write app/modules/food/schema.py**

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .model import OrderStatus

class ProductCreate(BaseModel):
    name:         str
    description:  Optional[str] = None
    price:        Decimal
    calories:     int = 0
    protein_g:    Decimal = Decimal("0")
    carb_g:       Decimal = Decimal("0")
    fat_g:        Decimal = Decimal("0")
    category:     Optional[str] = None
    badge:        Optional[str] = None
    images:       List[str] = []

class ProductOut(BaseModel):
    product_id:   int
    vendor_id:    int
    name:         str
    description:  Optional[str]
    price:        Decimal
    calories:     int
    protein_g:    Decimal
    carb_g:       Decimal
    fat_g:        Decimal
    category:     Optional[str]
    badge:        Optional[str]
    is_available: bool
    avg_rating:   Decimal
    total_reviews:int
    created_at:   datetime
    model_config = {"from_attributes": True}

class OrderItem(BaseModel):
    product_id: int
    qty:        int
    price:      Decimal
    name:       str

class OrderCreate(BaseModel):
    items:            List[OrderItem]
    delivery_address: str
    vendor_id:        int
    guest_phone:      Optional[str] = None
    fitcoin_used:     Decimal = Decimal("0")
    payment_method:   Optional[str] = None
    is_meal_prep:     bool = False

class OrderOut(BaseModel):
    order_id:         int
    user_id:          Optional[int]
    guest_phone:      Optional[str]
    vendor_id:        int
    items:            list
    subtotal:         Decimal
    total_amount:     Decimal
    delivery_address: str
    status:           OrderStatus
    created_at:       datetime
    model_config = {"from_attributes": True}

class ReviewCreate(BaseModel):
    rating:  int
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    review_id:  int
    product_id: int
    user_id:    int
    rating:     int
    comment:    Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Write app/modules/food/service.py**

```python
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.dependencies import err
from app.modules.users.model import User
from .model import FoodProduct, FoodOrder, FoodReview, OrderStatus
from .schema import ProductCreate, OrderCreate, ReviewCreate

DELIVERY_FEE = Decimal("15000")
MIN_ORDER    = Decimal("30000")

async def list_products(db: AsyncSession, search: str = None) -> list:
    q = select(FoodProduct).where(FoodProduct.is_available == True)
    if search:
        q = q.where(FoodProduct.name.ilike(f"%{search}%"))
    r = await db.execute(q.order_by(FoodProduct.created_at.desc()))
    return r.scalars().all()

async def get_product(db: AsyncSession, product_id: int) -> FoodProduct:
    r = await db.execute(select(FoodProduct).where(FoodProduct.product_id == product_id))
    p = r.scalar_one_or_none()
    if not p:
        err("NOT_FOUND", "Product not found", 404)
    return p

async def create_product(db: AsyncSession, vendor: User, data: ProductCreate) -> FoodProduct:
    if vendor.role.value != "vendor":
        err("FORBIDDEN", "Only vendors can create products (BR-15)", 403)
    p = FoodProduct(vendor_id=vendor.user_id, **data.model_dump())
    db.add(p)
    await db.flush()
    return p

async def update_product(db: AsyncSession, vendor: User, product_id: int, data: ProductCreate) -> FoodProduct:
    p = await get_product(db, product_id)
    if p.vendor_id != vendor.user_id:
        err("FORBIDDEN", "Not your product", 403)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    await db.flush()
    return p

async def place_order(db: AsyncSession, user: User | None, data: OrderCreate) -> FoodOrder:
    if user is None and not data.guest_phone:
        err("VALIDATION_ERROR", "guest_phone required for guest orders (BR-18)")
    subtotal = sum(item.price * item.qty for item in data.items)
    if subtotal < MIN_ORDER:
        err("VALIDATION_ERROR", f"Minimum order is {MIN_ORDER}đ")
    total = subtotal + DELIVERY_FEE - data.fitcoin_used
    order = FoodOrder(
        user_id=user.user_id if user else None,
        guest_phone=data.guest_phone,
        vendor_id=data.vendor_id,
        items=[i.model_dump() for i in data.items],
        subtotal=subtotal,
        delivery_fee=DELIVERY_FEE,
        total_amount=max(total, Decimal("0")),
        fitcoin_used=data.fitcoin_used,
        delivery_address=data.delivery_address,
        payment_method=data.payment_method,
        is_meal_prep=data.is_meal_prep,
    )
    db.add(order)
    await db.flush()
    return order

async def get_my_orders(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(FoodOrder).where(FoodOrder.user_id == user_id).order_by(FoodOrder.created_at.desc())
    )
    return r.scalars().all()

async def update_order_status(db: AsyncSession, vendor: User, order_id: int, status: OrderStatus) -> FoodOrder:
    r = await db.execute(select(FoodOrder).where(FoodOrder.order_id == order_id))
    order = r.scalar_one_or_none()
    if not order:
        err("NOT_FOUND", "Order not found", 404)
    if order.vendor_id != vendor.user_id:
        err("FORBIDDEN", "Not your order", 403)
    order.status = status
    await db.flush()
    return order

async def create_review(db: AsyncSession, user: User, product_id: int, data: ReviewCreate) -> FoodReview:
    if not 1 <= data.rating <= 5:
        err("VALIDATION_ERROR", "Rating must be 1-5")
    existing = await db.execute(
        select(FoodReview).where(FoodReview.product_id == product_id, FoodReview.user_id == user.user_id)
    )
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already reviewed this product")
    review = FoodReview(product_id=product_id, user_id=user.user_id, **data.model_dump())
    db.add(review)
    await db.flush()
    # update avg_rating
    r = await db.execute(select(FoodReview).where(FoodReview.product_id == product_id))
    reviews = r.scalars().all()
    product = await get_product(db, product_id)
    product.total_reviews = len(reviews)
    product.avg_rating = Decimal(str(sum(rv.rating for rv in reviews) / len(reviews))).quantize(Decimal("0.1"))
    await db.flush()
    return review

async def get_product_reviews(db: AsyncSession, product_id: int) -> list:
    r = await db.execute(select(FoodReview).where(FoodReview.product_id == product_id))
    return r.scalars().all()
```

- [ ] **Step 4: Write app/modules/food/router.py**

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_vendor
from app.modules.users.model import User
from .schema import ProductCreate, ProductOut, OrderCreate, OrderOut, ReviewCreate, ReviewOut
from .model import OrderStatus
from . import service

router = APIRouter()

def ok(data): return {"success": True, "data": data}

@router.get("/products")
async def list_products(search: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    items = await service.list_products(db, search)
    return ok([ProductOut.model_validate(p).model_dump() for p in items])

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await service.get_product(db, product_id)
    return ok(ProductOut.model_validate(p).model_dump())

@router.post("/products")
async def create_product(
    data: ProductCreate,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    p = await service.create_product(db, vendor, data)
    return ok(ProductOut.model_validate(p).model_dump())

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    data: ProductCreate,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    p = await service.update_product(db, vendor, product_id, data)
    return ok(ProductOut.model_validate(p).model_dump())

@router.post("/orders")
async def place_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    credentials=Depends(__import__("fastapi.security", fromlist=["HTTPBearer"]).HTTPBearer(auto_error=False)),
):
    from app.core.security import decode_token
    from sqlalchemy import select
    from app.modules.users.model import User as UserModel
    user = None
    if credentials:
        payload = decode_token(credentials.credentials)
        if payload:
            r = await db.execute(select(UserModel).where(UserModel.user_id == int(payload["sub"])))
            user = r.scalar_one_or_none()
    order = await service.place_order(db, user, data)
    return ok(OrderOut.model_validate(order).model_dump())

@router.get("/orders")
async def my_orders(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    orders = await service.get_my_orders(db, user.user_id)
    return ok([OrderOut.model_validate(o).model_dump() for o in orders])

@router.put("/orders/{order_id}/status")
async def update_status(
    order_id: int,
    status: OrderStatus,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    order = await service.update_order_status(db, vendor, order_id, status)
    return ok(OrderOut.model_validate(order).model_dump())

@router.post("/products/{product_id}/reviews")
async def create_review(
    product_id: int,
    data: ReviewCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    review = await service.create_review(db, user, product_id, data)
    return ok(ReviewOut.model_validate(review).model_dump())

@router.get("/products/{product_id}/reviews")
async def get_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    reviews = await service.get_product_reviews(db, product_id)
    return ok([ReviewOut.model_validate(r).model_dump() for r in reviews])
```

- [ ] **Step 5: Commit**

```
git add app/modules/food/
git commit -m "feat: add food module (products, orders, reviews)"
```

---

### Task 7: Gym Module

**Files:**
- Create: `app/modules/gym/model.py`
- Create: `app/modules/gym/schema.py`
- Create: `app/modules/gym/service.py`
- Create: `app/modules/gym/router.py`

- [ ] **Step 1: Write app/modules/gym/model.py**

```python
import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class SessionStatus(str, enum.Enum):
    active    = "active"
    done      = "done"
    cancelled = "cancelled"

class MuscleGroup(str, enum.Enum):
    chest     = "chest"
    back      = "back"
    legs      = "legs"
    shoulders = "shoulders"
    arms      = "arms"
    core      = "core"

class MembershipStatus(str, enum.Enum):
    active    = "active"
    expired   = "expired"
    cancelled = "cancelled"

class Gym(Base):
    __tablename__ = "gyms"

    gym_id        = Column(Integer, primary_key=True)
    owner_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name          = Column(String(200), nullable=False)
    address       = Column(String(500), nullable=False)
    phone         = Column(String(15))
    opening_hours = Column(JSONB, default=dict)
    services      = Column(JSONB, default=list)
    membership_plans = Column(JSONB, default=list)
    logo_url      = Column(String(500))
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

class GymMembership(Base):
    __tablename__ = "gym_memberships"

    membership_id  = Column(Integer, primary_key=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    gym_id         = Column(Integer, ForeignKey("gyms.gym_id", ondelete="CASCADE"), nullable=False)
    plan_name      = Column(String(100), nullable=False)
    start_date     = Column(Date, nullable=False)
    end_date       = Column(Date, nullable=False)
    status         = Column(Enum(MembershipStatus), nullable=False, default=MembershipStatus.active)
    auto_renew     = Column(Boolean, default=False, nullable=False)
    payment_method = Column(String(50))
    amount_paid    = Column(Numeric(12, 2), nullable=False, default=0)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    session_id   = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    gym_id       = Column(Integer, ForeignKey("gyms.gym_id", ondelete="SET NULL"))
    date         = Column(Date, nullable=False)
    duration_min = Column(Integer)
    status       = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.active)
    notes        = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    exercises = relationship("ExerciseLog", back_populates="session", cascade="all, delete-orphan")

class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    log_id        = Column(Integer, primary_key=True)
    session_id    = Column(Integer, ForeignKey("workout_sessions.session_id", ondelete="CASCADE"), nullable=False)
    exercise_name = Column(String(200), nullable=False)
    muscle_group  = Column(Enum(MuscleGroup), nullable=False)
    sets          = Column(JSONB, nullable=False, default=list)
    is_pr         = Column(Boolean, default=False, nullable=False)
    notes         = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("WorkoutSession", back_populates="exercises")
```

- [ ] **Step 2: Write app/modules/gym/schema.py**

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .model import SessionStatus, MuscleGroup, MembershipStatus

class GymOut(BaseModel):
    gym_id:    int
    owner_id:  int
    name:      str
    address:   str
    phone:     Optional[str]
    logo_url:  Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class MembershipCreate(BaseModel):
    gym_id:         int
    plan_name:      str
    start_date:     date
    end_date:       date
    amount_paid:    Decimal
    payment_method: Optional[str] = None
    auto_renew:     bool = False

class MembershipOut(BaseModel):
    membership_id: int
    user_id:       int
    gym_id:        int
    plan_name:     str
    start_date:    date
    end_date:      date
    status:        MembershipStatus
    amount_paid:   Decimal
    created_at:    datetime
    model_config = {"from_attributes": True}

class SetData(BaseModel):
    reps:   int
    weight: float

class ExerciseCreate(BaseModel):
    exercise_name: str
    muscle_group:  MuscleGroup
    sets:          List[SetData]
    notes:         Optional[str] = None

class ExerciseOut(BaseModel):
    log_id:        int
    exercise_name: str
    muscle_group:  MuscleGroup
    sets:          list
    is_pr:         bool
    created_at:    datetime
    model_config = {"from_attributes": True}

class SessionCreate(BaseModel):
    date:         date
    gym_id:       Optional[int] = None
    duration_min: Optional[int] = None
    notes:        Optional[str] = None

class SessionOut(BaseModel):
    session_id:   int
    user_id:      int
    gym_id:       Optional[int]
    date:         date
    duration_min: Optional[int]
    status:       SessionStatus
    exercises:    List[ExerciseOut] = []
    created_at:   datetime
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Write app/modules/gym/service.py**

```python
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.core.dependencies import err
from app.modules.users.model import User
from .model import Gym, GymMembership, WorkoutSession, ExerciseLog, MembershipStatus
from .schema import MembershipCreate, SessionCreate, ExerciseCreate

async def list_gyms(db: AsyncSession) -> list:
    r = await db.execute(select(Gym).order_by(Gym.gym_id))
    return r.scalars().all()

async def get_gym(db: AsyncSession, gym_id: int) -> Gym:
    r = await db.execute(select(Gym).where(Gym.gym_id == gym_id))
    g = r.scalar_one_or_none()
    if not g:
        err("NOT_FOUND", "Gym not found", 404)
    return g

async def get_my_memberships(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(GymMembership).where(GymMembership.user_id == user_id).order_by(GymMembership.created_at.desc())
    )
    return r.scalars().all()

async def buy_membership(db: AsyncSession, user: User, data: MembershipCreate) -> GymMembership:
    if data.end_date <= data.start_date:
        err("VALIDATION_ERROR", "end_date must be after start_date")
    # BR-06: no overlapping active membership at same gym
    r = await db.execute(
        select(GymMembership).where(
            GymMembership.user_id == user.user_id,
            GymMembership.gym_id == data.gym_id,
            GymMembership.status == MembershipStatus.active,
        )
    )
    if r.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already have an active membership at this gym (BR-06)")
    m = GymMembership(user_id=user.user_id, **data.model_dump())
    db.add(m)
    await db.flush()
    return m

async def log_session(db: AsyncSession, user: User, data: SessionCreate) -> WorkoutSession:
    session = WorkoutSession(user_id=user.user_id, **data.model_dump())
    db.add(session)
    await db.flush()
    return session

async def get_my_sessions(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .options(selectinload(WorkoutSession.exercises))
        .order_by(WorkoutSession.date.desc())
    )
    return r.scalars().all()

async def log_exercise(db: AsyncSession, user: User, session_id: int, data: ExerciseCreate) -> ExerciseLog:
    r = await db.execute(
        select(WorkoutSession).where(
            WorkoutSession.session_id == session_id,
            WorkoutSession.user_id == user.user_id,
        )
    )
    session = r.scalar_one_or_none()
    if not session:
        err("NOT_FOUND", "Session not found", 404)
    # check PR: is this weight higher than any previous log for this exercise?
    prev = await db.execute(
        select(ExerciseLog).join(WorkoutSession).where(
            WorkoutSession.user_id == user.user_id,
            ExerciseLog.exercise_name == data.exercise_name,
        )
    )
    all_prev = prev.scalars().all()
    max_prev_weight = max(
        (max((s.get("weight", 0) for s in log.sets), default=0) for log in all_prev),
        default=0
    )
    new_max = max((s.weight for s in data.sets), default=0)
    is_pr = new_max > max_prev_weight

    log = ExerciseLog(
        session_id=session_id,
        exercise_name=data.exercise_name,
        muscle_group=data.muscle_group,
        sets=[s.model_dump() for s in data.sets],
        is_pr=is_pr,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()
    return log

async def get_my_records(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(ExerciseLog)
        .join(WorkoutSession)
        .where(WorkoutSession.user_id == user_id, ExerciseLog.is_pr == True)
        .order_by(ExerciseLog.created_at.desc())
    )
    return r.scalars().all()
```

- [ ] **Step 4: Write app/modules/gym/router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import MembershipCreate, MembershipOut, SessionCreate, SessionOut, ExerciseCreate, ExerciseOut, GymOut
from . import service

router = APIRouter()
def ok(data): return {"success": True, "data": data}

@router.get("/")
async def list_gyms(db: AsyncSession = Depends(get_db)):
    gyms = await service.list_gyms(db)
    return ok([GymOut.model_validate(g).model_dump() for g in gyms])

@router.get("/{gym_id}")
async def get_gym(gym_id: int, db: AsyncSession = Depends(get_db)):
    g = await service.get_gym(db, gym_id)
    return ok(GymOut.model_validate(g).model_dump())

@router.get("/memberships/my")
async def my_memberships(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ms = await service.get_my_memberships(db, user.user_id)
    return ok([MembershipOut.model_validate(m).model_dump() for m in ms])

@router.post("/memberships")
async def buy_membership(
    data: MembershipCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    m = await service.buy_membership(db, user, data)
    return ok(MembershipOut.model_validate(m).model_dump())

@router.post("/sessions")
async def log_session(
    data: SessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = await service.log_session(db, user, data)
    return ok(SessionOut.model_validate(s).model_dump())

@router.get("/sessions/my")
async def my_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sessions = await service.get_my_sessions(db, user.user_id)
    return ok([SessionOut.model_validate(s).model_dump() for s in sessions])

@router.post("/sessions/{session_id}/exercises")
async def log_exercise(
    session_id: int,
    data: ExerciseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await service.log_exercise(db, user, session_id, data)
    return ok(ExerciseOut.model_validate(log).model_dump())

@router.get("/records/my")
async def my_records(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    records = await service.get_my_records(db, user.user_id)
    return ok([ExerciseOut.model_validate(r).model_dump() for r in records])
```

- [ ] **Step 5: Commit**

```
git add app/modules/gym/
git commit -m "feat: add gym module (gyms, memberships, sessions, exercise logs, PR tracking)"
```

---

### Task 8: Gamification, FitCoin, Social, Notifications

**Files (all 4 remaining modules):**

- [ ] **Step 1: Write app/modules/gamification/model.py**

```python
import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class ChallengeType(str, enum.Enum):
    weekly  = "weekly"
    monthly = "monthly"
    special = "special"

class UserChallengeStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed   = "completed"
    failed      = "failed"

class BadgeCategory(str, enum.Enum):
    gym    = "gym"
    food   = "food"
    gear   = "gear"
    social = "social"
    streak = "streak"

class Challenge(Base):
    __tablename__ = "challenges"
    challenge_id  = Column(Integer, primary_key=True)
    title         = Column(String(200), nullable=False)
    description   = Column(Text)
    type          = Column(Enum(ChallengeType), nullable=False)
    criteria      = Column(JSONB, nullable=False)
    reward_xp     = Column(Integer, nullable=False)
    reward_fitcoin= Column(Numeric(10, 2), nullable=False, default=0)
    start_date    = Column(Date, nullable=False)
    end_date      = Column(Date, nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)

class UserChallenge(Base):
    __tablename__ = "user_challenges"
    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.challenge_id", ondelete="CASCADE"), nullable=False)
    progress     = Column(JSONB, default=dict)
    status       = Column(Enum(UserChallengeStatus), nullable=False, default=UserChallengeStatus.in_progress)
    completed_at = Column(DateTime)

class Badge(Base):
    __tablename__ = "badges"
    badge_id    = Column(Integer, primary_key=True)
    name        = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon_url    = Column(String(500))
    criteria    = Column(JSONB, nullable=False)
    category    = Column(Enum(BadgeCategory), nullable=False)
```

- [ ] **Step 2: Write app/modules/gamification/schema.py**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from .model import ChallengeType, UserChallengeStatus, BadgeCategory

class ChallengeOut(BaseModel):
    challenge_id:   int
    title:          str
    description:    Optional[str]
    type:           ChallengeType
    criteria:       dict
    reward_xp:      int
    reward_fitcoin: Decimal
    start_date:     date
    end_date:       date
    is_active:      bool
    model_config = {"from_attributes": True}

class UserChallengeOut(BaseModel):
    id:           int
    user_id:      int
    challenge_id: int
    progress:     dict
    status:       UserChallengeStatus
    completed_at: Optional[datetime]
    model_config = {"from_attributes": True}

class BadgeOut(BaseModel):
    badge_id:    int
    name:        str
    description: Optional[str]
    icon_url:    Optional[str]
    category:    BadgeCategory
    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Write app/modules/gamification/service.py**

```python
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import Challenge, UserChallenge, Badge, UserChallengeStatus

async def list_challenges(db: AsyncSession) -> list:
    r = await db.execute(select(Challenge).where(Challenge.is_active == True))
    return r.scalars().all()

async def join_challenge(db: AsyncSession, user: User, challenge_id: int) -> UserChallenge:
    existing = await db.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == user.user_id,
            UserChallenge.challenge_id == challenge_id,
        )
    )
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already joined this challenge")
    uc = UserChallenge(user_id=user.user_id, challenge_id=challenge_id)
    db.add(uc)
    await db.flush()
    return uc

async def get_my_challenges(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id))
    return r.scalars().all()

async def get_leaderboard(db: AsyncSession) -> list:
    from app.modules.users.model import User as UserModel
    r = await db.execute(
        select(UserModel).order_by(UserModel.xp_total.desc()).limit(50)
    )
    return r.scalars().all()

async def list_badges(db: AsyncSession) -> list:
    r = await db.execute(select(Badge))
    return r.scalars().all()
```

- [ ] **Step 4: Write app/modules/gamification/router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from app.modules.users.schema import UserOut
from .schema import ChallengeOut, UserChallengeOut, BadgeOut
from . import service

router = APIRouter()
def ok(data): return {"success": True, "data": data}

@router.get("/challenges")
async def list_challenges(db: AsyncSession = Depends(get_db)):
    cs = await service.list_challenges(db)
    return ok([ChallengeOut.model_validate(c).model_dump() for c in cs])

@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = await service.join_challenge(db, user, challenge_id)
    return ok(UserChallengeOut.model_validate(uc).model_dump())

@router.get("/challenges/my")
async def my_challenges(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ucs = await service.get_my_challenges(db, user.user_id)
    return ok([UserChallengeOut.model_validate(uc).model_dump() for uc in ucs])

@router.get("/leaderboard")
async def leaderboard(db: AsyncSession = Depends(get_db)):
    users = await service.get_leaderboard(db)
    return ok([{"user_id": u.user_id, "display_name": u.display_name, "xp_total": u.xp_total, "current_level": u.current_level} for u in users])

@router.get("/badges")
async def list_badges(db: AsyncSession = Depends(get_db)):
    badges = await service.list_badges(db)
    return ok([BadgeOut.model_validate(b).model_dump() for b in badges])
```

- [ ] **Step 5: Write app/modules/fitcoin/model.py**

```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum, Text, DateTime
from app.core.database import Base

class FitcoinType(str, enum.Enum):
    earn    = "earn"
    spend   = "spend"
    deposit = "deposit"
    refund  = "refund"

class FitcoinSource(str, enum.Enum):
    gear_sale   = "gear_sale"
    challenge   = "challenge"
    referral    = "referral"
    streak      = "streak"
    deposit     = "deposit"
    food_order  = "food_order"
    gear_rental = "gear_rental"
    membership  = "membership"

class FitcoinTransaction(Base):
    __tablename__ = "fitcoin_transactions"
    txn_id       = Column(Integer, primary_key=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type         = Column(Enum(FitcoinType), nullable=False)
    amount       = Column(Numeric(12, 2), nullable=False)
    source       = Column(Enum(FitcoinSource), nullable=False)
    reference_id = Column(Integer)
    balance_after= Column(Numeric(12, 2), nullable=False)
    note         = Column(Text)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 6: Write app/modules/fitcoin/schema.py, service.py, router.py**

**schema.py:**
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .model import FitcoinType, FitcoinSource

class FitcoinTxnOut(BaseModel):
    txn_id:       int
    type:         FitcoinType
    amount:       Decimal
    source:       FitcoinSource
    balance_after:Decimal
    note:         Optional[str]
    created_at:   datetime
    model_config = {"from_attributes": True}

class EarnIn(BaseModel):
    amount:       Decimal
    source:       FitcoinSource
    reference_id: Optional[int] = None
    note:         Optional[str] = None
```

**service.py:**
```python
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import FitcoinTransaction, FitcoinType, FitcoinSource
from .schema import EarnIn

async def get_balance(user: User) -> dict:
    return {"balance": float(user.fitcoin_balance), "user_id": user.user_id}

async def get_history(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(FitcoinTransaction)
        .where(FitcoinTransaction.user_id == user_id)
        .order_by(FitcoinTransaction.created_at.desc())
    )
    return r.scalars().all()

async def earn(db: AsyncSession, user: User, data: EarnIn) -> FitcoinTransaction:
    new_balance = user.fitcoin_balance + data.amount
    txn = FitcoinTransaction(
        user_id=user.user_id,
        type=FitcoinType.earn,
        amount=data.amount,
        source=data.source,
        reference_id=data.reference_id,
        balance_after=new_balance,
        note=data.note,
    )
    db.add(txn)
    user.fitcoin_balance = new_balance
    await db.flush()
    return txn

async def spend(db: AsyncSession, user: User, amount: Decimal, source: FitcoinSource, ref_id: int = None) -> FitcoinTransaction:
    if user.fitcoin_balance < amount:
        err("INSUFFICIENT_FITCOIN", f"Need {amount} FitCoin, have {user.fitcoin_balance}")
    new_balance = user.fitcoin_balance - amount
    txn = FitcoinTransaction(
        user_id=user.user_id,
        type=FitcoinType.spend,
        amount=amount,
        source=source,
        reference_id=ref_id,
        balance_after=new_balance,
    )
    db.add(txn)
    user.fitcoin_balance = new_balance
    await db.flush()
    return txn
```

**router.py:**
```python
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import FitcoinTxnOut, EarnIn
from .model import FitcoinSource
from . import service

router = APIRouter()
def ok(data): return {"success": True, "data": data}

@router.get("/balance")
async def balance(user: User = Depends(get_current_user)):
    return ok(await service.get_balance(user))

@router.get("/history")
async def history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    txns = await service.get_history(db, user.user_id)
    return ok([FitcoinTxnOut.model_validate(t).model_dump() for t in txns])

@router.post("/earn")
async def earn(data: EarnIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    txn = await service.earn(db, user, data)
    return ok(FitcoinTxnOut.model_validate(txn).model_dump())
```

- [ ] **Step 7: Write social and notifications modules**

**app/modules/social/model.py:**
```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class PostType(str, enum.Enum):
    milestone      = "milestone"
    pr             = "pr"
    streak         = "streak"
    transformation = "transformation"
    review         = "review"

class SocialPost(Base):
    __tablename__ = "social_posts"
    post_id        = Column(Integer, primary_key=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type           = Column(Enum(PostType), nullable=False)
    content        = Column(Text)
    media_urls     = Column(JSONB, default=list)
    linked_data    = Column(JSONB, default=dict)
    likes_count    = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**app/modules/social/schema.py:**
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .model import PostType

class PostCreate(BaseModel):
    type:       PostType
    content:    Optional[str] = None
    media_urls: List[str] = []
    linked_data: dict = {}

class PostOut(BaseModel):
    post_id:       int
    user_id:       int
    type:          PostType
    content:       Optional[str]
    media_urls:    list
    likes_count:   int
    created_at:    datetime
    model_config = {"from_attributes": True}
```

**app/modules/social/service.py:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.modules.users.model import User, Follow
from app.core.dependencies import err
from .model import SocialPost
from .schema import PostCreate

async def get_feed(db: AsyncSession, user_id: int) -> list:
    following = select(Follow.following_id).where(Follow.follower_id == user_id)
    r = await db.execute(
        select(SocialPost)
        .where(or_(SocialPost.user_id == user_id, SocialPost.user_id.in_(following)))
        .order_by(SocialPost.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()

async def list_posts(db: AsyncSession) -> list:
    r = await db.execute(select(SocialPost).order_by(SocialPost.created_at.desc()).limit(100))
    return r.scalars().all()

async def create_post(db: AsyncSession, user: User, data: PostCreate) -> SocialPost:
    post = SocialPost(user_id=user.user_id, **data.model_dump())
    db.add(post)
    await db.flush()
    return post

async def delete_post(db: AsyncSession, user: User, post_id: int):
    r = await db.execute(select(SocialPost).where(SocialPost.post_id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        err("NOT_FOUND", "Post not found", 404)
    if post.user_id != user.user_id:
        err("FORBIDDEN", "Not your post", 403)
    await db.delete(post)
```

**app/modules/social/router.py:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import PostCreate, PostOut
from . import service

router = APIRouter()
def ok(data): return {"success": True, "data": data}

@router.get("/feed")
async def feed(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    posts = await service.get_feed(db, user.user_id)
    return ok([PostOut.model_validate(p).model_dump() for p in posts])

@router.get("/posts")
async def all_posts(db: AsyncSession = Depends(get_db)):
    posts = await service.list_posts(db)
    return ok([PostOut.model_validate(p).model_dump() for p in posts])

@router.post("/posts")
async def create_post(data: PostCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = await service.create_post(db, user, data)
    return ok(PostOut.model_validate(post).model_dump())

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.delete_post(db, user, post_id)
    return ok({"deleted": post_id})
```

**app/modules/notifications/model.py:**
```python
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum
from app.core.database import Base

class NotifType(str, enum.Enum):
    streak_reminder = "streak_reminder"
    order_update    = "order_update"
    promo           = "promo"
    challenge       = "challenge"
    gear_return     = "gear_return"
    gym_closed      = "gym_closed"
    gear_approved   = "gear_approved"

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type            = Column(Enum(NotifType), nullable=False)
    title           = Column(String(200), nullable=False)
    message         = Column(Text)
    is_read         = Column(Boolean, default=False, nullable=False)
    action_url      = Column(String(500))
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**app/modules/notifications/schema.py:**
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .model import NotifType

class NotifOut(BaseModel):
    notification_id: int
    type:            NotifType
    title:           str
    message:         Optional[str]
    is_read:         bool
    action_url:      Optional[str]
    created_at:      datetime
    model_config = {"from_attributes": True}
```

**app/modules/notifications/service.py:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .model import Notification

async def get_my_notifs(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()

async def mark_read(db: AsyncSession, user_id: int, notif_id: int):
    await db.execute(
        update(Notification)
        .where(Notification.notification_id == notif_id, Notification.user_id == user_id)
        .values(is_read=True)
    )

async def mark_all_read(db: AsyncSession, user_id: int):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id)
        .values(is_read=True)
    )
```

**app/modules/notifications/router.py:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import NotifOut
from . import service

router = APIRouter()
def ok(data): return {"success": True, "data": data}

@router.get("/")
async def my_notifs(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    notifs = await service.get_my_notifs(db, user.user_id)
    return ok([NotifOut.model_validate(n).model_dump() for n in notifs])

@router.put("/{notif_id}/read")
async def mark_read(notif_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.mark_read(db, user.user_id, notif_id)
    return ok({"read": notif_id})

@router.put("/read-all")
async def mark_all_read(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await service.mark_all_read(db, user.user_id)
    return ok({"message": "All notifications marked as read"})
```

- [ ] **Step 8: Commit all remaining modules**

```
git add app/modules/gamification/ app/modules/fitcoin/ app/modules/social/ app/modules/notifications/
git commit -m "feat: add gamification, fitcoin, social, and notifications modules"
```

---

### Task 9: Database Migration + Final Wiring

- [ ] **Step 1: Run alembic migration**

```bash
cd database
pip install -r requirements.txt
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

- [ ] **Step 2: Seed the database**

```bash
psql -U postgres -d fitfuel -f database/schema.sql
psql -U postgres -d fitfuel -f database/seed.sql
```

- [ ] **Step 3: Start the server**

```bash
uvicorn app.main:app --reload --port 8000
```

Verify: `http://localhost:8000/health` → `{"status": "ok"}`
API docs: `http://localhost:8000/api/docs`

- [ ] **Step 4: Run all tests**

```bash
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Push to remote**

```bash
git push origin main
```

---

## Self-Review Notes

- All 55+ endpoints covered across 9 modules
- BR-11B enforced in gear/service.py and DB CHECK
- BR-13 (50% deposit) enforced in gear/service.py
- BR-18 (guest OTP) enforced in auth/service.py
- BR-24 (FitCoin balance) kept in sync in fitcoin/service.py (DB trigger is secondary safety net)
- BR-37 (gear_lifecycle append-only) enforced by DB trigger; service only does INSERT
- Error format: `{"success": false, "error": "CODE", "message": "..."}` consistent across all modules
- SQLite used for test DB (aiosqlite) to avoid PostgreSQL dependency in CI
- Enum values match schema.sql exactly
