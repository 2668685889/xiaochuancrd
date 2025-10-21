"""
操作日志中间件
自动记录所有API请求的操作日志
"""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
import uuid
from datetime import datetime

from app.core.database import SessionLocal
from app.services.operation_log_service import OperationLogService
from app.schemas.operation_log import OperationLogCreate


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # 跳过某些不需要记录的路径
        if self._should_skip_logging(request):
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        operation_info = await self._extract_operation_info(request)
        
        # 执行请求
        try:
            response = await call_next(request)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 记录成功日志
            await self._log_operation(
                request=request,
                response=response,
                operation_info=operation_info,
                response_time=response_time,
                error=None
            )
            
            return response
            
        except Exception as e:
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 记录失败日志
            await self._log_operation(
                request=request,
                response=None,
                operation_info=operation_info,
                response_time=response_time,
                error=str(e)
            )
            
            # 重新抛出异常
            raise
    
    def _should_skip_logging(self, request: Request) -> bool:
        """判断是否应该跳过日志记录"""
        # 跳过健康检查、文档页面等
        skip_paths = [
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/static',
            '/favicon.ico'
        ]
        
        return any(request.url.path.startswith(path) for path in skip_paths)
    
    async def _extract_operation_info(self, request: Request) -> dict:
        """提取操作信息"""
        # 解析路径和HTTP方法
        path = request.url.path
        method = request.method
        
        # 根据路径和方法确定操作类型和模块
        operation_type, operation_module = self._map_operation_type(path, method)
        
        # 提取目标对象信息
        target_info = self._extract_target_info(path)
        
        return {
            'operation_type': operation_type,
            'operation_module': operation_module,
            'target_info': target_info,
            'path': path,
            'method': method
        }
    
    def _map_operation_type(self, path: str, method: str) -> tuple[str, str]:
        """映射操作类型和模块"""
        # 默认值
        operation_type = 'VIEW'
        operation_module = 'system'
        
        # 根据HTTP方法确定操作类型
        if method == 'GET':
            operation_type = 'VIEW'
        elif method == 'POST':
            operation_type = 'CREATE'
        elif method == 'PUT' or method == 'PATCH':
            operation_type = 'UPDATE'
        elif method == 'DELETE':
            operation_type = 'DELETE'
        
        # 根据路径确定操作模块
        if '/api/v1/Products' in path:
            operation_module = 'products'
        elif '/api/v1/Suppliers' in path:
            operation_module = 'suppliers'
        elif '/api/v1/Inventory' in path:
            operation_module = 'inventory'
        elif '/api/v1/PurchaseOrders' in path:
            operation_module = 'purchase_orders'
        elif '/api/v1/SalesOrders' in path:
            operation_module = 'sales_orders'
        elif '/api/v1/Customers' in path:
            operation_module = 'customers'
        elif '/api/v1/Users' in path:
            operation_module = 'users'
        elif '/api/v1/ProductModels' in path:
            operation_module = 'product_models'
        elif '/api/v1/ProductCategories' in path:
            operation_module = 'product_categories'
        elif '/api/v1/OperationLogs' in path:
            operation_module = 'operation_logs'
        
        return operation_type, operation_module
    
    def _extract_target_info(self, path: str) -> dict:
        """提取目标对象信息"""
        # 从路径中提取UUID（如果有）
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, path)
        
        target_uuid = match.group(0) if match else None
        
        # 根据路径确定目标名称
        target_name = None
        if '/api/v1/Products' in path:
            target_name = '产品'
        elif '/api/v1/Suppliers' in path:
            target_name = '供应商'
        elif '/api/v1/Inventory' in path:
            target_name = '库存记录'
        elif '/api/v1/PurchaseOrders' in path:
            target_name = '采购订单'
        elif '/api/v1/SalesOrders' in path:
            target_name = '销售订单'
        elif '/api/v1/Customers' in path:
            target_name = '客户'
        elif '/api/v1/Users' in path:
            target_name = '用户'
        elif '/api/v1/ProductModels' in path:
            target_name = '产品型号'
        elif '/api/v1/ProductCategories' in path:
            target_name = '产品分类'
        
        return {
            'target_uuid': target_uuid,
            'target_name': target_name
        }
    
    async def _log_operation(
        self, 
        request: Request, 
        response: Response, 
        operation_info: dict, 
        response_time: float,
        error: str = None
    ):
        """记录操作日志"""
        try:
            # 获取操作者信息（从请求头或认证信息中）
            operator_info = await self._extract_operator_info(request)
            
            # 构建操作描述
            operation_description = self._build_operation_description(
                operation_info, response, response_time, error
            )
            
            # 构建日志数据
            log_data = OperationLogCreate(
                operation_type=operation_info['operation_type'],
                operation_module=operation_info['operation_module'],
                operation_description=operation_description,
                target_uuid=operation_info['target_info']['target_uuid'],
                target_name=operation_info['target_info']['target_name'],
                operator_uuid=operator_info['operator_uuid'],
                operator_name=operator_info['operator_name'],
                operator_ip=self._get_client_ip(request),
                operation_status='FAILED' if error else 'SUCCESS',
                error_message=error
            )
            
            # 异步记录日志（不阻塞主流程）
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                try:
                    # 使用异步方式记录日志
                    await OperationLogService.create_log(db, log_data)
                except Exception as e:
                    # 记录日志失败不应该影响主业务流程
                    print(f"记录操作日志失败: {str(e)}")
                
        except Exception as e:
            # 记录日志失败不应该影响主业务流程
            print(f"记录操作日志失败: {str(e)}")
    
    async def _extract_operator_info(self, request: Request) -> dict:
        """提取操作者信息"""
        # 从请求头或认证信息中获取操作者信息
        # 这里需要根据实际的认证系统进行调整
        
        # 默认值（未认证用户）
        operator_uuid = str(uuid.uuid4())  # 生成临时UUID
        operator_name = '匿名用户'
        
        # 尝试从认证信息中获取用户信息
        # 这里需要根据实际的认证系统实现
        # 例如：从JWT token中解析用户信息
        
        # 示例：从请求头中获取用户信息
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # 这里可以解析JWT token获取用户信息
            # 暂时使用默认值
            pass
        
        return {
            'operator_uuid': operator_uuid,
            'operator_name': operator_name
        }
    
    def _build_operation_description(
        self, 
        operation_info: dict, 
        response: Response, 
        response_time: float,
        error: str = None
    ) -> str:
        """构建操作描述"""
        # 获取当前时间（上海时区）
        from datetime import datetime, timezone, timedelta
        shanghai_tz = timezone(timedelta(hours=8))
        current_time = datetime.now(shanghai_tz).strftime('%H:%M:%S')
        
        # 根据操作类型和模块生成业务描述
        operation_type_cn = {
            'CREATE': '添加',
            'UPDATE': '修改', 
            'DELETE': '删除',
            'VIEW': '查看',
            'EXPORT': '导出',
            'IMPORT': '导入'
        }
        
        operation_module_cn = {
            'products': '产品',
            'suppliers': '供应商',
            'inventory': '库存',
            'purchase_orders': '采购订单',
            'sales_orders': '销售订单',
            'customers': '客户',
            'users': '用户',
            'product_models': '产品型号',
            'product_categories': '产品分类',
            'operation_logs': '操作日志'
        }
        
        # 生成业务描述
        operation_type_text = operation_type_cn.get(operation_info['operation_type'], operation_info['operation_type'])
        operation_module_text = operation_module_cn.get(operation_info['operation_module'], operation_info['operation_module'])
        
        if error:
            description = f"在{current_time} {operation_type_text}{operation_module_text}失败 - 错误: {error}"
        else:
            description = f"在{current_time} {operation_type_text}了{operation_module_text}"
        
        return description
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        if request.client:
            return request.client.host
        
        # 从X-Forwarded-For头中获取真实IP（如果使用代理）
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        return 'unknown'