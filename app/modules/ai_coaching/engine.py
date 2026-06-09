from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.gym.model import WorkoutSession, ExerciseLog
from app.modules.food.model import FoodProduct
from app.modules.users.model import User

# ── Layer 2: Muscle → Macro Rules (BR-28/29/34) ─────────────────────────────

# Priority order for tiebreaking (BR-34)
MUSCLE_PRIORITY = ["legs", "back", "chest", "shoulders", "arms", "core"]

MACRO_RULES: dict[tuple[str, str], tuple[int, int, int, str]] = {
    # (muscle_group, fitness_goal) → (min_protein_g, min_carb_g, max_fat_g, label)
    ("legs",      "bulk"):     (30, 50, 20, "high_protein_high_carb"),
    ("legs",      "cut"):      (35, 25, 15, "high_protein_low_carb"),
    ("legs",      "maintain"): (30, 35, 18, "high_protein_moderate_carb"),
    ("back",      "bulk"):     (30, 50, 20, "high_protein_high_carb"),
    ("back",      "cut"):      (35, 25, 15, "high_protein_low_carb"),
    ("back",      "maintain"): (28, 35, 18, "high_protein_moderate_carb"),
    ("chest",     "bulk"):     (28, 45, 20, "high_protein_high_carb"),
    ("chest",     "cut"):      (32, 20, 15, "high_protein_low_carb"),
    ("chest",     "maintain"): (25, 30, 18, "moderate_protein_moderate_carb"),
    ("shoulders", "bulk"):     (25, 40, 20, "moderate_protein_high_carb"),
    ("shoulders", "cut"):      (30, 20, 12, "high_protein_low_carb"),
    ("shoulders", "maintain"): (22, 28, 15, "moderate_protein_moderate_carb"),
    ("arms",      "bulk"):     (25, 40, 18, "moderate_protein_high_carb"),
    ("arms",      "cut"):      (28, 18, 12, "high_protein_low_carb"),
    ("arms",      "maintain"): (20, 25, 15, "moderate_protein_low_carb"),
    ("core",      "bulk"):     (22, 35, 18, "moderate_protein_moderate_carb"),
    ("core",      "cut"):      (25, 18, 12, "moderate_protein_low_carb"),
    ("core",      "maintain"): (20, 25, 15, "moderate_protein_moderate_carb"),
}


def get_macro_profile(muscle_group: str, fitness_goal: str | None) -> tuple:
    """Returns (min_protein_g, min_carb_g, max_fat_g, label)"""
    goal = fitness_goal or "maintain"
    return MACRO_RULES.get((muscle_group, goal), MACRO_RULES[("core", "maintain")])


# ── Layer 1: Tracker — dominant muscle group from session ───────────────────

async def get_session_dominant_muscle(
    db: AsyncSession,
    session_id: int,
    user_id: int,
) -> str | None:
    """
    Returns the dominant muscle group from a completed or active session.
    Dominant = most exercises logged for that group.
    Tiebreak = priority order: legs > back > chest > shoulders > arms > core.
    Returns None if session not found or has no exercises.
    """
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.session_id == session_id)
        .where(WorkoutSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        return None

    # Load exercises for this session
    logs_result = await db.execute(
        select(ExerciseLog).where(ExerciseLog.session_id == session_id)
    )
    exercises = logs_result.scalars().all()

    if not exercises:
        return None

    # Count exercises per muscle group
    counts: dict[str, int] = {}
    for ex in exercises:
        group = ex.muscle_group.value if hasattr(ex.muscle_group, "value") else str(ex.muscle_group)
        counts[group] = counts.get(group, 0) + 1

    # Find max count
    max_count = max(counts.values())
    candidates = [g for g, c in counts.items() if c == max_count]

    # Tiebreak by priority order
    for group in MUSCLE_PRIORITY:
        if group in candidates:
            return group

    # Fallback (should not happen if MUSCLE_PRIORITY is exhaustive)
    return candidates[0]


# ── Layer 3: Recommender — query food products by macro profile ──────────────

def _filter_allergens(products: list, user_allergens: list[str]) -> list:
    """Filter out products whose allergens overlap with the user's allergens."""
    if not user_allergens:
        return products
    user_set = set(a.lower() for a in user_allergens)
    filtered = []
    for p in products:
        product_allergens = p.allergens or []
        product_set = set(a.lower() for a in product_allergens)
        if not product_set.intersection(user_set):
            filtered.append(p)
    return filtered


async def _query_personalized(
    db: AsyncSession,
    min_protein: int,
    min_carb: int,
    max_fat: int,
    user_allergens: list[str],
) -> list:
    """
    Query food products by macro constraints, with allergen filtering.
    Implements BR-30: relax constraints progressively if fewer than 3 results.
    """
    # Attempt 1: full constraints
    stmt = (
        select(FoodProduct)
        .where(FoodProduct.is_available == True)
        .where(FoodProduct.protein_g >= min_protein)
        .where(FoodProduct.carb_g >= min_carb)
        .where(FoodProduct.fat_g <= max_fat)
        .order_by(FoodProduct.avg_rating.desc())
        .limit(30)
    )
    rows = (await db.execute(stmt)).scalars().all()
    results = _filter_allergens(rows, user_allergens)[:3]

    if len(results) >= 3:
        return results

    # Attempt 2: relax fat constraint
    stmt2 = (
        select(FoodProduct)
        .where(FoodProduct.is_available == True)
        .where(FoodProduct.protein_g >= min_protein)
        .where(FoodProduct.carb_g >= min_carb)
        .order_by(FoodProduct.avg_rating.desc())
        .limit(30)
    )
    rows2 = (await db.execute(stmt2)).scalars().all()
    results2 = _filter_allergens(rows2, user_allergens)[:3]

    if len(results2) >= 3:
        return results2

    # Attempt 3: relax carb constraint as well
    stmt3 = (
        select(FoodProduct)
        .where(FoodProduct.is_available == True)
        .where(FoodProduct.protein_g >= min_protein)
        .order_by(FoodProduct.avg_rating.desc())
        .limit(30)
    )
    rows3 = (await db.execute(stmt3)).scalars().all()
    results3 = _filter_allergens(rows3, user_allergens)[:3]

    return results3


async def get_food_recommendations(
    db: AsyncSession,
    user: User | None,
    session_id: int | None,
) -> dict:
    """
    Returns dict with keys: mode, muscle_group, macro_focus, recommendations, reason
    """
    muscle_group: str | None = None
    macro_focus: str | None = None
    mode = "best_seller"
    reason = "Món ăn bán chạy nhất trên nền tảng."
    recommendations = []

    if session_id is not None and user is not None:
        muscle_group = await get_session_dominant_muscle(db, session_id, user.user_id)

        if muscle_group is not None:
            fitness_goal = user.fitness_goal.value if user.fitness_goal else None
            min_protein, min_carb, max_fat, label = get_macro_profile(muscle_group, fitness_goal)
            macro_focus = label

            user_allergens = user.allergens or []
            recommendations = await _query_personalized(
                db, min_protein, min_carb, max_fat, user_allergens
            )

            mode = "personalized"
            reason = f"Bạn vừa tập {muscle_group}. Cần bổ sung {label}."

    # Fall back to best-seller if any condition not met or mode still "best_seller"
    if mode == "best_seller":
        stmt = (
            select(FoodProduct)
            .where(FoodProduct.is_available == True)
            .order_by(FoodProduct.total_orders.desc(), FoodProduct.avg_rating.desc())
            .limit(3)
        )
        rows = (await db.execute(stmt)).scalars().all()
        recommendations = list(rows)
        muscle_group = None
        macro_focus = None

    return {
        "mode": mode,
        "muscle_group": muscle_group,
        "macro_focus": macro_focus,
        "recommendations": recommendations,
        "reason": reason,
    }
