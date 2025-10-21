"""
服务层单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.operation_log_service import OperationLogService
from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate, OperationLogFilter


class TestOperationLogService:
    """操作日志服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.fixture
    def sample_log_data(self):
        """样本日志数据"""
        return OperationLogCreate(
            operation_type="CREATE",
            operation_module="products",
            operation_description="创建新产品",
            target_uuid="test-product-uuid",
            target_name="测试产品",
            before_data=None,
            after_data={"name": "测试产品", "price": 100},
            operator_uuid="test-user-uuid",
            operator_name="测试用户",
            operator_ip="127.0.0.1",
            operation_status="SUCCESS",
            error_message=None
        )
    
    @pytest.fixture
    def sample_log(self):
        """样本日志对象"""
        log = OperationLog()
        log.uuid = "test-log-uuid"
        log.operation_type = "CREATE"
        log.operation_module = "products"
        log.operation_description = "创建新产品"
        log.target_uuid = "test-product-uuid"
        log.target_name = "测试产品"
        log.before_data = None
        log.after_data = {"name": "测试产品", "price": 100}
        log.operator_uuid = "test-user-uuid"
        log.operator_name = "测试用户"
        log.operator_ip = "127.0.0.1"
        log.operation_status = "SUCCESS"
        log.error_message = None
        log.operation_time = datetime.utcnow()
        return log
    
    @pytest.mark.asyncio
    async def test_create_log_success(self, mock_db, sample_log_data):
        """测试创建操作日志成功"""
        # 模拟数据库操作
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # 调用服务方法
        result = await OperationLogService.create_log(mock_db, sample_log_data)
        
        # 验证结果
        assert isinstance(result, OperationLog)
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called
    
    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, mock_db, sample_log):
        """测试带过滤条件的获取日志列表"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_log]
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_db.execute.return_value = mock_count_result
        
        # 创建过滤条件
        filter_data = OperationLogFilter(
            page=1,
            size=20,
            operation_type="CREATE",
            operation_module="products",
            operator_name="测试用户"
        )
        
        # 调用服务方法
        result = await OperationLogService.get_logs(mock_db, filter_data)
        
        # 验证结果
        assert result.total == 1
        assert result.page == 1
        assert result.size == 20
        assert len(result.items) == 1
        assert result.items[0]["operation_type"] == "CREATE"
    
    @pytest.mark.asyncio
    async def test_get_logs_with_date_filters(self, mock_db, sample_log):
        """测试带日期过滤条件的获取日志列表"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_log]
        mock_db.execute.return_value = mock_result
        
        # 模拟总数查询
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_db.execute.return_value = mock_count_result
        
        # 创建日期过滤条件
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        filter_data = OperationLogFilter(
            page=1,
            size=20,
            start_date=start_date,
            end_date=end_date
        )
        
        # 调用服务方法
        result = await OperationLogService.get_logs(mock_db, filter_data)
        
        # 验证结果
        assert result.total == 1
        assert len(result.items) == 1
    
    @pytest.mark.asyncio
    async def test_get_log_by_uuid_success(self, mock_db, sample_log):
        """测试根据UUID获取日志成功"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_log
        mock_db.execute.return_value = mock_result
        
        # 调用服务方法
        result = await OperationLogService.get_log_by_uuid(
            mock_db, "test-log-uuid"
        )
        
        # 验证结果
        assert result is not None
        assert result.uuid == "test-log-uuid"
        assert result.operation_type == "CREATE"
    
    @pytest.mark.asyncio
    async def test_get_log_by_uuid_not_found(self, mock_db):
        """测试根据UUID获取日志不存在"""
        # 模拟数据库查询结果为空
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # 调用服务方法
        result = await OperationLogService.get_log_by_uuid(
            mock_db, "non-existent-uuid"
        )
        
        # 验证结果
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_recent_logs_success(self, mock_db, sample_log):
        """测试获取最近日志成功"""
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_log]
        mock_db.execute.return_value = mock_result
        
        # 调用服务方法
        result = await OperationLogService.get_recent_logs(mock_db, limit=5)
        
        # 验证结果
        assert len(result) == 1
        assert result[0]["operation_type"] == "CREATE"
    
    @pytest.mark.asyncio
    async def test_get_recent_logs_empty(self, mock_db):
        """测试获取最近日志为空"""
        # 模拟数据库查询结果为空
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # 调用服务方法
        result = await OperationLogService.get_recent_logs(mock_db, limit=5)
        
        # 验证结果
        assert len(result) == 0
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_statistics_success(self, mock_db):
        """测试获取统计信息成功"""
        # 模拟类型统计查询结果
        mock_type_result = MagicMock()
        mock_type_result.all.return_value = [("CREATE", 10), ("UPDATE", 5)]
        
        # 模拟模块统计查询结果
        mock_module_result = MagicMock()
        mock_module_result.all.return_value = [("products", 8), ("customers", 7)]
        
        # 模拟操作者统计查询结果
        mock_operator_result = MagicMock()
        mock_operator_result.all.return_value = [("用户A", 6), ("用户B", 4)]
        
        # 模拟今日统计查询结果
        mock_today_result = MagicMock()
        mock_today_result.scalar.return_value = 3
        
        # 模拟总数查询结果
        mock_total_result = MagicMock()
        mock_total_result.scalar.return_value = 15
        
        # 模拟成功率查询结果
        mock_success_result = MagicMock()
        mock_success_result.scalar.return_value = 0.9
        
        # 设置数据库执行返回不同的结果
        def execute_side_effect(query):
            if "operation_type" in str(query):
                return mock_type_result
            elif "operation_module" in str(query):
                return mock_module_result
            elif "operator_name" in str(query):
                return mock_operator_result
            elif "today_start" in str(query):
                return mock_today_result
            elif "total_count" in str(query):
                return mock_total_result
            elif "success_rate" in str(query):
                return mock_success_result
            else:
                return MagicMock()
        
        mock_db.execute.side_effect = execute_side_effect
        
        # 调用服务方法
        result = await OperationLogService.get_statistics(mock_db, days=30)
        
        # 验证结果
        assert "type_statistics" in result
        assert "module_statistics" in result
        assert "operator_statistics" in result
        assert "today_count" in result
        assert "total_count" in result
        assert "success_rate" in result
        
        assert result["type_statistics"]["CREATE"] == 10
        assert result["module_statistics"]["products"] == 8
        assert result["today_count"] == 3
        assert result["total_count"] == 15
        assert result["success_rate"] == 0.9





class TestCozeService:
    """Coze服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_sync_templates_success(self, mock_db):
        """测试同步模板成功"""
        # 导入Coze服务
        from app.services.coze_service import CozeService
        
        # 模拟API响应
        mock_response = {
            "templates": [
                {
                    "id": "template1",
                    "name": "产品分析模板",
                    "description": "用于产品数据分析"
                }
            ]
        }
        
        # 模拟HTTP客户端
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        # 模拟数据库操作
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.execute.return_value = MagicMock()
        
        # 创建服务实例
        service = CozeService(mock_db)
        service.client = mock_client
        
        # 调用同步方法
        result = await service.sync_templates()
        
        # 验证结果
        assert result["success"] is True
        assert "synced" in result
        assert mock_client.get.called
        assert mock_db.add.called
        assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_get_template_by_id_success(self, mock_db):
        """测试根据ID获取模板成功"""
        # 导入Coze服务
        from app.services.coze_service import CozeService
        
        # 模拟数据库查询结果
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = {
            "id": "template1",
            "name": "产品分析模板",
            "content": "模板内容"
        }
        mock_db.execute.return_value = mock_result
        
        # 创建服务实例
        service = CozeService(mock_db)
        
        # 调用获取模板方法
        result = await service.get_template_by_id("template1")
        
        # 验证结果
        assert result is not None
        assert result["id"] == "template1"
        assert result["name"] == "产品分析模板"


class TestAnalysisPredictor:
    """分析预测器测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_predict_sales_trend_success(self, mock_db):
        """测试销售趋势预测成功"""
        # 导入分析预测器
        from app.services.analysis_predictor import AnalysisPredictor
        
        # 模拟历史数据查询结果
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("2024-01", 1000),
            ("2024-02", 1200),
            ("2024-03", 1100)
        ]
        mock_db.execute.return_value = mock_result
        
        # 创建预测器实例
        predictor = AnalysisPredictor(mock_db)
        
        # 调用预测方法
        result = await predictor.predict_sales_trend(
            product_uuid="test-product-uuid",
            periods=3
        )
        
        # 验证结果
        assert "predictions" in result
        assert "trend" in result
        assert "confidence" in result
        assert len(result["predictions"]) == 3
    
    @pytest.mark.asyncio
    async def test_analyze_inventory_optimization(self, mock_db):
        """测试库存优化分析成功"""
        # 导入分析预测器
        from app.services.analysis_predictor import AnalysisPredictor
        
        # 模拟库存数据查询结果






        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("产品A", 100, 50, 200, 10),
            ("产品B", 200, 100, 500, 20)
        ]
        mock_db.execute.return_value = mock_result
        
        # 创建预测器实例
        predictor = AnalysisPredictor(mock_db)
        
        # 调用分析方法
        result = await predictor.analyze_inventory_optimization()
        
        # 验证结果
        assert "analysis" in result
        assert "recommendations" in result
        assert "risk_level" in result
        assert len(result["analysis"]) > 0