from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    phone: Optional[str] = None
    referred_by: Optional[int] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class OTPRequestIn(BaseModel):
    phone: str


class OTPVerifyIn(BaseModel):
    phone: str
    otp_code: str
