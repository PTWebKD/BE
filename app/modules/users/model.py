import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.core.database import Base


class UserRole(str, enum.Enum):
    member = "member"
    vendor = "vendor"
    gym_owner = "gym_owner"


class FitnessGoal(str, enum.Enum):
    bulk = "bulk"
    cut = "cut"
    maintain = "maintain"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.member)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    fitness_goal = Column(Enum(FitnessGoal, name="fitness_goal"))
    xp_total = Column(Integer, default=0, nullable=False)
    current_level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    fitcoin_balance = Column(Numeric(12, 2), default=0, nullable=False)
    tdee = Column(Integer)
    referred_by = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    last_active_date = Column(Date, nullable=True)
    allergens = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    passport = relationship("FitnessPassport", back_populates="user", uselist=False)
    gear_items = relationship("GearItem", foreign_keys="GearItem.lister_id", back_populates="lister")


class FitnessPassport(Base):
    __tablename__ = "fitness_passport"

    passport_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    total_sessions = Column(Integer, default=0, nullable=False)
    total_volume = Column(Numeric(12, 2), default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    body_weight_log = Column(JSON, default=list)
    body_photos = Column(JSON, default=list)
    milestone_badges = Column(JSON, default=list)
    is_public = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="passport")


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    following_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
