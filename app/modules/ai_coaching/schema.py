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


class FoodRecommendationOut(BaseModel):
    mode: str                       # "personalized" | "best_seller"
    muscle_group: Optional[str]     # main group trained, None for best_seller mode
    macro_focus: Optional[str]      # e.g. "high_protein_high_carb", None for best_seller
    recommendations: list[RecommendedDish]
    reason: str                     # human-readable explanation
