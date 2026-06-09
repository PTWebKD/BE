from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .model import UserRole, FitnessGoal


class UserOut(BaseModel):
    user_id: int
    email: str
    display_name: str
    role: UserRole
    avatar_url: Optional[str] = None
    fitness_goal: Optional[FitnessGoal] = None
    xp_total: int
    current_level: int
    current_streak: int
    fitcoin_balance: Decimal
    last_active_date: Optional[date] = None
    allergens: List[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    fitness_goal: Optional[FitnessGoal] = None
    phone: Optional[str] = None
    tdee: Optional[int] = None


class UserUpdateAllergens(BaseModel):
    allergens: List[str]


class PassportOut(BaseModel):
    passport_id: int
    total_sessions: int
    total_volume: Decimal
    longest_streak: int
    is_public: bool
    body_weight_log: list = []
    milestone_badges: list = []

    model_config = {"from_attributes": True}
