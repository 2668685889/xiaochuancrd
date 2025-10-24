"""
认证相关的Pydantic模式
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class Token(BaseModel):
    """Token响应模式"""
    accessToken: str
    tokenType: str = "bearer"


class TokenData(BaseModel):
    """Token数据模式"""
    username: Optional[str] = None


class UserBase(BaseModel):
    """用户基础模式"""
    username: str
    email: EmailStr
    fullName: str


class UserCreate(BaseModel):
    """用户创建模式"""
    username: str
    email: EmailStr
    password: str
    fullName: str


class UserResponse(BaseModel):
    """用户响应模式"""
    uuid: UUID
    username: str
    email: EmailStr
    fullName: str
    isActive: bool
    isSuperuser: bool
    createdAt: datetime
    lastLogin: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求模式"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模式"""
    accessToken: str
    tokenType: str
    user: UserResponse