import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.core.database import Base


class GearCategory(str, enum.Enum):
    Weights = "Weights"
    Apparel = "Apparel"
    Supplements = "Supplements"
    Accessories = "Accessories"
    Cardio = "Cardio"
    Recovery = "Recovery"


class ListingType(str, enum.Enum):
    sell = "sell"
    rent = "rent"
    both = "both"


class LifecycleAction(str, enum.Enum):
    listed = "listed"
    sold = "sold"
    rented = "rented"
    returned = "returned"
    relisted = "relisted"


class GearTxnType(str, enum.Enum):
    sale = "sale"
    rental = "rental"


class GearTxnStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    disputed = "disputed"


class GearItem(Base):
    __tablename__ = "gear_items"

    gear_id = Column(String(20), primary_key=True)
    current_owner_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    lister_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    lister_role = Column(String(20), nullable=False, default="gym_owner")
    category = Column(Enum(GearCategory, name="gear_category"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    condition_rating = Column(Integer, nullable=False)
    condition_notes = Column(Text)
    images = Column(JSON, default=list)
    listing_type = Column(Enum(ListingType, name="listing_type"), nullable=False, default=ListingType.rent)
    sell_price = Column(Numeric(12, 2))
    rent_price_day = Column(Numeric(10, 2))
    rent_price_week = Column(Numeric(10, 2))
    deposit_amount = Column(Numeric(12, 2))
    qr_code_url = Column(String(500))
    verified = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    avg_rating = Column(Numeric(2, 1), default=0, nullable=False)
    total_reviews = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lister = relationship("User", foreign_keys=[lister_id], back_populates="gear_items")
    lifecycle = relationship(
        "GearLifecycle", back_populates="gear_item", order_by="GearLifecycle.timestamp"
    )
    transactions = relationship("GearTransaction", back_populates="gear_item")


class GearLifecycle(Base):
    __tablename__ = "gear_lifecycle"

    lifecycle_id = Column(Integer, primary_key=True)
    gear_id = Column(String(20), ForeignKey("gear_items.gear_id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action = Column(Enum(LifecycleAction, name="lifecycle_action"), nullable=False)
    condition_at_time = Column(Integer)
    notes = Column(Text)
    photos = Column(JSON, default=list)
    price_snapshot = Column(Numeric(12, 2))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    gear_item = relationship("GearItem", back_populates="lifecycle")


class GearTransaction(Base):
    __tablename__ = "gear_transactions"

    transaction_id = Column(Integer, primary_key=True)
    gear_id = Column(String(20), ForeignKey("gear_items.gear_id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    type = Column(Enum(GearTxnType, name="gear_txn_type"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    deposit = Column(Numeric(12, 2), default=0, nullable=False)
    fitcoin_used = Column(Numeric(12, 2), default=0, nullable=False)
    rental_start = Column(Date)
    rental_end = Column(Date)
    status = Column(
        Enum(GearTxnStatus, name="gear_txn_status"), nullable=False, default=GearTxnStatus.pending
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    gear_item = relationship("GearItem", back_populates="transactions")
