from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import FitcoinTransaction, FitcoinType, FitcoinSource
from .schema import EarnIn, SpendIn


async def get_balance(user: User) -> dict:
    return {"balance": float(user.fitcoin_balance), "user_id": user.user_id}


async def get_history(db: AsyncSession, user_id: int) -> list:
    r = await db.execute(
        select(FitcoinTransaction)
        .where(FitcoinTransaction.user_id == user_id)
        .order_by(FitcoinTransaction.created_at.desc())
        .limit(100)
    )
    return r.scalars().all()


async def earn(db: AsyncSession, user: User, data: EarnIn) -> FitcoinTransaction:
    new_balance = user.fitcoin_balance + data.amount
    txn = FitcoinTransaction(
        user_id=user.user_id,
        type=FitcoinType.earn,
        amount=data.amount,
        source=data.source,
        reference_id=data.reference_id,
        balance_after=new_balance,
        note=data.note,
    )
    db.add(txn)
    user.fitcoin_balance = new_balance
    await db.flush()
    return txn


async def spend(db: AsyncSession, user: User, data: SpendIn) -> FitcoinTransaction:
    # BR-24: validate balance
    if user.fitcoin_balance < data.amount:
        err(
            "INSUFFICIENT_FITCOIN",
            f"Need {data.amount} FitCoin but only have {user.fitcoin_balance}",
        )
    new_balance = user.fitcoin_balance - data.amount
    txn = FitcoinTransaction(
        user_id=user.user_id,
        type=FitcoinType.spend,
        amount=data.amount,
        source=data.source,
        reference_id=data.reference_id,
        balance_after=new_balance,
        note=data.note,
    )
    db.add(txn)
    user.fitcoin_balance = new_balance
    await db.flush()
    return txn
