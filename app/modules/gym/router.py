from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import (
    GymCreate, GymOut, MembershipCreate, MembershipOut,
    SessionCreate, SessionOut, ExerciseCreate, ExerciseOut,
)
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("/")
async def list_gyms(db: AsyncSession = Depends(get_db)):
    gyms = await service.list_gyms(db)
    return ok([GymOut.model_validate(g).model_dump() for g in gyms])


@router.get("/{gym_id}")
async def get_gym(gym_id: int, db: AsyncSession = Depends(get_db)):
    g = await service.get_gym(db, gym_id)
    return ok(GymOut.model_validate(g).model_dump())


@router.post("/")
async def create_gym(
    data: GymCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    gym = await service.create_gym(db, user, data)
    return ok(GymOut.model_validate(gym).model_dump())


@router.get("/memberships/my")
async def my_memberships(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
async def my_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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
async def my_records(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    records = await service.get_my_records(db, user.user_id)
    return ok([ExerciseOut.model_validate(r).model_dump() for r in records])
