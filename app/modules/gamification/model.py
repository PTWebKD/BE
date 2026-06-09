import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.types import JSON
from app.core.database import Base


class ChallengeType(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"
    special = "special"


class UserChallengeStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class BadgeCategory(str, enum.Enum):
    gym = "gym"
    food = "food"
    gear = "gear"
    social = "social"
    streak = "streak"


class Challenge(Base):
    __tablename__ = "challenges"

    challenge_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(ChallengeType, name="challenge_type"), nullable=False)
    criteria = Column(JSON, nullable=False)
    reward_xp = Column(Integer, nullable=False)
    reward_fitcoin = Column(Numeric(10, 2), nullable=False, default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(
        Integer, ForeignKey("challenges.challenge_id", ondelete="CASCADE"), nullable=False
    )
    progress = Column(JSON, default=dict)
    status = Column(
        Enum(UserChallengeStatus, name="user_challenge_status"),
        nullable=False,
        default=UserChallengeStatus.in_progress,
    )
    completed_at = Column(DateTime)


class Badge(Base):
    __tablename__ = "badges"

    badge_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon_url = Column(String(500))
    criteria = Column(JSON, nullable=False)
    category = Column(Enum(BadgeCategory, name="badge_category"), nullable=False)
