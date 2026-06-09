from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_vendor
from app.core.security import decode_token
from app.modules.users.model import User
from .schema import ProductCreate, ProductOut, OrderCreate, OrderOut, ReviewCreate, ReviewOut
from . import service

router = APIRouter()
_bearer = HTTPBearer(auto_error=False)


def ok(data):
    return {"success": True, "data": data}


async def _optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    result = await db.execute(select(User).where(User.user_id == int(payload["sub"])))
    return result.scalar_one_or_none()


@router.get("/products")
async def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items = await service.list_products(db, search, category)
    return ok([ProductOut.model_validate(p).model_dump() for p in items])


@router.get("/vendor/products")
async def vendor_products(
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    items = await service.get_vendor_products(db, vendor.user_id)
    return ok([ProductOut.model_validate(p).model_dump() for p in items])


@router.get("/vendor/orders")
async def vendor_orders(
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    orders = await service.get_vendor_orders(db, vendor.user_id)
    return ok([OrderOut.model_validate(o).model_dump() for o in orders])


@router.patch("/products/{product_id}/availability")
async def toggle_availability(
    product_id: int,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    p = await service.toggle_product_availability(db, vendor, product_id)
    return ok(ProductOut.model_validate(p).model_dump())


@router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await service.get_product(db, product_id)
    return ok(ProductOut.model_validate(p).model_dump())


@router.post("/products")
async def create_product(
    data: ProductCreate,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    p = await service.create_product(db, vendor, data)
    return ok(ProductOut.model_validate(p).model_dump())


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    data: ProductCreate,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    p = await service.update_product(db, vendor, product_id, data)
    return ok(ProductOut.model_validate(p).model_dump())


@router.post("/orders")
async def place_order(
    data: OrderCreate,
    user: Optional[User] = Depends(_optional_user),
    db: AsyncSession = Depends(get_db),
):
    order = await service.place_order(db, user, data)
    return ok(OrderOut.model_validate(order).model_dump())


@router.get("/orders")
async def my_orders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orders = await service.get_my_orders(db, user.user_id)
    return ok([OrderOut.model_validate(o).model_dump() for o in orders])


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await service.get_order_by_id(db, order_id)
    if order.user_id != user.user_id and order.vendor_id != user.user_id:
        from app.core.dependencies import err
        err("FORBIDDEN", "Not your order", 403)
    return ok(OrderOut.model_validate(order).model_dump())


@router.put("/orders/{order_id}/status")
async def update_status(
    order_id: int,
    status: str,
    vendor: User = Depends(require_vendor),
    db: AsyncSession = Depends(get_db),
):
    order = await service.update_order_status(db, vendor, order_id, status)
    return ok(OrderOut.model_validate(order).model_dump())


@router.post("/products/{product_id}/reviews")
async def create_review(
    product_id: int,
    data: ReviewCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    review = await service.create_review(db, user, product_id, data)
    return ok(ReviewOut.model_validate(review).model_dump())


@router.get("/products/{product_id}/reviews")
async def get_reviews(product_id: int, db: AsyncSession = Depends(get_db)):
    reviews = await service.get_product_reviews(db, product_id)
    return ok([ReviewOut.model_validate(r).model_dump() for r in reviews])
