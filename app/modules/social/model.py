import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.types import JSON
from app.core.database import Base


class PostType(str, enum.Enum):
    milestone = "milestone"
    pr = "pr"
    streak = "streak"
    transformation = "transformation"
    review = "review"


class SocialPost(Base):
    __tablename__ = "social_posts"

    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(PostType, name="post_type"), nullable=False)
    content = Column(Text)
    media_urls = Column(JSON, default=list)
    linked_data = Column(JSON, default=dict)
    likes_count = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
