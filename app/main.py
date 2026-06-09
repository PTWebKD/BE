from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings
from .modules.auth.router import router as auth_router
from .modules.users.router import router as users_router
from .modules.gym.router import router as gym_router
from .modules.food.router import router as food_router
from .modules.gear.router import router as gear_router
from .modules.gamification.router import router as gamification_router
from .modules.fitcoin.router import router as fitcoin_router
from .modules.social.router import router as social_router
from .modules.notifications.router import router as notif_router
from .modules.ai_coaching.router import router as ai_router

app = FastAPI(
    title="FitFuel+ API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        raise exc
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "INTERNAL_ERROR", "message": str(exc), "detail": None},
    )


app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(gym_router, prefix="/api/gym", tags=["Gym"])
app.include_router(food_router, prefix="/api/food", tags=["Food"])
app.include_router(gear_router, prefix="/api/gear", tags=["Gear"])
app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(fitcoin_router, prefix="/api/fitcoin", tags=["FitCoin"])
app.include_router(social_router, prefix="/api/social", tags=["Social"])
app.include_router(notif_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Coaching"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "FitFuel+ API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
