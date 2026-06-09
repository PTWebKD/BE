from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.users.model import User
from .schema import FitcoinTxnOut, EarnIn, SpendIn
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.get("/balance")
async def balance(user: User = Depends(get_current_user)):
    return ok(await service.get_balance(user))


@router.get("/history")
async def history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txns = await service.get_history(db, user.user_id)
    return ok([FitcoinTxnOut.model_validate(t).model_dump() for t in txns])


@router.post("/earn")
async def earn(
    data: EarnIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txn = await service.earn(db, user, data)
    return ok(FitcoinTxnOut.model_validate(txn).model_dump())


@router.post("/spend")
async def spend(
    data: SpendIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txn = await service.spend(db, user, data)
    return ok(FitcoinTxnOut.model_validate(txn).model_dump())
