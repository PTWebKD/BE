import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Enum, Text, DateTime
from app.core.database import Base


class FitcoinType(str, enum.Enum):
    earn = "earn"
    spend = "spend"
    deposit = "deposit"
    refund = "refund"


class FitcoinSource(str, enum.Enum):
    gear_sale = "gear_sale"
    challenge = "challenge"
    referral = "referral"
    streak = "streak"
    deposit = "deposit"
    food_order = "food_order"
    gear_rental = "gear_rental"
    membership = "membership"


class FitcoinTransaction(Base):
    __tablename__ = "fitcoin_transactions"

    txn_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(FitcoinType, name="fitcoin_type"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    source = Column(Enum(FitcoinSource, name="fitcoin_source"), nullable=False)
    reference_id = Column(Integer)
    balance_after = Column(Numeric(12, 2), nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
