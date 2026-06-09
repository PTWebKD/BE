from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .model import PostType


class PostCreate(BaseModel):
    type: PostType
    content: Optional[str] = None
    media_urls: List[str] = []
    linked_data: dict = {}


class PostOut(BaseModel):
    post_id: int
    user_id: int
    type: PostType
    content: Optional[str] = None
    media_urls: list
    likes_count: int
    comments_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
