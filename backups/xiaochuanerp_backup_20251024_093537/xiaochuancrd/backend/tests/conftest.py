"""
Pytest configuration and fixtures for the test suite
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock

from app.core.config import settings
from app.core.database import Base, AsyncSessionLocal, engine


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_session() -> AsyncGenerator:
    """Create a fresh database session for testing."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSessionLocal() as session:
        yield session
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def mock_user():
    """Create a mock user object for testing."""
    user = Mock()
    user.uuid = "test-user-uuid-12345"
    user.username = "test_user"
    user.email = "test@example.com"
    user.role = "user"
    user.is_active = True
    return user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    
    # Mock common session methods
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    
    return session


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    client = AsyncMock()
    
    # Mock common HTTP methods
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    
    return client


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    original_database_url = settings.DATABASE_URL
    
    # Use test database
    settings.DATABASE_URL = "mysql+pymysql://root:Xiaochuan123!@localhost/xiaochuanERP_test"
    
    yield settings
    
    # Restore original settings
    settings.DATABASE_URL = original_database_url


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "测试产品",
        "sku": "TEST001",
        "description": "测试产品描述",
        "price": 100.0,
        "stock_quantity": 50,
        "category_id": 1
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "name": "测试客户",
        "email": "test@example.com",
        "phone": "13800138000",
        "address": "测试地址"
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "customer_id": 1,
        "total_amount": 200.0,
        "status": "pending",
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 100.0
            }
        ]
    }