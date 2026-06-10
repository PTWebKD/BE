from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .model import GearCategory, ListingType, GearTxnStatus, GearTxnType


class GearItemCreate(BaseModel):
    name: str
    category: GearCategory
    description: Optional[str] = None
    condition_rating: int
    condition_notes: Optional[str] = None
    listing_type: ListingType = ListingType.rent
    sell_price: Optional[Decimal] = None
    rent_price_day: Optional[Decimal] = None
    rent_price_week: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    images: List[str] = []


class GearItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_rating: Optional[int] = None
    sell_price: Optional[Decimal] = None
    rent_price_day: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    is_available: Optional[bool] = None


class GearItemOut(BaseModel):
    gear_id: str
    lister_id: int
    lister_role: str
    name: str
    category: GearCategory
    description: Optional[str] = None
    condition_rating: int
    listing_type: ListingType
    sell_price: Optional[Decimal] = None
    rent_price_day: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    images: List[str] = []
    verified: bool
    is_available: bool
    avg_rating: Decimal
    total_reviews: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RentIn(BaseModel):
    rental_start: date
    rental_end: date


class LifecycleOut(BaseModel):
    lifecycle_id: int
    action: str
    condition_at_time: Optional[int] = None
    notes: Optional[str] = None
    price_snapshot: Optional[Decimal] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    transaction_id: int
    gear_id: str
    type: GearTxnType
    amount: Decimal
    deposit: Decimal
    rental_start: Optional[date] = None
    rental_end: Optional[date] = None
    status: GearTxnStatus
    created_at: datetime

    model_config = {"from_attributes": True}
