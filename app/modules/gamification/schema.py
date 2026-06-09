from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from .model import ChallengeType, UserChallengeStatus, BadgeCategory


class ChallengeOut(BaseModel):
    challenge_id: int
    title: str
    description: Optional[str] = None
    type: ChallengeType
    criteria: dict
    reward_xp: int
    reward_fitcoin: Decimal
    start_date: date
    end_date: date
    is_active: bool

    model_config = {"from_attributes": True}


class UserChallengeOut(BaseModel):
    id: int
    user_id: int
    challenge_id: int
    progress: dict
    status: UserChallengeStatus
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BadgeOut(BaseModel):
    badge_id: int
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    category: BadgeCategory

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    user_id: int
    display_name: str
    xp_total: int
    current_level: int
    current_streak: int
