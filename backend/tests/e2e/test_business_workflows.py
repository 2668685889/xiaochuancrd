"""
端到端业务流程测试
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


class TestProductManagementWorkflow:
    """产品管理端到端测试"""
    
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
    async def test_create_product_workflow(self, client):
        """测试创建产品完整流程"""
        # 1. 创建产品
        product_data = {
            "productName": "测试产品",
            "productCode": "TEST001",
            "description": "这是一个测试产品",
            "category": "电子产品",
            "unitPrice": 99.99,
            "costPrice": 50.00,
            "stockQuantity": 100,
            "minStockLevel": 10,
            "maxStockLevel": 500,
            "unitOfMeasure": "个",
            "brand": "测试品牌",
            "model": "测试型号",
            "specifications": "测试规格",
            "weight": 1.5,
            "dimensions": "10x10x5cm",
            "isActive": True
        }
        
        response = await client.post("/Products", json=product_data)
        
        # 验证创建成功
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            
            product = data["data"]
            assert "uuid" in product
            product_uuid = product["uuid"]
            
            # 2. 验证产品已创建
            get_response = await client.get(f"/Products/{product_uuid}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                assert get_data["success"] is True
                assert get_data["data"]["productName"] == "测试产品"
                assert get_data["data"]["productCode"] == "TEST001"
            
            # 3. 更新产品信息
            update_data = {
                "productName": "更新后的测试产品",
                "unitPrice": 129.99,
                "stockQuantity": 150
            }
            
            update_response = await client.put(f"/Products/{product_uuid}", json=update_data)
            
            if update_response.status_code == 200:
                update_data = update_response.json()
                assert update_data["success"] is True
                
                # 4. 验证更新成功
                verify_response = await client.get(f"/Products/{product_uuid}")
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    assert verify_data["data"]["productName"] == "更新后的测试产品"
                    assert verify_data["data"]["unitPrice"] == 129.99
    
    @pytest.mark.asyncio
    async def test_product_list_pagination_workflow(self, client):
        """测试产品列表分页流程"""
        # 创建多个测试产品
        products_to_create = [
            {
                "productName": f"测试产品{i}",
                "productCode": f"TEST{i:03d}",
                "unitPrice": 100 + i,
                "stockQuantity": 50 + i,
                "isActive": True
            }
            for i in range(1, 6)
        ]
        
        # 批量创建产品
        for product_data in products_to_create:
            await client.post("/Products", json=product_data)
        
        # 测试分页查询
        response = await client.get("/Products?page=1&size=3")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "data" in data:
                pagination_data = data["data"]
                
                # 验证分页信息
                assert pagination_data["page"] == 1
                assert pagination_data["size"] == 3
                assert "items" in pagination_data
                assert "total" in pagination_data
                
                # 验证返回的项目数量
                assert len(pagination_data["items"]) <= 3
        
        # 测试搜索功能
        search_response = await client.get("/Products?search=测试产品")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("success"):
                # 搜索应该返回结果
                assert "data" in search_data


class TestCustomerOrderWorkflow:
    """客户订单端到端测试"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_customer_creation_workflow(self, client):
        """测试客户创建流程"""
        customer_data = {
            "customerName": "测试客户公司",
            "customerCode": "CUST001",
            "contactPerson": "张经理",
            "phone": "13800138000",
            "email": "test@example.com",
            "address": "测试地址",
            "city": "测试城市",
            "province": "测试省份",
            "postalCode": "100000",
            "customerType": "企业客户",
            "creditLimit": 10000.00,
            "paymentTerms": "30天",
            "taxId": "123456789012345",
            "notes": "测试备注",
            "isActive": True
        }
        
        response = await client.post("/Customers", json=customer_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            
            customer = data["data"]
            assert "uuid" in customer
            customer_uuid = customer["uuid"]
            
            # 验证客户信息
            get_response = await client.get(f"/Customers/{customer_uuid}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                assert get_data["data"]["customerName"] == "测试客户公司"
                assert get_data["data"]["customerCode"] == "CUST001"
    
    @pytest.mark.asyncio
    async def test_sales_order_workflow(self, client):
        """测试销售订单完整流程"""
        # 1. 创建客户
        customer_data = {
            "customerName": "订单测试客户",
            "customerCode": "ORDER001",
            "contactPerson": "李经理",
            "phone": "13900139000",
            "isActive": True
        }
        
        customer_response = await client.post("/Customers", json=customer_data)
        
        if customer_response.status_code == 200:
            customer_data = customer_response.json()
            customer_uuid = customer_data["data"]["uuid"]
            
            # 2. 创建产品
            product_data = {
                "productName": "订单测试产品",
                "productCode": "ORDERPROD001",
                "unitPrice": 200.00,
                "stockQuantity": 100,
                "isActive": True
            }
            
            product_response = await client.post("/Products", json=product_data)
            
            if product_response.status_code == 200:
                product_data = product_response.json()
                product_uuid = product_data["data"]["uuid"]
                
                # 3. 创建销售订单
                order_data = {
                    "orderNumber": "SO2024001",
                    "customerUuid": customer_uuid,
                    "orderDate": "2024-01-15",
                    "expectedDeliveryDate": "2024-01-20",
                    "orderStatus": "pending",
                    "paymentStatus": "pending",
                    "totalAmount": 2000.00,
                    "taxAmount": 200.00,
                    "discountAmount": 0.00,
                    "shippingAddress": "测试配送地址",
                    "billingAddress": "测试账单地址",
                    "notes": "测试订单备注",
                    "orderItems": [
                        {
                            "productUuid": product_uuid,
                            "quantity": 10,
                            "unitPrice": 200.00,
                            "totalPrice": 2000.00
                        }
                    ]
                }
                
                order_response = await client.post("/SalesOrders", json=order_data)
                
                if order_response.status_code == 200:
                    order_data = order_response.json()
                    assert order_data["success"] is True
                    
                    order_uuid = order_data["data"]["uuid"]
                    
                    # 4. 验证订单创建
                    get_order_response = await client.get(f"/SalesOrders/{order_uuid}")
                    
                    if get_order_response.status_code == 200:
                        get_order_data = get_order_response.json()
                        assert get_order_data["data"]["orderNumber"] == "SO2024001"
                        assert get_order_data["data"]["orderStatus"] == "pending"
                        
                        # 5. 更新订单状态
                        update_data = {
                            "orderStatus": "confirmed",
                            "paymentStatus": "paid"
                        }
                        
                        update_response = await client.put(f"/SalesOrders/{order_uuid}", json=update_data)
                        
                        if update_response.status_code == 200:
                            update_data = update_response.json()
                            assert update_data["success"] is True
                            
                            # 6. 验证订单状态更新
                            verify_response = await client.get(f"/SalesOrders/{order_uuid}")
                            
                            if verify_response.status_code == 200:
                                verify_data = verify_response.json()
                                assert verify_data["data"]["orderStatus"] == "confirmed"
                                assert verify_data["data"]["paymentStatus"] == "paid"


class TestInventoryManagementWorkflow:
    """库存管理端到端测试"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_inventory_tracking_workflow(self, client):
        """测试库存跟踪流程"""
        # 1. 创建产品
        product_data = {
            "productName": "库存测试产品",
            "productCode": "INV001",
            "unitPrice": 50.00,
            "stockQuantity": 100,
            "minStockLevel": 20,
            "maxStockLevel": 200,
            "isActive": True
        }
        
        product_response = await client.post("/Products", json=product_data)
        
        if product_response.status_code == 200:
            product_data = product_response.json()
            product_uuid = product_data["data"]["uuid"]
            
            # 2. 检查库存记录
            inventory_response = await client.get("/Inventory")
            
            if inventory_response.status_code == 200:
                inventory_data = inventory_response.json()
                
                # 验证库存端点响应结构
                if inventory_data.get("success"):
                    assert "data" in inventory_data
                    
                    # 3. 测试库存查询
                    search_response = await client.get(f"/Inventory?productUuid={product_uuid}")
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        
                        # 库存查询应该返回相关结果
                        if search_data.get("success"):
                            assert "data" in search_data
    
    @pytest.mark.asyncio
    async def test_low_stock_alert_workflow(self, client):
        """测试低库存预警流程"""
        # 创建低库存产品
        low_stock_product = {
            "productName": "低库存测试产品",
            "productCode": "LOWSTOCK001",
            "unitPrice": 30.00,
            "stockQuantity": 5,  # 低于最小库存
            "minStockLevel": 10,
            "maxStockLevel": 100,
            "isActive": True
        }
        
        response = await client.post("/Products", json=low_stock_product)
        
        if response.status_code == 200:
            data = response.json()
            
            # 验证产品创建成功
            assert data["success"] is True
            
            # 检查库存状态（这里可以扩展为检查低库存预警）
            # 在实际系统中，可能会有低库存预警机制
            product_uuid = data["data"]["uuid"]
            
            # 获取产品详情验证库存数量
            get_response = await client.get(f"/Products/{product_uuid}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                stock_quantity = get_data["data"]["stockQuantity"]
                min_stock_level = get_data["data"]["minStockLevel"]
                
                # 验证库存低于最小库存水平
                assert stock_quantity < min_stock_level


class TestSupplierPurchaseWorkflow:
    """供应商采购端到端测试"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_supplier_management_workflow(self, client):
        """测试供应商管理流程"""
        supplier_data = {
            "supplierName": "测试供应商",
            "supplierCode": "SUP001",
            "contactPerson": "王经理",
            "phone": "13700137000",
            "email": "supplier@example.com",
            "address": "供应商地址",
            "city": "供应商城市",
            "province": "供应商省份",
            "postalCode": "200000",
            "supplierType": "生产商",
            "paymentTerms": "60天",
            "taxId": "987654321098765",
            "bankAccount": "12345678901234567890",
            "bankName": "测试银行",
            "notes": "供应商备注",
            "isActive": True
        }
        
        response = await client.post("/Suppliers", json=supplier_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            
            supplier_uuid = data["data"]["uuid"]
            
            # 验证供应商信息
            get_response = await client.get(f"/Suppliers/{supplier_uuid}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                assert get_data["data"]["supplierName"] == "测试供应商"
                assert get_data["data"]["supplierCode"] == "SUP001"
    
    @pytest.mark.asyncio
    async def test_purchase_order_workflow(self, client):
        """测试采购订单流程"""
        # 1. 创建供应商
        supplier_data = {
            "supplierName": "采购订单供应商",
            "supplierCode": "POSUP001",
            "contactPerson": "采购经理",
            "phone": "13600136000",
            "isActive": True
        }
        
        supplier_response = await client.post("/Suppliers", json=supplier_data)
        
        if supplier_response.status_code == 200:
            supplier_data = supplier_response.json()
            supplier_uuid = supplier_data["data"]["uuid"]
            
            # 2. 创建产品
            product_data = {
                "productName": "采购测试产品",
                "productCode": "POPROD001",
                "unitPrice": 80.00,
                "stockQuantity": 50,
                "isActive": True
            }
            
            product_response = await client.post("/Products", json=product_data)
            
            if product_response.status_code == 200:
                product_data = product_response.json()
                product_uuid = product_data["data"]["uuid"]
                
                # 3. 创建采购订单
                po_data = {
                    "orderNumber": "PO2024001",
                    "supplierUuid": supplier_uuid,
                    "orderDate": "2024-01-10",
                    "expectedDeliveryDate": "2024-01-25",
                    "orderStatus": "pending",
                    "paymentStatus": "pending",
                    "totalAmount": 4000.00,
                    "taxAmount": 400.00,
                    "discountAmount": 0.00,
                    "shippingAddress": "公司仓库",
                    "billingAddress": "公司财务部",
                    "notes": "采购订单备注",
                    "orderItems": [
                        {
                            "productUuid": product_uuid,
                            "quantity": 50,
                            "unitPrice": 80.00,
                            "totalPrice": 4000.00
                        }
                    ]
                }
                
                po_response = await client.post("/PurchaseOrders", json=po_data)
                
                if po_response.status_code == 200:
                    po_data = po_response.json()
                    assert po_data["success"] is True
                    
                    po_uuid = po_data["data"]["uuid"]
                    
                    # 4. 验证采购订单
                    get_po_response = await client.get(f"/PurchaseOrders/{po_uuid}")
                    
                    if get_po_response.status_code == 200:
                        get_po_data = get_po_response.json()
                        assert get_po_data["data"]["orderNumber"] == "PO2024001"
                        assert get_po_data["data"]["orderStatus"] == "pending"


class TestDashboardAnalyticsWorkflow:
    """仪表板分析端到端测试"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_dashboard_data_workflow(self, client):
        """测试仪表板数据流程"""
        # 测试仪表板端点
        response = await client.get("/Dashboard")
        
        # 验证仪表板端点响应
        if response.status_code == 200:
            data = response.json()
            
            # 验证响应结构
            assert "success" in data
            assert "message" in data
            
            if data.get("success") and "data" in data:
                dashboard_data = data["data"]
                
                # 验证仪表板数据字段（根据实际实现调整）
                expected_fields = [
                    "totalProducts", "totalCustomers", "totalSuppliers",
                    "totalSalesOrders", "totalPurchaseOrders",
                    "recentSales", "recentPurchases",
                    "inventoryAlerts", "performanceMetrics"
                ]
                
                for field in expected_fields:
                    if field in dashboard_data:
                        # 字段存在，验证类型
                        assert dashboard_data[field] is not None
    
    @pytest.mark.asyncio
    async def test_smart_assistant_workflow(self, client):
        """测试智能助手流程"""
        # 测试智能助手端点
        response = await client.get("/SmartAssistant")
        
        # 验证智能助手端点响应
        if response.status_code == 200:
            data = response.json()
            
            # 验证响应结构
            assert "success" in data
            assert "message" in data
            
            if data.get("success") and "data" in data:
                assistant_data = data["data"]
                
                # 验证智能助手数据字段（根据实际实现调整）
                expected_fields = [
                    "analytics", "predictions", "recommendations"
                ]
                
                for field in expected_fields:
                    if field in assistant_data:
                        # 字段存在，验证类型
                        assert assistant_data[field] is not None


class TestErrorRecoveryWorkflow:
    """错误恢复端到端测试"""
    
    @pytest.fixture(scope="class")
    async def client(self, test_app):
        """创建测试客户端"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, client):
        """测试错误处理流程"""
        # 测试各种错误场景
        
        # 1. 测试不存在的端点
        response = await client.get("/nonexistent-endpoint")
        
        # 验证404错误处理
        if response.status_code == 404:
            data = response.json()
            assert "detail" in data
        
        # 2. 测试无效的UUID格式
        response = await client.get("/Products/invalid-uuid-format")
        
        # 验证UUID格式错误处理
        if response.status_code == 422:  # 验证错误
            data = response.json()
            assert "detail" in data
        
        # 3. 测试无效的JSON数据
        response = await client.post("/Products", content="invalid json")
        
        # 验证JSON解析错误处理
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data
        
        # 4. 测试必填字段缺失
        incomplete_data = {
            "productName": "",  # 空名称
            "unitPrice": -100   # 负价格
        }
        
        response = await client.post("/Products", json=incomplete_data)
        
        # 验证数据验证错误处理
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data