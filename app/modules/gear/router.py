from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import GearItemCreate, GearItemUpdate, GearItemOut, RentIn, LifecycleOut, TransactionOut
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("")
@router.get("/")
async def list_gear(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_gear(db, category, search)
    return ok([GearItemOut.model_validate(i).model_dump() for i in items])


@router.get("/my/listings")
async def my_listings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await service.get_my_listings(db, user.user_id)
    return ok([GearItemOut.model_validate(i).model_dump() for i in items])


@router.get("/my/rentals")
async def my_rentals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txns = await service.get_my_rentals(db, user.user_id)
    return ok([TransactionOut.model_validate(t).model_dump() for t in txns])


@router.post("/")
async def create_gear(
    data: GearItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await service.create_gear(db, user, data)
    return ok(GearItemOut.model_validate(item).model_dump())


@router.get("/{gear_id}")
async def get_gear(gear_id: str, db: AsyncSession = Depends(get_db)):
    item = await service.get_gear(db, gear_id)
    return ok(GearItemOut.model_validate(item).model_dump())


@router.put("/{gear_id}")
async def update_gear(
    gear_id: str,
    data: GearItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await service.update_gear(db, user, gear_id, data)
    return ok(GearItemOut.model_validate(item).model_dump())


@router.delete("/{gear_id}")
async def delete_gear(
    gear_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_gear(db, user, gear_id)
    return ok({"deleted": gear_id})


@router.post("/{gear_id}/rent")
async def rent_gear(
    gear_id: str,
    data: RentIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txn = await service.rent_gear(db, user, gear_id, data)
    return ok(TransactionOut.model_validate(txn).model_dump())


@router.post("/{gear_id}/return")
async def return_gear(
    gear_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await service.return_gear(db, user, gear_id)
    return ok(GearItemOut.model_validate(item).model_dump())


@router.get("/{gear_id}/lifecycle")
async def get_lifecycle(gear_id: str, db: AsyncSession = Depends(get_db)):
    events = await service.get_lifecycle(db, gear_id)
    return ok([LifecycleOut.model_validate(e).model_dump() for e in events])
