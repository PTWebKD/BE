from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .model import SessionStatus, MuscleGroup, MembershipStatus


class GymOut(BaseModel):
    gym_id: int
    owner_id: int
    name: str
    address: str
    phone: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GymCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    logo_url: Optional[str] = None


class MembershipCreate(BaseModel):
    gym_id: int
    plan_name: str
    start_date: date
    end_date: date
    amount_paid: Decimal
    payment_method: Optional[str] = None
    auto_renew: bool = False


class MembershipOut(BaseModel):
    membership_id: int
    user_id: int
    gym_id: int
    plan_name: str
    start_date: date
    end_date: date
    status: MembershipStatus
    amount_paid: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class SetData(BaseModel):
    reps: int
    weight: float


class ExerciseCreate(BaseModel):
    exercise_name: str
    muscle_group: MuscleGroup
    sets: List[SetData]
    notes: Optional[str] = None


class ExerciseOut(BaseModel):
    log_id: int
    exercise_name: str
    muscle_group: MuscleGroup
    sets: list
    is_pr: bool
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    date: date
    gym_id: Optional[int] = None
    duration_min: Optional[int] = None
    notes: Optional[str] = None


class SessionOut(BaseModel):
    session_id: int
    user_id: int
    gym_id: Optional[int] = None
    date: date
    duration_min: Optional[int] = None
    status: SessionStatus
    notes: Optional[str] = None
    xp_earned: int = 0
    completed_at: Optional[datetime] = None
    exercises: List[ExerciseOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("exercises", mode="before")
    @classmethod
    def safe_exercises(cls, v):
        # Catch MissingGreenlet when relationship not eagerly loaded
        try:
            return list(v) if v is not None else []
        except Exception:
            return []


class SessionCompleteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session: SessionOut
    xp_earned: int
    new_streak: int
    badges_earned: list[str]


class MuscleGroupSuggestion(BaseModel):
    suggested_muscle_group: str
    reason: str


class AnnouncementCreate(BaseModel):
    title: str
    body: str
    priority: str = "medium"


class AnnouncementOut(BaseModel):
    announcement_id: int
    gym_id: int
    title: str
    body: str
    priority: str
    created_at: datetime
    model_config = {"from_attributes": True}
