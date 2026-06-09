from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import err
from app.modules.users.model import User
from .model import Gym, GymMembership, WorkoutSession, ExerciseLog, MembershipStatus
from .schema import MembershipCreate, SessionCreate, ExerciseCreate, GymCreate


async def list_gyms(db: AsyncSession) -> list:
    r = await db.execute(select(Gym).order_by(Gym.gym_id))
    return r.scalars().all()


async def get_gym(db: AsyncSession, gym_id: int) -> Gym:
    r = await db.execute(select(Gym).where(Gym.gym_id == gym_id))
    g = r.scalar_one_or_none()
    if not g:
        err("NOT_FOUND", "Gym not found", 404)
    return g


async def create_gym(db: AsyncSession, owner: User, data: GymCreate) -> Gym:
    if owner.role.value != "gym_owner":
        err("FORBIDDEN", "Only gym owners can create gyms", 403)
    gym = Gym(owner_id=owner.user_id, **data.model_dump())
    db.add(gym)
    await db.flush()
    return gym


async def get_my_memberships(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(GymMembership)
        .where(GymMembership.user_id == user_id)
        .order_by(GymMembership.created_at.desc())
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


async def log_exercise(
    db: AsyncSession, user: User, session_id: int, data: ExerciseCreate
) -> ExerciseLog:
    r = await db.execute(
        select(WorkoutSession).where(
            WorkoutSession.session_id == session_id,
            WorkoutSession.user_id == user.user_id,
        )
    )
    session = r.scalar_one_or_none()
    if not session:
        err("NOT_FOUND", "Session not found or not yours", 404)

    # PR detection: check if this is the heaviest weight for this exercise
    prev = await db.execute(
        select(ExerciseLog)
        .join(WorkoutSession, WorkoutSession.session_id == ExerciseLog.session_id)
        .where(
            WorkoutSession.user_id == user.user_id,
            ExerciseLog.exercise_name == data.exercise_name,
        )
    )
    all_prev = prev.scalars().all()
    max_prev = max(
        (max((s.get("weight", 0) for s in log.sets or []), default=0) for log in all_prev),
        default=0,
    )
    new_max = max((s.weight for s in data.sets), default=0)
    is_pr = new_max > max_prev and new_max > 0

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
        .join(WorkoutSession, WorkoutSession.session_id == ExerciseLog.session_id)
        .where(WorkoutSession.user_id == user_id, ExerciseLog.is_pr == True)
        .order_by(ExerciseLog.created_at.desc())
    )
    return r.scalars().all()
