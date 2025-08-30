from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate

class UserCreate(BaseCreate):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль")

class UserUpdate(BaseUpdate):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Email пользователя")

class UserResponse(BaseResponse):
    username: str
    email: str
    is_active: bool = True

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class RefreshToken(BaseModel):
    refresh_token: str
