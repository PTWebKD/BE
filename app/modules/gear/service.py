import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.dependencies import err
from app.modules.users.model import User
from .model import (
    GearItem, GearLifecycle, GearTransaction,
    ListingType, LifecycleAction, GearTxnType, GearTxnStatus,
)
from .schema import GearItemCreate, GearItemUpdate, RentIn

DEPOSIT_RATE = Decimal("0.5")  # BR-13: deposit >= 50% of item value


def _gen_gear_id() -> str:
    uid = uuid.uuid4().hex[:8].upper()
    return f"GEAR-{uid[:4]}-{uid[4:]}"


async def list_gear(db: AsyncSession, category: str = None, search: str = None) -> list:
    q = select(GearItem).where(GearItem.is_available == True)
    if category:
        q = q.where(GearItem.category == category)
    if search:
        q = q.where(GearItem.name.ilike(f"%{search}%"))
    result = await db.execute(q.order_by(GearItem.created_at.desc()))
    return result.scalars().all()


async def get_gear(db: AsyncSession, gear_id: str) -> GearItem:
    result = await db.execute(select(GearItem).where(GearItem.gear_id == gear_id))
    item = result.scalar_one_or_none()
    if not item:
        err("NOT_FOUND", "Gear item not found", 404)
    return item


async def create_gear(db: AsyncSession, user: User, data: GearItemCreate) -> GearItem:
    # BR-11B: member can only list for rent
    if user.role.value == "member" and data.listing_type != ListingType.rent:
        err("MEMBER_CANNOT_SELL", "Members can only list gear for rent (BR-11B)", 400)

    # BR-13: if deposit provided, validate it's >= 50% of reference price
    if data.deposit_amount is not None:
        reference = data.sell_price or (
            data.rent_price_day * 30 if data.rent_price_day else None
        )
        if reference and data.deposit_amount < reference * DEPOSIT_RATE:
            err("DEPOSIT_REQUIRED", "Deposit must be >= 50% of item value (BR-13)", 400)

    gear_id = _gen_gear_id()
    item = GearItem(
        gear_id=gear_id,
        current_owner_id=user.user_id,
        lister_id=user.user_id,
        lister_role=user.role.value,
        category=data.category,
        name=data.name,
        description=data.description,
        condition_rating=data.condition_rating,
        condition_notes=data.condition_notes,
        listing_type=data.listing_type,
        sell_price=data.sell_price,
        rent_price_day=data.rent_price_day,
        rent_price_week=data.rent_price_week,
        deposit_amount=data.deposit_amount,
        images=data.images,
    )
    db.add(item)
    await db.flush()

    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.listed,
        condition_at_time=data.condition_rating,
        price_snapshot=data.sell_price or data.rent_price_day,
    )
    db.add(lc)
    await db.flush()
    return item


async def update_gear(db: AsyncSession, user: User, gear_id: str, data: GearItemUpdate) -> GearItem:
    item = await get_gear(db, gear_id)
    if item.lister_id != user.user_id:
        err("FORBIDDEN", "Not your listing", 403)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    await db.flush()
    return item


async def delete_gear(db: AsyncSession, user: User, gear_id: str):
    item = await get_gear(db, gear_id)
    if item.lister_id != user.user_id:
        err("FORBIDDEN", "Not your listing", 403)
    item.is_available = False
    await db.flush()


async def rent_gear(db: AsyncSession, user: User, gear_id: str, data: RentIn) -> GearTransaction:
    item = await get_gear(db, gear_id)
    if not item.is_available:
        err("VALIDATION_ERROR", "Gear is not currently available")
    if item.listing_type not in (ListingType.rent, ListingType.both):
        err("VALIDATION_ERROR", "This gear is not listed for rent")
    if item.current_owner_id == user.user_id:
        err("VALIDATION_ERROR", "Cannot rent your own gear")
    days = (data.rental_end - data.rental_start).days
    if days <= 0:
        err("VALIDATION_ERROR", "rental_end must be after rental_start")

    daily = item.rent_price_day or Decimal("0")
    total = daily * days
    deposit = item.deposit_amount or (total * DEPOSIT_RATE)

    txn = GearTransaction(
        gear_id=gear_id,
        seller_id=item.current_owner_id,
        buyer_id=user.user_id,
        type=GearTxnType.rental,
        amount=total,
        deposit=deposit,
        rental_start=data.rental_start,
        rental_end=data.rental_end,
        status=GearTxnStatus.active,
    )
    db.add(txn)
    item.is_available = False

    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.rented,
        price_snapshot=total,
    )
    db.add(lc)
    await db.flush()
    return txn


async def return_gear(db: AsyncSession, user: User, gear_id: str) -> GearItem:
    item = await get_gear(db, gear_id)
    result = await db.execute(
        select(GearTransaction).where(
            GearTransaction.gear_id == gear_id,
            GearTransaction.buyer_id == user.user_id,
            GearTransaction.status == GearTxnStatus.active,
        )
    )
    txn = result.scalar_one_or_none()
    if not txn:
        err("NOT_FOUND", "No active rental found for this gear", 404)
    txn.status = GearTxnStatus.completed
    item.is_available = True

    lc = GearLifecycle(
        gear_id=gear_id,
        owner_id=user.user_id,
        action=LifecycleAction.returned,
    )
    db.add(lc)
    await db.flush()
    return item


async def get_my_listings(db: AsyncSession, user_id: int) -> list:
    result = await db.execute(
        select(GearItem).where(GearItem.lister_id == user_id).order_by(GearItem.created_at.desc())
    )
    return result.scalars().all()


async def get_my_rentals(db: AsyncSession, user_id: int) -> list:
    result = await db.execute(
        select(GearTransaction).where(
            GearTransaction.buyer_id == user_id,
            GearTransaction.status == GearTxnStatus.active,
        )
    )
    return result.scalars().all()


async def get_lifecycle(db: AsyncSession, gear_id: str) -> list:
    await get_gear(db, gear_id)
    result = await db.execute(
        select(GearLifecycle)
        .where(GearLifecycle.gear_id == gear_id)
        .order_by(GearLifecycle.timestamp)
    )
    return result.scalars().all()
