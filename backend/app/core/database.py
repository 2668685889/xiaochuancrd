"""
数据库配置和连接管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 创建异步数据库引擎
engine_kwargs = {
    "url": settings.DATABASE_URL,
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

# 如果是调试模式使用NullPool，否则使用连接池
if settings.DEBUG:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

engine = create_async_engine(**engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 创建声明式基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()