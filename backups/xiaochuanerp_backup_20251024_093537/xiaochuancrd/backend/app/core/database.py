"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# 创建同步数据库引擎
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

engine = create_engine(**engine_kwargs)

# 创建同步会话工厂
SessionLocal = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)

# 创建声明式基类
Base = declarative_base()

# 创建异步数据库引擎
# 将MySQL连接URL转换为异步URL
async_database_url = settings.DATABASE_URL.replace("mysql+pymysql:", "mysql+aiomysql:")
async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db():
    """获取数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取异步数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        yield session