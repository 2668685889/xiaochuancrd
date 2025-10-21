"""
API路由单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.routes.products import router as products_router
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.product_model import ProductModel
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.response import ApiResponse, ApiPaginatedResponse


class TestProductsRoutes:
    """产品路由测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def sample_product_data(self):
        """样本产品数据"""
        return {
            "productName": "测试产品",
            "description": "测试产品描述",
            "categoryUuid": "test-category-uuid",
            "supplierUuid": "test-supplier-uuid",
            "modelUuid": "test-model-uuid",
            "unitPrice": 100.0,
            "costPrice": 80.0,
            "stockQuantity": 100,
            "minStockLevel": 10,
            "maxStockLevel": 1000,
            "isActive": True
        }
    
    @pytest.fixture
    def sample_product(self):
        """样本产品对象"""
        product = Product()
        product.uuid = "test-product-uuid"
        product.product_name = "测试产品"
        product.product_code = "TEST001"
        product.description = "测试产品描述"
        product.category_uuid = "test-category-uuid"
        product.supplier_uuid = "test-supplier-uuid"
        product.model_uuid = "test-model-uuid"
        product.unit_price = 100.0
        product.cost_price = 80.0
        product.stock_quantity = 100
        product.min_stock_level = 10
        product.max_stock_level = 1000
        product.is_active = True
        return product
    
    @pytest.mark.asyncio
    async def test_get_products_success(self, mock_db, sample_product):
        """测试获取产品列表成功"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (sample_product, "测试供应商", "测试型号", {"spec": "value"})
        ]
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await products_router.get_products(
            page=1, size=20, search=None, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert response.message == "获取产品列表成功"
        assert response.data.total == 1
        assert len(response.data.items) == 1
        assert response.data.items[0]["productName"] == "测试产品"
    
    @pytest.mark.asyncio
    async def test_get_products_with_search(self, mock_db, sample_product):
        """测试带搜索条件的获取产品列表"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = [
            (sample_product, "测试供应商", "测试型号", {"spec": "value"})
        ]
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await products_router.get_products(
            page=1, size=20, search="测试", db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert response.data.total == 1
    
    @pytest.mark.asyncio
    async def test_get_product_success(self, mock_db, sample_product):
        """测试获取单个产品成功"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.first.return_value = (
            sample_product, "测试供应商", "测试型号", {"spec": "value"}
        )
        mock_db.execute.return_value = mock_result
        
        # 调用API
        response = await products_router.get_product(
            product_uuid="test-product-uuid", db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert response.message == "获取产品成功"
        assert response.data["productName"] == "测试产品"
        assert response.data["supplierName"] == "测试供应商"
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, mock_db):
        """测试获取不存在的产品"""
        # 模拟数据库查询结果为空
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 验证抛出404异常
        with pytest.raises(HTTPException) as exc_info:
            await products_router.get_product(
                product_uuid="non-existent-uuid", db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "产品不存在" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_product_success(self, mock_db, sample_product_data):
        """测试创建产品成功"""
        # 模拟编码生成
        mock_code_generator = AsyncMock()
        mock_code_generator.return_value = "TEST001"
        
        # 模拟产品编码检查
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 模拟数据库提交和刷新
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # 创建产品数据
        product_create = ProductCreate(**sample_product_data)
        
        # 调用API
        response = await products_router.create_product(
            product_data=product_create, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert response.message == "产品创建成功"
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_create_product_duplicate_code(self, mock_db, sample_product_data):
        """测试创建产品时编码冲突"""
        # 模拟编码生成
        mock_code_generator = AsyncMock()
        mock_code_generator.return_value = "TEST001"
        
        # 模拟产品编码已存在
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Product()
        mock_db.execute.return_value = mock_result
        
        # 创建产品数据
        product_create = ProductCreate(**sample_product_data)
        
        # 验证抛出400异常
        with pytest.raises(HTTPException) as exc_info:
            await products_router.create_product(
                product_data=product_create, db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "产品编码已存在" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_product_success(self, mock_db, sample_product):
        """测试更新产品成功"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_product
        mock_db.execute.return_value = mock_result
        
        # 模拟产品编码检查（无冲突）
        mock_code_check_result = MagicMock()
        mock_code_check_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_code_check_result
        
        # 模拟数据库提交
        mock_db.commit = AsyncMock()
        
        # 更新数据
        update_data = ProductUpdate(productName="更新后的产品名")
        
        # 调用API
        response = await products_router.update_product(
            product_uuid="test-product-uuid", 
            product_data=update_data, 
            db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert response.message == "产品更新成功"
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_update_product_not_found(self, mock_db):
        """测试更新不存在的产品"""
        # 模拟数据库查询结果为空
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 更新数据
        update_data = ProductUpdate(productName="更新后的产品名")
        
        # 验证抛出404异常
        with pytest.raises(HTTPException) as exc_info:
            await products_router.update_product(
                product_uuid="non-existent-uuid", 
                product_data=update_data, 
                db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "产品不存在" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_product_duplicate_code(self, mock_db, sample_product):
        """测试更新产品时编码冲突"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_product
        mock_db.execute.return_value = mock_result
        
        # 模拟产品编码已存在（其他产品使用相同编码）
        mock_code_check_result = MagicMock()
        existing_product = Product()
        existing_product.uuid = "other-product-uuid"
        mock_code_check_result.scalar_one_or_none.return_value = existing_product
        mock_db.execute.return_value = mock_code_check_result
        
        # 更新数据（包含产品编码）
        update_data = ProductUpdate(productCode="DUPLICATE001")
        
        # 验证抛出400异常
        with pytest.raises(HTTPException) as exc_info:
            await products_router.update_product(
                product_uuid="test-product-uuid", 
                product_data=update_data, 
                db=mock_db
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "产品编码已存在" in str(exc_info.value.detail)


class TestCustomersRoutes:
    """客户路由测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_customers_success(self, mock_db):
        """测试获取客户列表成功"""
        # 导入客户路由
        from app.routes.customers import router as customers_router
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await customers_router.get_customers(
            page=1, size=20, search=None, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert "客户列表" in response.message


class TestSuppliersRoutes:
    """供应商路由测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_suppliers_success(self, mock_db):
        """测试获取供应商列表成功"""
        # 导入供应商路由
        from app.routes.suppliers import router as suppliers_router
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await suppliers_router.get_suppliers(
            page=1, size=20, search=None, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert "供应商列表" in response.message


class TestSalesOrdersRoutes:
    """销售订单路由测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_sales_orders_success(self, mock_db):
        """测试获取销售订单列表成功"""
        # 导入销售订单路由
        from app.routes.sales_orders import router as sales_orders_router
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await sales_orders_router.get_sales_orders(
            page=1, size=20, search=None, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert "销售订单列表" in response.message


class TestPurchaseOrdersRoutes:
    """采购订单路由测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_get_purchase_orders_success(self, mock_db):
        """测试获取采购订单列表成功"""
        # 导入采购订单路由
        from app.routes.purchase_orders import router as purchase_orders_router
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_db.execute.return_value = mock_count_result
        
        # 调用API
        response = await purchase_orders_router.get_purchase_orders(
            page=1, size=20, search=None, db=mock_db
        )
        
        # 验证响应
        assert response.success is True
        assert "采购订单列表" in response.message