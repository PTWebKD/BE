from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import Challenge, UserChallenge, Badge, UserChallengeStatus


async def list_challenges(db: AsyncSession) -> list:
    r = await db.execute(select(Challenge).where(Challenge.is_active == True))
    return r.scalars().all()


async def get_challenge(db: AsyncSession, challenge_id: int) -> Challenge:
    r = await db.execute(select(Challenge).where(Challenge.challenge_id == challenge_id))
    c = r.scalar_one_or_none()
    if not c:
        err("NOT_FOUND", "Challenge not found", 404)
    return c


async def join_challenge(db: AsyncSession, user: User, challenge_id: int) -> UserChallenge:
    challenge = await get_challenge(db, challenge_id)
    existing = await db.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == user.user_id,
            UserChallenge.challenge_id == challenge_id,
        )
    )
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Already joined this challenge")
    uc = UserChallenge(user_id=user.user_id, challenge_id=challenge_id, progress={})
    db.add(uc)
    await db.flush()
    return uc


async def get_my_challenges(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(UserChallenge).where(UserChallenge.user_id == user_id)
    )
    return r.scalars().all()


async def update_challenge_progress(
    db: AsyncSession, user: User, challenge_id: int, progress: dict
) -> UserChallenge:
    r = await db.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == user.user_id,
            UserChallenge.challenge_id == challenge_id,
        )
    )
    uc = r.scalar_one_or_none()
    if not uc:
        err("NOT_FOUND", "Not participating in this challenge", 404)
    challenge = await get_challenge(db, challenge_id)
    uc.progress = progress
    # Simple completion check based on criteria
    criteria = challenge.criteria or {}
    target = criteria.get("target", None)
    current = progress.get("current", 0)
    if target and current >= target:
        uc.status = UserChallengeStatus.completed
        uc.completed_at = datetime.utcnow()
        # Award XP
        user.xp_total += challenge.reward_xp
    await db.flush()
    return uc


async def get_leaderboard(db: AsyncSession, limit: int = 50) -> list:
    r = await db.execute(
        select(User).order_by(User.xp_total.desc()).limit(limit)
    )
    return r.scalars().all()


async def list_badges(db: AsyncSession) -> list:
    r = await db.execute(select(Badge))
    return r.scalars().all()
