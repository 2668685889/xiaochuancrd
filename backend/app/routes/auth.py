"""
认证路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.schemas.response import ApiResponse
from app.utils.auth import verify_password, create_access_token, get_password_hash
from app.utils.mapper import snake_to_camel

router = APIRouter()
security = HTTPBearer()


@router.post("/auth/login", response_model=ApiResponse[LoginResponse])
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """用户登录"""
    # 查询用户
    result = db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用",
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.username})
    
    # 更新最后登录时间
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 直接使用正确的字段名构建用户响应数据
    user_response = UserResponse(
        uuid=user.uuid,
        username=user.username,
        email=user.email,
        fullName=user.full_name,
        isActive=user.is_active,
        isSuperuser=user.is_superuser,
        createdAt=user.created_at,
        lastLogin=user.last_login,
    )
    
    login_response = LoginResponse(
        accessToken=access_token,
        tokenType="bearer",
        user=user_response
    )
    
    return ApiResponse(
        success=True,
        data=login_response,
        message="登录成功"
    )


@router.post("/auth/refresh", response_model=ApiResponse[dict])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """刷新访问令牌"""
    # 这里可以实现令牌刷新逻辑
    # 目前直接返回错误，需要前端重新登录
    return ApiResponse(
        success=False,
        data={},
        message="令牌已过期，请重新登录"
    )


@router.post("/auth/logout", response_model=ApiResponse[dict])
async def logout():
    """用户登出"""
    return ApiResponse(
        success=True,
        data={"message": "登出成功"},
        message="登出成功"
    )


# 创建默认管理员用户的函数（用于初始化）
async def create_default_admin(db: AsyncSession):
    """创建默认管理员用户"""
    result = await db.execute(select(User).where(User.username == "admin"))
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@inventory.com",
            password_hash=get_password_hash("admin123"),
            full_name="系统管理员",
            is_superuser=True,
        )
        db.add(admin_user)
        await db.commit()
        print("默认管理员用户创建成功")
    
    return admin_user