from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from .schema import UserOut, UserUpdate, UserUpdateAllergens, PassportOut
from .model import User
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump())


@router.put("/me")
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_user(db, user, data)
    return ok(UserOut.model_validate(updated).model_dump())


@router.put("/me/allergens")
async def update_my_allergens(
    data: UserUpdateAllergens,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user.allergens = data.allergens
    await db.flush()
    return ok(UserOut.model_validate(user).model_dump())


@router.get("/me/passport")
async def get_my_passport(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    passport = await service.get_or_create_passport(db, user.user_id)
    return ok(PassportOut.model_validate(passport).model_dump())


@router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await service.get_user_by_id(db, user_id)
    return ok(UserOut.model_validate(user).model_dump())


@router.post("/{user_id}/follow")
async def follow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.follow_user(db, current_user.user_id, user_id)
    return ok({"followed": user_id})


@router.delete("/{user_id}/follow")
async def unfollow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.unfollow_user(db, current_user.user_id, user_id)
    return ok({"unfollowed": user_id})
