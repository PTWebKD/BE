from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schema import RegisterIn, LoginIn, OTPRequestIn, OTPVerifyIn
from . import service

router = APIRouter()


def ok(data):
    return {"success": True, "data": data}


@router.post("/register")
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    result = await service.register(db, data)
    return ok(result)


@router.post("/login")
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await service.login(db, data)
    return ok(result)


@router.post("/guest/otp/request")
async def request_otp(data: OTPRequestIn, db: AsyncSession = Depends(get_db)):
    result = await service.request_otp(db, data.phone)
    return ok(result)


@router.post("/guest/otp/verify")
async def verify_otp(data: OTPVerifyIn, db: AsyncSession = Depends(get_db)):
    result = await service.verify_otp(db, data.phone, data.otp_code)
    return ok(result)
