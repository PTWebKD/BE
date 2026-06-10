import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.core.database import Base


class SessionStatus(str, enum.Enum):
    active = "active"
    done = "done"
    cancelled = "cancelled"


class MuscleGroup(str, enum.Enum):
    chest = "chest"
    back = "back"
    legs = "legs"
    shoulders = "shoulders"
    arms = "arms"
    core = "core"


class MembershipStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class Gym(Base):
    __tablename__ = "gyms"

    gym_id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)
    phone = Column(String(15))
    opening_hours = Column(JSON, default=dict)
    services = Column(JSON, default=list)
    membership_plans = Column(JSON, default=list)
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GymMembership(Base):
    __tablename__ = "gym_memberships"

    membership_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gyms.gym_id", ondelete="CASCADE"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(
        Enum(MembershipStatus, name="membership_status"), nullable=False, default=MembershipStatus.active
    )
    auto_renew = Column(Boolean, default=False, nullable=False)
    payment_method = Column(String(50))
    amount_paid = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gyms.gym_id", ondelete="SET NULL"))
    date = Column(Date, nullable=False)
    duration_min = Column(Integer)
    status = Column(
        Enum(SessionStatus, name="session_status"), nullable=False, default=SessionStatus.active
    )
    notes = Column(Text)
    xp_earned = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    exercises = relationship(
        "ExerciseLog", back_populates="session", cascade="all, delete-orphan",
    )


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    log_id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer, ForeignKey("workout_sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    exercise_name = Column(String(200), nullable=False)
    muscle_group = Column(Enum(MuscleGroup, name="muscle_group"), nullable=False)
    sets = Column(JSON, nullable=False, default=list)
    is_pr = Column(Boolean, default=False, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("WorkoutSession", back_populates="exercises")


class AnnouncementPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class GymAnnouncement(Base):
    __tablename__ = "gym_announcements"

    announcement_id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gyms.gym_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    priority = Column(Enum(AnnouncementPriority, name="announcement_priority"), default=AnnouncementPriority.medium, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
