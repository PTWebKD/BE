import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import err
from app.modules.users.model import User, UserRole, FitnessPassport
from .model import GuestOTP
from .schema import RegisterIn, LoginIn

OTP_TTL_MINUTES = 5
OTP_MAX_ATTEMPTS = 3


async def register(db: AsyncSession, data: RegisterIn) -> dict:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        err("VALIDATION_ERROR", "Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=UserRole.member,
        phone=data.phone,
        referred_by=data.referred_by,
    )
    db.add(user)
    await db.flush()
    passport = FitnessPassport(user_id=user.user_id)
    db.add(passport)
    await db.flush()
    token = create_access_token(
        {"sub": str(user.user_id), "role": user.role.value, "email": user.email}
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.user_id, "role": user.role.value}


async def login(db: AsyncSession, data: LoginIn) -> dict:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        err("UNAUTHORIZED", "Invalid email or password", 401)
    token = create_access_token(
        {"sub": str(user.user_id), "role": user.role.value, "email": user.email}
    )
    return {"access_token": token, "token_type": "bearer", "user_id": user.user_id, "role": user.role.value}


async def request_otp(db: AsyncSession, phone: str) -> dict:
    code = "".join(random.choices(string.digits, k=6))
    expires = datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)
    # Store naive datetime (without tzinfo) for DB compatibility
    otp = GuestOTP(phone=phone, otp_code=code, expires_at=expires.replace(tzinfo=None))
    db.add(otp)
    await db.flush()
    # Production: send SMS via provider. Dev: return code in response.
    return {"message": "OTP sent", "dev_otp": code, "expires_in_minutes": OTP_TTL_MINUTES}


async def verify_otp(db: AsyncSession, phone: str, code: str) -> dict:
    result = await db.execute(
        select(GuestOTP)
        .where(GuestOTP.phone == phone, GuestOTP.used == False)
        .order_by(GuestOTP.created_at.desc())
    )
    otp = result.scalar_one_or_none()
    if not otp:
        err("OTP_EXPIRED", "No active OTP for this phone number")
    if otp.attempts >= OTP_MAX_ATTEMPTS:
        err("OTP_MAX_ATTEMPTS", "Maximum OTP attempts exceeded. Request a new OTP.")
    now = datetime.utcnow()
    if now > otp.expires_at:
        err("OTP_EXPIRED", "OTP has expired. Please request a new one.")
    otp.attempts += 1
    if otp.otp_code != code:
        await db.flush()
        remaining = OTP_MAX_ATTEMPTS - otp.attempts
        err("UNAUTHORIZED", f"Invalid OTP. {remaining} attempts remaining.", 401)
    otp.used = True
    await db.flush()
    return {"verified": True, "phone": phone}
