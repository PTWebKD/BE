from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .model import NotifType


class NotifOut(BaseModel):
    notification_id: int
    type: NotifType
    title: str
    message: Optional[str] = None
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotifCreate(BaseModel):
    user_id: int
    type: NotifType
    title: str
    message: Optional[str] = None
    action_url: Optional[str] = None
