from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .model import FitcoinType, FitcoinSource


class FitcoinTxnOut(BaseModel):
    txn_id: int
    type: FitcoinType
    amount: Decimal
    source: FitcoinSource
    balance_after: Decimal
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EarnIn(BaseModel):
    amount: Decimal
    source: FitcoinSource
    reference_id: Optional[int] = None
    note: Optional[str] = None


class SpendIn(BaseModel):
    amount: Decimal
    source: FitcoinSource
    reference_id: Optional[int] = None
    note: Optional[str] = None
