from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import ChallengeOut, UserChallengeOut, BadgeOut, LeaderboardEntry
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


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
async def my_challenges(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ucs = await service.get_my_challenges(db, user.user_id)
    return ok([UserChallengeOut.model_validate(uc).model_dump() for uc in ucs])


@router.put("/challenges/{challenge_id}/progress")
async def update_progress(
    challenge_id: int,
    progress: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uc = await service.update_challenge_progress(db, user, challenge_id, progress)
    return ok(UserChallengeOut.model_validate(uc).model_dump())


@router.get("/leaderboard")
async def leaderboard(db: AsyncSession = Depends(get_db)):
    users = await service.get_leaderboard(db)
    return ok([
        LeaderboardEntry(
            user_id=u.user_id,
            display_name=u.display_name,
            xp_total=u.xp_total,
            current_level=u.current_level,
            current_streak=u.current_streak,
        ).model_dump()
        for u in users
    ])


@router.get("/badges")
async def list_badges(db: AsyncSession = Depends(get_db)):
    badges = await service.list_badges(db)
    return ok([BadgeOut.model_validate(b).model_dump() for b in badges])
