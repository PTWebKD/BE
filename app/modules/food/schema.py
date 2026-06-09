from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .model import OrderStatus


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    calories: int = 0
    protein_g: Decimal = Decimal("0")
    carb_g: Decimal = Decimal("0")
    fat_g: Decimal = Decimal("0")
    category: Optional[str] = None
    badge: Optional[str] = None
    images: List[str] = []


class ProductOut(BaseModel):
    product_id: int
    vendor_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    calories: int
    protein_g: Decimal
    carb_g: Decimal
    fat_g: Decimal
    ingredients: List = []
    allergens: List = []
    images: List[str] = []
    category: Optional[str] = None
    badge: Optional[str] = None
    is_available: bool
    avg_rating: Decimal
    total_reviews: int
    total_orders: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderItem(BaseModel):
    product_id: int
    qty: int
    price: Decimal
    name: str


class OrderCreate(BaseModel):
    items: List[OrderItem]
    delivery_address: str
    vendor_id: int
    guest_phone: Optional[str] = None
    fitcoin_used: Decimal = Decimal("0")
    payment_method: Optional[str] = None
    is_meal_prep: bool = False
    delivery_time: Optional[str] = None


class OrderOut(BaseModel):
    order_id: int
    user_id: Optional[int] = None
    guest_phone: Optional[str] = None
    vendor_id: int
    items: list
    subtotal: Decimal
    total_amount: Decimal
    delivery_address: str
    status: OrderStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    review_id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
