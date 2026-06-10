from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.dependencies import err
from app.modules.users.model import User, FitnessPassport
from .model import Gym, GymMembership, WorkoutSession, ExerciseLog, MembershipStatus, SessionStatus, GymAnnouncement
from .schema import MembershipCreate, SessionCreate, ExerciseCreate, GymCreate, AnnouncementCreate


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


def _best_volume(sets) -> float:
    """Return the best (max) weight*reps volume across all sets (DB JSON dicts)."""
    return max((s.get("weight", 0) * s.get("reps", 0) for s in (sets or [])), default=0)


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
    if session.status != SessionStatus.active:
        err("BAD_REQUEST", "Cannot log exercises on a completed or cancelled session", 400)
    _check_session_editable(session)

    # PR detection (BR-31): best volume = max(weight × reps) across all sets
    prev = await db.execute(
        select(ExerciseLog)
        .join(WorkoutSession, WorkoutSession.session_id == ExerciseLog.session_id)
        .where(
            WorkoutSession.user_id == user.user_id,
            ExerciseLog.exercise_name == data.exercise_name,
        )
    )
    all_prev = prev.scalars().all()
    max_prev = max((_best_volume(log.sets) for log in all_prev), default=0)
    # data.sets is Pydantic objects → use attribute access
    new_best = max((s.weight * s.reps for s in data.sets), default=0)
    is_pr = new_best > max_prev and new_best > 0

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


def _check_session_editable(session: WorkoutSession) -> None:
    """BR-33: sessions are locked from editing 24 hours after completion."""
    if session.status == SessionStatus.done:
        if session.completed_at and (datetime.utcnow() - session.completed_at).total_seconds() > 86400:
            err("FORBIDDEN", "Session locked — cannot edit after 24 hours (BR-33)", 403)


async def complete_session(db: AsyncSession, user: User, session_id: int) -> dict:
    """Mark a session as done, award XP, update streak, check milestones (BR-18/20/21/22)."""
    # 1. Fetch session
    r = await db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.session_id == session_id,
            WorkoutSession.user_id == user.user_id,
        )
        .options(selectinload(WorkoutSession.exercises))
    )
    session = r.scalar_one_or_none()
    if not session:
        err("NOT_FOUND", "Session not found or not yours", 404)
    if session.status != SessionStatus.active:
        err("BAD_REQUEST", "Session is already done or cancelled", 400)

    # 2. Calculate XP (BR-18)
    total_sets = sum(len(ex.sets or []) for ex in session.exercises)
    xp = max(total_sets * 10, 20)
    pr_count = sum(1 for ex in session.exercises if ex.is_pr)
    xp += pr_count * 50

    # 3. Update streak (BR-20/21)
    today = date.today()
    yesterday = date.fromordinal(today.toordinal() - 1)
    last_active = user.last_active_date

    if last_active is None or last_active < yesterday:
        user.current_streak = 1
    elif last_active == yesterday:
        user.current_streak = (user.current_streak or 0) + 1
    # if last_active == today: keep streak unchanged

    user.last_active_date = today

    # Load passport explicitly to avoid lazy-load crash in async SQLAlchemy (MissingGreenlet)
    r_passport = await db.execute(
        select(FitnessPassport).where(FitnessPassport.user_id == user.user_id)
    )
    passport = r_passport.scalar_one_or_none()
    if not passport:
        err("NOT_FOUND", "Fitness passport not found", 404)

    if passport and user.current_streak > (passport.longest_streak or 0):
        passport.longest_streak = user.current_streak

    # 4. Check streak milestones (BR-22)
    badges_earned = []
    streak_milestones = [
        (7, 50, "streak_7"),
        (30, 200, "streak_30"),
        (100, 500, "streak_100"),
    ]
    if passport is not None:
        existing_badges = [b.get("badge") for b in (passport.milestone_badges or [])]
        for days, coins, badge_name in streak_milestones:
            if user.current_streak >= days and badge_name not in existing_badges:
                user.fitcoin_balance = Decimal(str(user.fitcoin_balance or 0)) + Decimal(str(coins))
                milestone_badges_list = list(passport.milestone_badges or [])
                milestone_badges_list.append(
                    {"badge": badge_name, "earned_at": datetime.utcnow().isoformat()}
                )
                passport.milestone_badges = milestone_badges_list
                badges_earned.append(badge_name)

    # 5. Update FitnessPassport totals
    if passport is not None:
        passport.total_sessions = (passport.total_sessions or 0) + 1
        session_volume = sum(
            float(s.get("weight", 0)) * int(s.get("reps", 0))
            for ex in session.exercises
            for s in (ex.sets or [])
        )
        passport.total_volume = Decimal(str(passport.total_volume or 0)) + Decimal(str(session_volume))

    # 6. Mark session done
    session.status = SessionStatus.done
    session.xp_earned = xp
    session.completed_at = datetime.utcnow()

    # 7. Update user XP
    user.xp_total = (user.xp_total or 0) + xp

    # 8. Flush
    await db.flush()

    # 9. Return result dict
    return {
        "session": session,
        "xp_earned": xp,
        "new_streak": user.current_streak,
        "badges_earned": badges_earned,
    }


async def get_session(db: AsyncSession, user_id: int, session_id: int) -> WorkoutSession:
    r = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.session_id == session_id, WorkoutSession.user_id == user_id)
        .options(selectinload(WorkoutSession.exercises))
    )
    session = r.scalar_one_or_none()
    if not session:
        err("NOT_FOUND", "Session not found or not yours", 404)
    return session


async def get_gym_announcements(db: AsyncSession, gym_id: int) -> list:
    r = await db.execute(
        select(GymAnnouncement).where(GymAnnouncement.gym_id == gym_id).order_by(GymAnnouncement.created_at.desc())
    )
    return r.scalars().all()


async def create_announcement(db: AsyncSession, owner: User, data: AnnouncementCreate) -> GymAnnouncement:
    r = await db.execute(select(Gym).where(Gym.owner_id == owner.user_id))
    gym = r.scalar_one_or_none()
    if not gym:
        err("NOT_FOUND", "No gym found for this owner", 404)
    ann = GymAnnouncement(gym_id=gym.gym_id, **data.model_dump())
    db.add(ann)
    await db.flush()
    return ann


async def delete_announcement(db: AsyncSession, owner: User, announcement_id: int) -> None:
    r = await db.execute(select(GymAnnouncement).where(GymAnnouncement.announcement_id == announcement_id))
    ann = r.scalar_one_or_none()
    if not ann:
        err("NOT_FOUND", "Announcement not found", 404)
    # Verify ownership via gym
    r2 = await db.execute(select(Gym).where(Gym.gym_id == ann.gym_id, Gym.owner_id == owner.user_id))
    if not r2.scalar_one_or_none():
        err("FORBIDDEN", "Not your gym's announcement", 403)
    await db.delete(ann)
    await db.flush()


async def suggest_muscle_group(db: AsyncSession, user_id: int) -> dict:
    """Suggest the least-trained muscle group from the last 7 days (BR-32/34)."""
    # Priority order for tiebreak (BR-34)
    priority = ["legs", "back", "chest", "shoulders", "arms", "core"]

    # 1. Fetch done sessions from last 7 days with exercises
    seven_days_ago = date.today() - timedelta(days=7)
    r = await db.execute(
        select(WorkoutSession)
        .where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatus.done,
            WorkoutSession.date >= seven_days_ago,
        )
        .options(selectinload(WorkoutSession.exercises))
    )
    sessions = r.scalars().all()

    # 2. If no sessions, return first priority group
    if not sessions:
        return {
            "suggested_muscle_group": "legs",
            "reason": "No workouts in the last 7 days — legs are the highest priority muscle group to train.",
        }

    # 3. Count exercises per muscle group
    counts: dict[str, int] = {g: 0 for g in priority}
    for session in sessions:
        for ex in session.exercises:
            group = ex.muscle_group.value if hasattr(ex.muscle_group, "value") else str(ex.muscle_group)
            if group in counts:
                counts[group] += 1

    # 4. Find the least-trained group, using priority order as tiebreak
    min_count = min(counts.values())
    least_trained = [g for g in priority if counts[g] == min_count]
    suggested = least_trained[0]  # priority order already applied via list comprehension

    return {
        "suggested_muscle_group": suggested,
        "reason": f"'{suggested}' has been trained only {min_count} time(s) in the last 7 days — it needs the most attention.",
    }
