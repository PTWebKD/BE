import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum
from app.core.database import Base


class NotifType(str, enum.Enum):
    streak_reminder = "streak_reminder"
    order_update = "order_update"
    promo = "promo"
    challenge = "challenge"
    gear_return = "gear_return"
    gym_closed = "gym_closed"
    gear_approved = "gear_approved"


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotifType, name="notif_type"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
