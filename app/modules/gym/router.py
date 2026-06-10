from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_gym_owner
from app.modules.users.model import User
from .model import Gym
from .schema import (
    GymCreate, GymOut, MembershipCreate, MembershipOut,
    SessionCreate, SessionOut, ExerciseCreate, ExerciseOut,
    AnnouncementCreate, AnnouncementOut,
)
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


# 1. GET / — list all gyms (no auth)
@router.get("/")
async def list_gyms(db: AsyncSession = Depends(get_db)):
    gyms = await service.list_gyms(db)
    return ok([GymOut.model_validate(g).model_dump() for g in gyms])


# 2. GET /mine — get the gym owned by current gym_owner (MUST be before /{gym_id})
@router.get("/mine")
async def my_gym(
    user: User = Depends(require_gym_owner),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Gym).where(Gym.owner_id == user.user_id))
    g = r.scalar_one_or_none()
    if not g:
        from app.core.dependencies import err
        err("NOT_FOUND", "No gym found for this owner", 404)
    return ok(GymOut.model_validate(g).model_dump())


# 3. GET /memberships/my
@router.get("/memberships/my")
async def my_memberships(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ms = await service.get_my_memberships(db, user.user_id)
    return ok([MembershipOut.model_validate(m).model_dump() for m in ms])


# 4. POST /memberships
@router.post("/memberships")
async def buy_membership(
    data: MembershipCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    m = await service.buy_membership(db, user, data)
    return ok(MembershipOut.model_validate(m).model_dump())


# 5. POST /sessions — log a new session
@router.post("/sessions")
async def log_session(
    data: SessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s = await service.log_session(db, user, data)
    # Build response manually — avoid model_validate on unflushed ORM object
    # which triggers async lazy-load of 'exercises' (MissingGreenlet crash)
    return ok({
        "session_id": s.session_id,
        "user_id": s.user_id,
        "gym_id": s.gym_id,
        "date": s.date.isoformat(),
        "duration_min": s.duration_min,
        "status": s.status.value,
        "notes": s.notes,
        "xp_earned": s.xp_earned or 0,
        "completed_at": s.completed_at,
        "exercises": [],
        "created_at": s.created_at.isoformat(),
    })


# 6. GET /sessions/my
@router.get("/sessions/my")
async def my_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sessions = await service.get_my_sessions(db, user.user_id)
    return ok([SessionOut.model_validate(s).model_dump() for s in sessions])


# 7. GET /sessions/suggest — MUST be before /sessions/{session_id}
@router.get("/sessions/suggest")
async def suggest_muscle(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await service.suggest_muscle_group(db, user.user_id)
    return ok(result)


# 8. GET /sessions/{session_id} — get a single session (NEW)
@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await service.get_session(db, user.user_id, session_id)
    return ok(SessionOut.model_validate(session).model_dump())


# 9. POST /sessions/{session_id}/complete
@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await service.complete_session(db, user, session_id)
    return ok({
        "session": SessionOut.model_validate(result["session"]).model_dump(),
        "xp_earned": result["xp_earned"],
        "new_streak": result["new_streak"],
        "badges_earned": result["badges_earned"],
    })


# 10. POST /sessions/{session_id}/exercises
@router.post("/sessions/{session_id}/exercises")
async def log_exercise(
    session_id: int,
    data: ExerciseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = await service.log_exercise(db, user, session_id, data)
    return ok(ExerciseOut.model_validate(log).model_dump())


# 11. GET /records/my
@router.get("/records/my")
async def my_records(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    records = await service.get_my_records(db, user.user_id)
    return ok([ExerciseOut.model_validate(r).model_dump() for r in records])


# 12. GET /announcements (gym_owner only)
@router.get("/announcements")
async def list_announcements(
    user: User = Depends(require_gym_owner),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Gym).where(Gym.owner_id == user.user_id))
    gym = r.scalar_one_or_none()
    if not gym:
        return ok([])
    anns = await service.get_gym_announcements(db, gym.gym_id)
    return ok([AnnouncementOut.model_validate(a).model_dump() for a in anns])


# 13. POST /announcements (gym_owner only)
@router.post("/announcements")
async def create_announcement(
    data: AnnouncementCreate,
    user: User = Depends(require_gym_owner),
    db: AsyncSession = Depends(get_db),
):
    ann = await service.create_announcement(db, user, data)
    return ok(AnnouncementOut.model_validate(ann).model_dump())


# 14. DELETE /announcements/{announcement_id} (gym_owner only)
@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    user: User = Depends(require_gym_owner),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_announcement(db, user, announcement_id)
    return ok({"deleted": announcement_id})


# 15. GET /{gym_id} — MUST be last to avoid catching other paths (catch-all by int)
@router.get("/{gym_id}")
async def get_gym(gym_id: int, db: AsyncSession = Depends(get_db)):
    g = await service.get_gym(db, gym_id)
    return ok(GymOut.model_validate(g).model_dump())


# 16. POST / — create gym
@router.post("/")
async def create_gym(
    data: GymCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    gym = await service.create_gym(db, user, data)
    return ok(GymOut.model_validate(gym).model_dump())
