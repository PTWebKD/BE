from pydantic import BaseModel, ConfigDict
from typing import Optional


class FoodRecommendationRequest(BaseModel):
    session_id: Optional[int] = None  # if None → Best Seller mode (BR-29B)


class RecommendedDish(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    name: str
    calories: int
    protein_g: float
    carb_g: float
    fat_g: float
    price: float
    avg_rating: float
    images: list
    vendor_id: int


