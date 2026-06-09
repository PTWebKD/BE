from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import NotifOut
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("/")
async def my_notifs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notifs = await service.get_my_notifs(db, user.user_id)
    return ok([NotifOut.model_validate(n).model_dump() for n in notifs])


@router.put("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.mark_all_read(db, user.user_id)
    return ok({"message": "All notifications marked as read"})


@router.put("/{notif_id}/read")
async def mark_read(
    notif_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.mark_read(db, user.user_id, notif_id)
    return ok({"read": notif_id})
