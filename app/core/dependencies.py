from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def err(code: str, msg: str, status: int = 400):
    raise HTTPException(
        status_code=status,
        detail={"success": False, "error": code, "message": msg, "detail": None},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.users.model import User

    if not credentials:
        err("UNAUTHORIZED", "Token required", 401)
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        err("UNAUTHORIZED", "Invalid or expired token", 401)
    result = await db.execute(select(User).where(User.user_id == int(payload["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        err("UNAUTHORIZED", "User not found", 401)
    return user


def require_role(*roles: str):
    async def _guard(user=Depends(get_current_user)):
        if user.role.value not in roles:
            err("FORBIDDEN", f"Role {list(roles)} required", 403)
        return user

    return _guard


require_member = require_role("member")
require_vendor = require_role("vendor")
require_gym_owner = require_role("gym_owner")
require_any = get_current_user
