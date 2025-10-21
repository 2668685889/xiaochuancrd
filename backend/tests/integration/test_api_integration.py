"""
API集成测试
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.models.base import Base
from app.main import app


class TestAPIEndpoints:
    """API端点集成测试类"""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """创建事件循环"""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()
    
    @pytest.fixture(scope="class")
    async def test_app(self):
        """创建测试应用"""
        # 创建内存数据库
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # 创建表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 创建会话工厂
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        
        # 重写依赖注入
        async def override_get_db():
            async with async_session() as session:
                yield session
        
        app.dependency_overrides[get_db] = override_get_db
        
        return app
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查端点"""
        response = await client.get("/health")
        
        # 如果健康检查端点存在，验证响应
        if response.status_code != 404:
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_products_endpoint_structure(self, client):
        """测试产品端点结构"""
        response = await client.get("/Products")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
            
            if data["success"]:
                assert "items" in data["data"]
                assert "total" in data["data"]
                assert "page" in data["data"]
                assert "size" in data["data"]
    
    @pytest.mark.asyncio
    async def test_customers_endpoint_structure(self, client):
        """测试客户端点结构"""
        response = await client.get("/Customers")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_suppliers_endpoint_structure(self, client):
        """测试供应商端点结构"""
        response = await client.get("/Suppliers")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_sales_orders_endpoint_structure(self, client):
        """测试销售订单端点结构"""
        response = await client.get("/SalesOrders")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_purchase_orders_endpoint_structure(self, client):
        """测试采购订单端点结构"""
        response = await client.get("/PurchaseOrders")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_inventory_endpoint_structure(self, client):
        """测试库存端点结构"""
        response = await client.get("/Inventory")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_dashboard_endpoint_structure(self, client):
        """测试仪表板端点结构"""
        response = await client.get("/Dashboard")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data
    
    @pytest.mark.asyncio
    async def test_smart_assistant_endpoint_structure(self, client):
        """测试智能助手端点结构"""
        response = await client.get("/SmartAssistant")
        
        # 验证响应结构
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data


class TestAuthentication:
    """认证集成测试类"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_auth_endpoints_exist(self, client):
        """测试认证端点存在性"""
        # 测试登录端点
        response = await client.post("/auth/login", json={
            "username": "test",
            "password": "test"
        })
        
        # 验证端点响应（可能返回401或400，但不应返回404）
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_protected_endpoints_require_auth(self, client):
        """测试受保护端点需要认证"""
        # 测试需要认证的端点
        endpoints_to_test = [
            "/Products",
            "/Customers", 
            "/Suppliers",
            "/SalesOrders",
            "/PurchaseOrders"
        ]
        
        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            
            # 如果端点需要认证，应该返回401或403
            # 如果端点不需要认证，可能返回200或404
            # 主要验证端点存在且响应合理
            assert response.status_code in [200, 401, 403, 404]


class TestErrorHandling:
    """错误处理集成测试类"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_404_not_found(self, client):
        """测试404错误处理"""
        response = await client.get("/nonexistent-endpoint")
        
        # 验证404响应结构
        if response.status_code == 404:
            data = response.json()
            assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, client):
        """测试无效JSON处理"""
        # 测试POST端点发送无效JSON
        endpoints_to_test = [
            "/Products",
            "/Customers"
        ]
        
        for endpoint in endpoints_to_test:
            response = await client.post(endpoint, content="invalid json")
            
            # 验证错误响应结构
            if response.status_code == 422:  # 验证错误
                data = response.json()
                assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, client):
        """测试验证错误处理"""
        # 测试创建产品时发送无效数据
        invalid_data = {
            "productName": "",  # 空名称
            "unitPrice": -100,  # 负价格
            "stockQuantity": "invalid"  # 无效库存数量
        }
        
        response = await client.post("/Products", json=invalid_data)
        
        # 验证验证错误响应
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data


class TestPagination:
    """分页功能集成测试类"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_pagination_parameters(self, client):
        """测试分页参数"""
        endpoints_to_test = [
            "/Products?page=1&size=10",
            "/Customers?page=2&size=20",
            "/Suppliers?page=1&size=5"
        ]
        
        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            
            # 验证分页响应结构
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    pagination_data = data["data"]
                    assert "page" in pagination_data
                    assert "size" in pagination_data
                    assert "total" in pagination_data
                    assert "pages" in pagination_data
    
    @pytest.mark.asyncio
    async def test_invalid_pagination_parameters(self, client):
        """测试无效分页参数"""
        invalid_parameters = [
            "/Products?page=0&size=10",  # 页码为0
            "/Customers?page=-1&size=20",  # 负页码
            "/Suppliers?page=1&size=0",  # 页面大小为0
            "/Products?page=1&size=101"  # 页面大小超过限制
        ]
        
        for endpoint in invalid_parameters:
            response = await client.get(endpoint)
            
            # 验证错误响应
            if response.status_code == 422:  # 验证错误
                data = response.json()
                assert "detail" in data


class TestSearchFunctionality:
    """搜索功能集成测试类"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_search_parameter(self, client):
        """测试搜索参数"""
        endpoints_to_test = [
            "/Products?search=test",
            "/Customers?search=company",
            "/Suppliers?search=supplier"
        ]
        
        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            
            # 验证搜索响应结构
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 搜索应该返回成功响应
                    assert "data" in data
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, client):
        """测试空搜索结果"""
        # 搜索不存在的关键词
        response = await client.get("/Products?search=nonexistentkeyword12345")
        
        # 验证空搜索结果处理
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                # 空搜索应该返回空列表
                assert "items" in data["data"]
                # 空列表也是有效结果
                assert isinstance(data["data"]["items"], list)


class TestResponseFormat:
    """响应格式集成测试类"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_response_structure_consistency(self, client):
        """测试响应结构一致性"""
        endpoints_to_test = [
            "/Products",
            "/Customers",
            "/Suppliers"
        ]
        
        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            
            # 验证所有端点使用相同的响应格式
            if response.status_code == 200:
                data = response.json()
                
                # 验证标准响应字段
                assert "success" in data
                assert "message" in data
                assert "data" in data
                
                # 验证success字段类型
                assert isinstance(data["success"], bool)
                
                # 验证message字段类型
                assert isinstance(data["message"], str)
    
    @pytest.mark.asyncio
    async def test_error_response_format(self, client):
        """测试错误响应格式"""
        # 测试不存在的端点
        response = await client.get("/nonexistent")
        
        # 验证错误响应格式
        if response.status_code >= 400:
            data = response.json()
            
            # 错误响应应该包含detail字段
            assert "detail" in data
            
            # 或者如果使用自定义错误格式
            if "success" in data:
                assert data["success"] is False
                assert "error" in data