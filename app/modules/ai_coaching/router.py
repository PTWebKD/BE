from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_optional_user
from app.modules.users.model import User
from .schema import FoodRecommendationRequest, RecommendedDish
from . import engine

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.post("/food-recommendation")
async def food_recommendation(
    body: FoodRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    """
    Food recommendation endpoint.
    Works for both authenticated users (personalized) and unauthenticated (best seller).
    - Authenticated + session_id provided → personalized recommendations based on
      the dominant muscle group trained and user's fitness goal.
    - No auth or no session_id → best-seller mode (BR-29B).
    """
    result = await engine.get_food_recommendations(db, user, body.session_id)
    return ok({
        "mode": result["mode"],
        "muscle_group": result["muscle_group"],
        "macro_focus": result["macro_focus"],
        "recommendations": [
            RecommendedDish.model_validate(p).model_dump()
            for p in result["recommendations"]
        ],
        "reason": result["reason"],
    })
