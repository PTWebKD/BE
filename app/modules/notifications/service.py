from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.modules.users.model import User
from .model import Notification, NotifType
from .schema import NotifCreate


async def get_my_notifs(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return r.scalars().all()


async def mark_read(db: AsyncSession, user_id: int, notif_id: int):
    await db.execute(
        update(Notification)
        .where(
            Notification.notification_id == notif_id,
            Notification.user_id == user_id,
        )
        .values(is_read=True)
    )
    await db.flush()


async def mark_all_read(db: AsyncSession, user_id: int):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.flush()


async def create_notification(db: AsyncSession, data: NotifCreate) -> Notification:
    notif = Notification(
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
        action_url=data.action_url,
    )
    db.add(notif)
    await db.flush()
    return notif
