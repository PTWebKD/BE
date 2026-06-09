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
    result = await db.execute(
        select(FitnessPassport).where(FitnessPassport.user_id == user_id)
    )
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
        select(Follow).where(
            Follow.follower_id == follower_id, Follow.following_id == following_id
        )
    )
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already following this user")
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    await db.flush()
    return follow


async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int):
    result = await db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id, Follow.following_id == following_id
        )
    )
    follow = result.scalar_one_or_none()
    if not follow:
        err("NOT_FOUND", "Not following this user", 404)
    await db.delete(follow)
