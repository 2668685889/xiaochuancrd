"""
Coze数据上传服务
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import json
import httpx
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.coze import (
    CozeTableInfo,
    CozeUploadFilter,
    CozeUploadStatus,
    CozeUploadHistory,
    CozeApiConfig
)
from app.core.database import get_db, Base
from app.models.operation_log import OperationLog
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.inventory import InventoryRecord
from app.models.sales_order import SalesOrder
from app.models.purchase_order import PurchaseOrder
from app.models.product_category import ProductCategory
from app.models.product_model import ProductModel
from app.models.user import User
from app.models.coze_sync_config import CozeSyncConfig  # 添加Coze同步配置模型导入
from app.utils.mapper import snake_to_camel  # 添加命名转换工具导入
from app.services.cdc_service import CDCService  # 添加CDC服务导入

# 配置logger以确保输出到控制台
logger = logging.getLogger(__name__)

# 清除所有现有的处理器
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# 强制设置logger级别为DEBUG
logger.setLevel(logging.DEBUG)

# 创建新的处理器
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False  # 防止日志传播到根logger，避免重复输出

# 强制设置所有相关logger的级别为DEBUG
logging.getLogger('app.services.coze_service').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('httpcore').setLevel(logging.DEBUG)

# 强制添加处理器到相关logger
for log_name in ['app.services.coze_service', 'httpx', 'httpcore']:
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    for handler in log.handlers[:]:
        log.removeHandler(handler)
    log.addHandler(handler)
    log.propagate = False


class CozeService:
    """Coze数据同步服务类"""
    
    # 实时同步配置存储
    _sync_configs = {}
    
    # 预定义的表配置（用于向后兼容）
    PREDEFINED_TABLES = {
        "products": {
            "display_name": "产品表",
            "description": "产品基本信息表",
            "model": Product,
            "fields": ["uuid", "product_name", "product_code", "unit_price", "current_quantity", "min_quantity", "max_quantity", "supplier_uuid", "category_uuid", "created_at", "updated_at"]
        },
        "suppliers": {
            "display_name": "供应商表", 
            "description": "供应商信息表",
            "model": Supplier,
            "fields": ["uuid", "supplier_name", "supplier_code", "contact_person", "phone", "email", "address", "created_at", "updated_at"]
        },
        "customers": {
            "display_name": "客户表",
            "description": "客户信息表", 
            "model": Customer,
            "fields": ["uuid", "customer_name", "customer_code", "contact_person", "phone", "email", "address", "is_active", "created_at", "updated_at", "deleted_at"]
        },
        "inventory_records": {
            "display_name": "库存表",
            "description": "库存记录表",
            "model": InventoryRecord,
            "fields": ["uuid", "product_uuid", "change_type", "quantity_change", "current_quantity", "remark", "record_date", "created_by", "created_at"]
        },
        "sales_orders": {
            "display_name": "销售订单表",
            "description": "销售订单记录表",
            "model": SalesOrder,
            "fields": ["uuid", "order_number", "customer_uuid", "total_amount", "status", "order_date", "created_at", "updated_at"]
        },
        "purchase_orders": {
            "display_name": "采购订单表", 
            "description": "采购订单记录表",
            "model": PurchaseOrder,
            "fields": ["uuid", "order_number", "supplier_uuid", "total_amount", "status", "order_date", "created_at", "updated_at"]
        },
        "product_categories": {
            "display_name": "产品分类表",
            "description": "产品分类信息表",
            "model": ProductCategory,
            "fields": ["uuid", "category_name", "category_code", "parent_uuid", "description", "created_at", "updated_at"]
        },
        "product_models": {
            "display_name": "产品型号表",
            "description": "产品型号信息表",
            "model": ProductModel,
            "fields": ["uuid", "model_name", "model_code", "product_uuid", "specifications", "created_at", "updated_at"]
        }
    }
    
    @classmethod
    async def get_all_tables(cls, db: AsyncSession) -> Dict[str, Dict[str, Any]]:
        """获取数据库中所有表的动态信息"""
        try:
            # 使用异步方式获取数据库中的所有表
            # 首先获取表名列表
            result = await db.execute(text("SHOW TABLES"))
            table_names = [row[0] for row in result.fetchall()]
            
            logger.info(f"动态获取数据库表: 发现 {len(table_names)} 个表")
            logger.info(f"表名列表: {table_names}")
            
            all_tables = {}
            
            for table_name in table_names:
                # 跳过系统表
                if table_name.startswith('_') or table_name in ['alembic_version']:
                    logger.debug(f"跳过系统表: {table_name}")
                    continue
                    
                logger.info(f"处理表: {table_name}")
                
                # 获取表的列信息
                result = await db.execute(text(f"DESCRIBE {table_name}"))
                columns = result.fetchall()
                
                # 构建字段列表
                fields = [col[0] for col in columns]  # 第一列是字段名
                
                # 获取表注释（如果有）
                table_comment = None
                try:
                    # 尝试获取表注释
                    result = await db.execute(text(f"SHOW TABLE STATUS LIKE '{table_name}'"))
                    table_status = result.fetchone()
                    if table_status:
                        table_comment = table_status.Comment
                except Exception as e:
                    logger.debug(f"获取表 {table_name} 注释失败: {str(e)}")
                    table_comment = None
                
                # 构建表配置
                table_config = {
                    "display_name": cls._get_display_name(table_name),
                    "description": table_comment or f"{table_name} 数据表",
                    "fields": fields,
                    "is_dynamic": True  # 标记为动态发现的表
                }
                
                # 如果表在预定义列表中，使用预定义的模型
                if table_name in cls.PREDEFINED_TABLES:
                    table_config.update({
                        "model": cls.PREDEFINED_TABLES[table_name]["model"],
                        "is_dynamic": False  # 标记为预定义表
                    })
                    logger.debug(f"表 {table_name} 是预定义表")
                else:
                    logger.debug(f"表 {table_name} 是动态发现的表")
                
                all_tables[table_name] = table_config
            
            logger.info(f"动态表获取完成: 共处理 {len(all_tables)} 个表")
            return all_tables
            
        except Exception as e:
            logger.error(f"获取数据库表信息失败: {str(e)}")
            # 如果动态获取失败，返回预定义的表
            logger.warning("动态表获取失败，回退到预定义表")
            return cls.PREDEFINED_TABLES
    
    @classmethod
    def _get_display_name(cls, table_name: str) -> str:
        """根据表名生成显示名称"""
        # 预定义表的显示名称
        predefined_names = {
            "products": "产品表",
            "suppliers": "供应商表",
            "customers": "客户表",
            "inventory_records": "库存记录表",
            "sales_orders": "销售订单表",
            "purchase_orders": "采购订单表",
            "product_categories": "产品分类表",
            "product_models": "产品型号表",
            "users": "用户表",
            "operation_logs": "操作日志表",
            "sales_order_items": "销售订单明细表",
            "purchase_order_items": "采购订单明细表"
        }
        
        if table_name in predefined_names:
            return predefined_names[table_name]
        
        # 动态生成显示名称
        # 将蛇形命名转换为中文描述
        name_parts = table_name.split('_')
        chinese_parts = []
        
        for part in name_parts:
            if part == 'orders':
                chinese_parts.append('订单')
            elif part == 'items':
                chinese_parts.append('明细')
            elif part == 'logs':
                chinese_parts.append('日志')
            elif part == 'records':
                chinese_parts.append('记录')
            elif part == 'categories':
                chinese_parts.append('分类')
            elif part == 'models':
                chinese_parts.append('型号')
            elif part == 'users':
                chinese_parts.append('用户')
            elif part == 'customers':
                chinese_parts.append('客户')
            elif part == 'suppliers':
                chinese_parts.append('供应商')
            elif part == 'products':
                chinese_parts.append('产品')
            elif part == 'inventory':
                chinese_parts.append('库存')
            elif part == 'sales':
                chinese_parts.append('销售')
            elif part == 'purchase':
                chinese_parts.append('采购')
            else:
                chinese_parts.append(part)
        
        return ''.join(chinese_parts) + '表'
    
    # 上传任务状态存储
    _upload_tasks = {}
    
    @classmethod
    async def create_sync_config(
        cls,
        table_name: str,
        coze_workflow_id: str = None,
        coze_workflow_id_insert: str = None,
        coze_workflow_id_update: str = None,
        coze_workflow_id_delete: str = None,
        coze_api_url: str = "https://api.coze.cn",
        coze_api_key: str = None,  # 注意：这里应该接收大驼峰命名的参数
        sync_on_insert: bool = True,
        sync_on_update: bool = True,
        sync_on_delete: bool = False,
        user_id: UUID = None,
        selected_fields: List[str] = None,
        config_title: str = None,
        db: AsyncSession = None
    ) -> str:
        """创建实时同步配置（数据库持久化版本）"""
        
        if not db:
            raise ValueError("数据库会话(db)是必需的参数")
        
        # 动态获取所有表信息
        all_tables = await cls.get_all_tables(db)
        
        # 验证表名是否存在
        if table_name not in all_tables:
            raise ValueError(f"表 {table_name} 不存在于数据库中")
        
        # 验证字段是否有效
        available_fields = all_tables[table_name]["fields"]
        if selected_fields:
            for field in selected_fields:
                if field not in available_fields:
                    raise ValueError(f"字段 {field} 不在表 {table_name} 中")
        
        # 确定使用的工作流ID（向后兼容）
        # 优先使用独立的工作流ID，如果没有设置则使用主工作流ID
        workflow_id_insert = coze_workflow_id_insert or coze_workflow_id
        workflow_id_update = coze_workflow_id_update or coze_workflow_id
        workflow_id_delete = coze_workflow_id_delete or coze_workflow_id
        
        # 创建数据库记录
        sync_config = CozeSyncConfig(
            config_title=config_title or f"{table_name} - 实时同步",
            table_name=table_name,
            coze_workflow_id=coze_workflow_id or workflow_id_insert or workflow_id_update or workflow_id_delete,
            coze_workflow_id_insert=workflow_id_insert,
            coze_workflow_id_update=workflow_id_update,
            coze_workflow_id_delete=workflow_id_delete,
            coze_api_url=coze_api_url,
            coze_api_key=coze_api_key,
            sync_on_insert=sync_on_insert,
            sync_on_update=sync_on_update,
            sync_on_delete=sync_on_delete,
            selected_fields=selected_fields or [],
            enabled=True,
            status="ACTIVE",
            created_by=user_id
        )
        
        # 保存到数据库
        db.add(sync_config)
        await db.commit()
        await db.refresh(sync_config)
        
        # 同时更新内存存储（用于向后兼容）
        config_id = str(sync_config.uuid)
        cls._sync_configs[config_id] = {
            "config_id": config_id,
            "table_name": table_name,
            "coze_workflow_id": coze_workflow_id,
            "coze_api_url": coze_api_url,
            "coze_api_key": coze_api_key,
            "sync_on_insert": sync_on_insert,
            "sync_on_update": sync_on_update,
            "sync_on_delete": sync_on_delete,
            "selected_fields": selected_fields or [],
            "config_title": config_title or f"{table_name} - 实时同步",
            "enabled": True,
            "status": "ACTIVE",
            "created_at": datetime.now(),
            "created_by": user_id,
            "is_dynamic": all_tables[table_name].get("is_dynamic", False)
        }
        
        # 启动实时同步监听
        if sync_config.enabled:
            asyncio.create_task(cls._start_real_time_sync(config_id))
        
        logger.info(f"创建同步配置成功: {config_id}, 表: {table_name}")
        return config_id
    
    @classmethod
    async def _start_real_time_sync(cls, config_id: str):
        """启动实时数据同步 - 基于CDC机制"""
        try:
            config = cls._sync_configs.get(config_id)
            if not config or not config["enabled"]:
                return
            
            table_name = config["table_name"]
            workflow_id = config["coze_workflow_id"]
            
            logger.info(f"开始CDC实时同步监听: {table_name} -> {workflow_id}")
            
            # 注册同步配置到CDC服务
            cdc_config = {
                "table_name": table_name,
                "coze_workflow_id": workflow_id,
                "coze_api_url": config.get("coze_api_url"),
                "coze_api_key": config.get("coze_api_key"),
                "sync_on_insert": config.get("sync_on_insert", True),
                "sync_on_update": config.get("sync_on_update", True),
                "sync_on_delete": config.get("sync_on_delete", False),
                "selected_fields": config.get("selected_fields", []),
                "enabled": config["enabled"]
            }
            
            CDCService.register_sync_config(config_id, cdc_config)
            
            logger.info(f"CDC同步配置已注册: {config_id}")
                    
        except Exception as e:
            logger.error(f"CDC实时同步监听失败: {str(e)}")
    
    @classmethod
    async def _check_and_sync_new_data(cls, config_id: str):
        """检查并同步新数据 - 基于CDC机制"""
        try:
            config = cls._sync_configs.get(config_id)
            if not config:
                return
            
            # 基于CDC机制，数据变化由数据库触发器捕获
            # CDC服务会自动处理数据变化，这里不需要手动检查
            
            # 检查CDC服务中是否有待处理的数据变化
            pending_count = await CDCService.get_pending_changes_count()
            if pending_count > 0:
                logger.info(f"CDC服务中有 {pending_count} 条待处理数据变化")
            
        except Exception as e:
            logger.error(f"CDC数据检查失败: {str(e)}")
    
    @classmethod
    def _filter_data_by_fields(
        cls,
        data: List[Dict[str, Any]],
        selected_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """根据选择的字段过滤数据"""
        if not selected_fields:
            return data
        
        filtered_data = []
        for item in data:
            # 只保留选择的字段
            filtered_item = {}
            for field in selected_fields:
                if field in item:
                    filtered_item[field] = item[field]
            filtered_data.append(filtered_item)
        
        return filtered_data

    @classmethod
    async def _get_recent_changes(
        cls,
        table_name: str,
        include_insert: bool,
        include_update: bool,
        include_delete: bool
    ) -> List[Dict[str, Any]]:
        """获取最近的数据变化"""
        try:
            from app.core.database import AsyncSessionLocal
            from sqlalchemy import text
            
            async with AsyncSessionLocal() as session:
                # 获取最近5分钟内的数据变化
                # 假设表中有created_at和updated_at字段
                # 对于插入操作：created_at在最近5分钟内
                # 对于更新操作：updated_at在最近5分钟内，且updated_at > created_at
                
                conditions = []
                params = {"five_minutes_ago": datetime.now() - timedelta(minutes=5)}
                
                if include_insert:
                    conditions.append("(created_at >= :five_minutes_ago)")
                
                if include_update:
                    conditions.append("(updated_at >= :five_minutes_ago AND updated_at > created_at)")
                
                # 对于删除操作，需要额外的日志表来跟踪，这里暂时不实现
                # 因为MySQL本身不提供内置的删除记录追踪
                
                if not conditions:
                    return []
                
                where_clause = " OR ".join(conditions)
                
                # 构建查询SQL
                sql = text(f"""
                    SELECT * FROM {table_name} 
                    WHERE {where_clause}
                    ORDER BY COALESCE(updated_at, created_at) DESC
                    LIMIT 100
                """)
                
                result = await session.execute(sql, params)
                
                # 获取列名
                columns = [col[0] for col in result.cursor.description]
                
                # 转换为字典格式
                data = []
                for row in result.fetchall():
                    record_dict = {}
                    for i, column in enumerate(columns):
                        value = row[i]
                        # 处理特殊类型
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        elif isinstance(value, UUID):
                            value = str(value)
                        record_dict[column] = value
                    data.append(record_dict)
                
                logger.info(f"检测到表 {table_name} 有 {len(data)} 条数据变化")
                return data
                
        except Exception as e:
            logger.error(f"获取表 {table_name} 最近变化失败: {str(e)}")
            # 如果查询失败，返回一些模拟数据用于测试
            logger.info("返回模拟数据用于测试同步功能")
            return [
                {
                    "uuid": str(uuid4()),
                    "table_name": table_name,
                    "change_type": "INSERT",
                    "timestamp": datetime.now().isoformat(),
                    "test_data": True
                }
            ]

    @classmethod
    async def get_table_data(
        cls,
        table_name: str,
        limit: int = 10,
        offset: int = 0,
        db: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """获取指定表的真实数据"""
        
        # 动态获取所有表信息
        if db:
            all_tables = await cls.get_all_tables(db)
        else:
            # 如果没有数据库会话，使用预定义表
            all_tables = cls.PREDEFINED_TABLES
        
        if table_name not in all_tables:
            raise ValueError(f"表 {table_name} 不存在于数据库中")
        
        # 检查是否有预定义的模型
        model = all_tables[table_name].get("model")
        
        if model:
            # 使用预定义模型查询
            try:
                from app.core.database import AsyncSessionLocal
                from sqlalchemy import select
                
                async with AsyncSessionLocal() as session:
                    # 构建查询语句
                    query = select(model).limit(limit).offset(offset)
                    
                    # 执行查询
                    result = await session.execute(query)
                    records = result.scalars().all()
                    
                    # 转换为字典格式
                    data = []
                    for record in records:
                        record_dict = {}
                        for column in record.__table__.columns:
                            value = getattr(record, column.name)
                            # 处理特殊类型
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            elif isinstance(value, UUID):
                                value = str(value)
                            record_dict[column.name] = value
                        data.append(record_dict)
                    
                    return data
                    
            except Exception as e:
                logger.error(f"获取表 {table_name} 数据失败: {str(e)}")
                raise
        else:
            # 动态表，使用原始SQL查询
            try:
                from app.core.database import AsyncSessionLocal
                from sqlalchemy import text
                
                async with AsyncSessionLocal() as session:
                    # 构建查询SQL
                    sql = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
                    result = await session.execute(sql, {"limit": limit, "offset": offset})
                    
                    # 获取列名
                    columns = [col[0] for col in result.cursor.description]
                    
                    # 转换为字典格式
                    data = []
                    for row in result.fetchall():
                        record_dict = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # 处理特殊类型
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            elif isinstance(value, UUID):
                                value = str(value)
                            record_dict[column] = value
                        data.append(record_dict)
                    
                    return data
                    
            except Exception as e:
                logger.error(f"获取表 {table_name} 数据失败: {str(e)}")
                raise

    @classmethod
    async def get_table_sample_data(
        cls,
        table_name: str,
        sample_size: int = 5
    ) -> List[Dict[str, Any]]:
        """获取表的样本数据（用于测试和预览）"""
        return await cls.get_table_data(table_name, limit=sample_size)
    
    @classmethod
    async def test_coze_connection(
        cls,
        coze_api_url: str,
        coze_api_key: str
    ) -> Dict[str, Any]:
        """测试Coze API连通性"""
        try:
            # 根据Coze官方文档，使用工作空间列表API进行测试
            # 如果API密钥为空，使用简单的连通性测试
            if not coze_api_key:
                # 简单的连通性测试 - 检查API服务器是否可达
                # 使用基础API端点进行测试，而不是完整的工作流运行端点
                test_url = coze_api_url
                if not test_url.endswith('/'):
                    test_url += '/'
                test_url += 'v1/workflow/run'
                
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                logger.info(f"测试Coze API服务器连通性: {test_url}")
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # 发送一个HEAD请求测试连通性
                    response = await client.head(test_url, headers=headers)
                    
                    if response.status_code in [200, 404, 405]:
                        # 200: 服务器正常响应
                        # 404: 端点不存在但服务器可达
                        # 405: 方法不支持但服务器可达
                        return {
                            "success": True,
                            "message": "Coze API服务器连通性测试成功（未验证API密钥）",
                            "status_code": response.status_code
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"API服务器连通性测试失败: {response.status_code}",
                            "status_code": response.status_code
                        }
            
            # 如果提供了API密钥，进行完整的认证测试
            # 使用工作空间列表API进行认证测试
            # 确保URL格式正确，避免重复的路径
            api_url = coze_api_url
            if not api_url.endswith('/v1/workspaces'):
                if api_url.endswith('/'):
                    api_url += 'v1/workspaces'
                else:
                    api_url += '/v1/workspaces'
            else:
                api_url = api_url
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {coze_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"测试Coze API认证连接: {api_url}")
            
            # 调用Coze API测试连接
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Coze API连接和认证测试成功",
                        "status_code": response.status_code
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": "API密钥无效或已过期",
                        "status_code": response.status_code
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "message": "API密钥权限不足",
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API连接失败: {response.status_code} - {response.text}",
                        "status_code": response.status_code
                    }
            
        except httpx.ConnectError as e:
            return {
                "success": False,
                "message": f"无法连接到API服务器: {str(e)}"
            }
        except httpx.TimeoutException as e:
            return {
                "success": False,
                "message": f"API请求超时: {str(e)}"
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "message": f"HTTP请求错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"测试Coze API连接失败: {str(e)}")
            return {
                "success": False,
                "message": f"测试连接失败: {str(e)}"
            }


    
    @classmethod
    async def get_sync_configs(cls, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """获取所有同步配置（数据库持久化版本）"""
        
        # 如果提供了数据库会话，从数据库获取
        if db:
            try:
                # 从数据库查询所有启用的同步配置
                from sqlalchemy import select
                result = await db.execute(select(CozeSyncConfig).where(CozeSyncConfig.enabled == True))
                db_configs = result.scalars().all()
                
                # 转换为字典格式
                configs = []
                for config in db_configs:
                    config_dict = {
                        "uuid": str(config.uuid),
                        "config_title": config.config_title,
                        "table_name": config.table_name,
                        "coze_workflow_id": config.coze_workflow_id,
                        "coze_workflow_id_insert": config.coze_workflow_id_insert,
                        "coze_workflow_id_update": config.coze_workflow_id_update,
                        "coze_workflow_id_delete": config.coze_workflow_id_delete,
                        "coze_api_url": config.coze_api_url,
                        "coze_api_key": config.coze_api_key,
                        "sync_on_insert": config.sync_on_insert,
                        "sync_on_update": config.sync_on_update,
                        "sync_on_delete": config.sync_on_delete,
                        "selected_fields": config.selected_fields or [],
                        "enabled": config.enabled,
                        "status": config.status,
                        "created_at": config.created_at,
                        "updated_at": config.updated_at,
                        "created_by": config.created_by,
                        "last_sync_time": config.last_sync_time,
                        "last_error": config.last_error,
                        "total_sync_count": config.total_sync_count,
                        "success_sync_count": config.success_sync_count,
                        "failed_sync_count": config.failed_sync_count,
                        "insert_sync_count": config.insert_sync_count,
                        "update_sync_count": config.update_sync_count,
                        "delete_sync_count": config.delete_sync_count,
                        "manual_sync_count": config.manual_sync_count,
                        "auto_sync_count": config.auto_sync_count,
                        "last_manual_sync_time": config.last_manual_sync_time,
                        "last_auto_sync_time": config.last_auto_sync_time,
                        "last_sync_type": config.last_sync_type
                    }
                    configs.append(config_dict)
                    
                    # 同时更新内存存储（用于向后兼容）
                    cls._sync_configs[str(config.uuid)] = config_dict
                
                logger.info(f"从数据库获取 {len(configs)} 个同步配置")
                return configs
                
            except Exception as e:
                logger.error(f"从数据库获取同步配置失败: {str(e)}")
                # 如果数据库查询失败，回退到内存存储
        
        # 回退到内存存储
        logger.info("使用内存存储的同步配置")
        return list(cls._sync_configs.values())
    
    @classmethod
    async def update_sync_config(cls, config_id: str, updates: Dict[str, Any], db: AsyncSession = None) -> bool:
        """更新同步配置（数据库持久化版本）"""
        
        if not db:
            # 如果没有数据库会话，使用内存存储
            if config_id not in cls._sync_configs:
                return False
            
            config = cls._sync_configs[config_id]
            
            # 更新配置
            for key, value in updates.items():
                if key in ["sync_on_insert", "sync_on_update", "sync_on_delete", "enabled", "table_name", "selected_fields", "config_title", "coze_workflow_id"]:
                    config[key] = value
            
            # 如果启用了同步，重新启动监听
            if config["enabled"]:
                asyncio.create_task(cls._start_real_time_sync(config_id))
            else:
                # 如果禁用了同步，从CDC服务注销配置
                CDCService.unregister_sync_config(config_id)
            
            return True
        
        # 使用数据库更新
        try:
            from sqlalchemy import select
            result = await db.execute(select(CozeSyncConfig).where(CozeSyncConfig.uuid == config_id))
            config = result.scalar_one_or_none()
            
            if not config:
                return False
            
            # 验证数据表更新（如果更新了数据表）
            if "table_name" in updates:
                # 动态获取所有表信息
                all_tables = await cls.get_all_tables(db)
                
                # 验证表名是否存在
                if updates["table_name"] not in all_tables:
                    raise ValueError(f"表 {updates['table_name']} 不存在于数据库中")
            
            # 验证字段更新（如果更新了字段）
            if "selected_fields" in updates:
                # 获取当前表名（可能是更新后的表名）
                table_name = updates.get("table_name", config.table_name)
                
                # 动态获取表信息
                all_tables = await cls.get_all_tables(db)
                if table_name not in all_tables:
                    raise ValueError(f"表 {table_name} 不存在于数据库中")
                
                # 验证字段是否有效
                available_fields = all_tables[table_name]["fields"]
                selected_fields = updates["selected_fields"] or []
                for field in selected_fields:
                    if field not in available_fields:
                        raise ValueError(f"字段 {field} 不在表 {table_name} 中")
            
            # 更新配置
            for key, value in updates.items():
                if key == "sync_on_insert":
                    config.sync_on_insert = value
                elif key == "sync_on_update":
                    config.sync_on_update = value
                elif key == "sync_on_delete":
                    config.sync_on_delete = value
                elif key == "enabled":
                    config.enabled = value
                elif key == "status":
                    config.status = value
                elif key == "last_sync_time":
                    config.last_sync_time = value
                elif key == "last_error":
                    config.last_error = value
                elif key == "table_name":
                    config.table_name = value
                elif key == "selected_fields":
                    config.selected_fields = value
                elif key == "config_title":
                    config.config_title = value
                elif key == "coze_workflow_id":
                    config.coze_workflow_id = value
                elif key == "coze_workflow_id_insert":
                    config.coze_workflow_id_insert = value
                elif key == "coze_workflow_id_update":
                    config.coze_workflow_id_update = value
                elif key == "coze_workflow_id_delete":
                    config.coze_workflow_id_delete = value
            
            # 更新内存存储
            if config_id in cls._sync_configs:
                for key, value in updates.items():
                    if key in cls._sync_configs[config_id]:
                        cls._sync_configs[config_id][key] = value
            
            await db.commit()
            
            # 如果启用了同步，重新启动监听
            if config.enabled:
                asyncio.create_task(cls._start_real_time_sync(config_id))
            else:
                # 如果禁用了同步，从CDC服务注销配置
                CDCService.unregister_sync_config(config_id)
            
            logger.info(f"更新同步配置成功: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新同步配置失败: {config_id}, 错误: {str(e)}")
            return False
    
    @classmethod
    async def delete_sync_config(cls, config_id: str, db: AsyncSession = None) -> bool:
        """删除同步配置（数据库持久化版本）"""
        
        if not db:
            # 如果没有数据库会话，使用内存存储
            if config_id not in cls._sync_configs:
                return False
            
            # 停止同步监听
            config = cls._sync_configs[config_id]
            config["enabled"] = False
            
            # 从CDC服务注销配置
            CDCService.unregister_sync_config(config_id)
            
            # 删除配置
            del cls._sync_configs[config_id]
            return True
        
        # 使用数据库删除
        try:
            from sqlalchemy import select, delete
            
            # 先查询配置是否存在
            result = await db.execute(select(CozeSyncConfig).where(CozeSyncConfig.uuid == config_id))
            config = result.scalar_one_or_none()
            
            if not config:
                return False
            
            # 停止同步监听
            config.enabled = False
            await db.commit()
            
            # 从CDC服务注销配置
            CDCService.unregister_sync_config(config_id)
            
            # 从数据库删除
            await db.execute(delete(CozeSyncConfig).where(CozeSyncConfig.uuid == config_id))
            await db.commit()
            
            # 从内存存储删除
            if config_id in cls._sync_configs:
                del cls._sync_configs[config_id]
            
            logger.info(f"删除同步配置成功: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除同步配置失败: {config_id}, 错误: {str(e)}")
            return False
    
    @classmethod
    async def get_available_tables(cls, db: AsyncSession) -> List[CozeTableInfo]:
        """获取可上传的数据表列表（动态获取所有表）"""
        # 动态获取所有表
        all_tables = await cls.get_all_tables(db)
        
        logger.info(f"get_available_tables: 获取到 {len(all_tables)} 个表")
        logger.info(f"get_available_tables: 表名列表: {list(all_tables.keys())}")
        
        tables = []
        
        for table_name, config in all_tables.items():
            # 获取记录数量
            record_count = await cls._get_table_record_count(db, table_name, config.get("model"))
            
            logger.info(f"处理表 {table_name}: 记录数={record_count}, 是否动态={config.get('is_dynamic', False)}")
            
            # 使用字典方式创建对象，确保命名转换正确应用
            table_data = {
                "tableName": table_name,
                "displayName": config["display_name"],
                "description": config["description"],
                "recordCount": record_count,
                "lastUpdated": datetime.now()
            }
            
            table_info = CozeTableInfo(**table_data)
            tables.append(table_info)
        
        logger.info(f"get_available_tables: 最终返回 {len(tables)} 个表信息")
        return tables

    @classmethod
    async def get_table_fields(cls, table_name: str, db: AsyncSession = None) -> List[Dict[str, Any]]:
        """获取数据表的字段信息"""
        # 动态获取表信息
        if db:
            all_tables = await cls.get_all_tables(db)
            if table_name not in all_tables:
                raise ValueError(f"不支持的表名: {table_name}")
            config = all_tables[table_name]
        else:
            # 如果没有提供db会话，使用预定义表
            if table_name not in cls.PREDEFINED_TABLES:
                raise ValueError(f"不支持的表名: {table_name}")
            config = cls.PREDEFINED_TABLES[table_name]
        
        fields_info = []
        
        # 定义字段类型映射
        field_type_mapping = {
            "uuid": "UUID",
            "product_name": "字符串",
            "product_code": "字符串", 
            "unit_price": "数字",
            "current_quantity": "整数",
            "min_quantity": "整数",
            "max_quantity": "整数",
            "supplier_name": "字符串",
            "supplier_code": "字符串",
            "contact_person": "字符串",
            "phone": "字符串",
            "email": "字符串",
            "address": "字符串",
            "customer_name": "字符串",
            "customer_code": "字符串",
            "change_type": "字符串",
            "quantity_change": "整数",
            "remark": "字符串",
            "record_date": "日期",
            "created_by": "字符串",
            "created_at": "日期时间",
            "updated_at": "日期时间",
            "order_number": "字符串",
            "total_amount": "数字",
            "status": "字符串",
            "order_date": "日期",
            "category_name": "字符串",
            "category_code": "字符串",
            "parent_uuid": "UUID",
            "model_name": "字符串",
            "model_code": "字符串",
            "product_uuid": "UUID",
            "specifications": "JSON"
        }
        
        # 定义字段描述映射
        field_description_mapping = {
            "uuid": "唯一标识符",
            "product_name": "产品名称",
            "product_code": "产品编码",
            "unit_price": "单价",
            "current_quantity": "当前库存数量",
            "min_quantity": "最小库存数量",
            "max_quantity": "最大库存数量",
            "supplier_name": "供应商名称",
            "supplier_code": "供应商编码",
            "contact_person": "联系人",
            "phone": "联系电话",
            "email": "邮箱地址",
            "address": "地址",
            "customer_name": "客户名称",
            "customer_code": "客户编码",
            "change_type": "库存变更类型",
            "quantity_change": "数量变更",
            "remark": "备注",
            "record_date": "记录日期",
            "created_by": "创建人",
            "created_at": "创建时间",
            "updated_at": "更新时间",
            "order_number": "订单编号",
            "total_amount": "总金额",
            "status": "状态",
            "order_date": "订单日期",
            "category_name": "分类名称",
            "category_code": "分类编码",
            "parent_uuid": "父级分类UUID",
            "model_name": "型号名称",
            "model_code": "型号编码",
            "product_uuid": "产品UUID",
            "specifications": "规格参数"
        }
        
        for field in config["fields"]:
            field_info = {
                "fieldName": field,
                "displayName": field_description_mapping.get(field, field.replace("_", " ").title()),
                "fieldType": field_type_mapping.get(field, "字符串"),
                "isRequired": field in ["uuid", "product_name", "supplier_name", "customer_name", "order_number"],
                "description": field_description_mapping.get(field, "")
            }
            fields_info.append(field_info)
        
        return fields_info
    
    @classmethod
    async def _get_table_record_count(cls, db: AsyncSession, table_name: str, model = None) -> int:
        """获取表的记录数量"""
        try:
            from sqlalchemy import func, text
            
            if model:
                # 使用预定义模型查询
                result = await db.execute(func.count(model.uuid))
                count = result.scalar()
                return count or 0
            else:
                # 动态表，使用原始SQL查询
                sql = text(f"SELECT COUNT(*) FROM {table_name}")
                result = await db.execute(sql)
                count = result.scalar()
                return count or 0
                
        except Exception as e:
            logger.error(f"获取表 {table_name} 记录数量失败: {str(e)}")
            return 0
    
    @classmethod
    def start_upload_task(
        cls,
        table_name: str,
        coze_workflow_id: str,
        coze_api_url: str = None,
        coze_api_key: str = None,
        filters: Optional[List[CozeUploadFilter]] = None,
        user_id: UUID = None
    ) -> str:
        """启动数据上传任务"""
        logger.warning(f"=== DEBUG: start_upload_task被调用，表名: {table_name}, 工作流ID: {coze_workflow_id} ===")
        
        # 使用PREDEFINED_TABLES替代AVAILABLE_TABLES
        if table_name not in cls.PREDEFINED_TABLES:
            logger.warning(f"=== DEBUG: 表名 {table_name} 不在预定义表中 ===")
            raise ValueError(f"不支持的表名: {table_name}")
        
        logger.warning(f"=== DEBUG: 表名 {table_name} 在预定义表中 ===")
        
        # 生成上传任务ID
        upload_id = str(uuid4())
        logger.warning(f"=== DEBUG: 生成上传任务ID: {upload_id} ===")
        
        # 创建上传任务状态
        status_data = {
            "uploadId": upload_id,
            "tableName": table_name,
            "status": "PENDING",
            "progress": 0,
            "totalRecords": 0,
            "processedRecords": 0,
            "failedRecords": 0,
            "startTime": datetime.now()
        }
        
        task_status = CozeUploadStatus(**status_data)
        
        # 存储任务状态
        cls._upload_tasks[upload_id] = {
            "status": task_status,
            "user_id": user_id,
            "coze_workflow_id": coze_workflow_id,
            "coze_api_url": coze_api_url,
            "coze_api_key": coze_api_key,
            "filters": filters
        }
        
        logger.warning(f"=== DEBUG: 任务状态已存储，准备启动后台任务 ===")
        
        # 启动后台任务
        asyncio.create_task(cls._process_upload_task(upload_id))
        logger.warning(f"=== DEBUG: 后台任务已启动 ===")
        
        return upload_id

    @classmethod
    async def trigger_manual_sync(cls, config_uuid: UUID, db_session) -> Dict[str, Any]:
        """手动触发同步配置的数据同步"""
        try:
            logger.warning(f"=== DEBUG: 开始手动同步，配置UUID: {config_uuid} ===")
            
            # 获取同步配置
            sync_config = None
            config_id_str = str(config_uuid)
            
            # 首先检查内存配置
            if config_id_str in cls._sync_configs:
                sync_config = cls._sync_configs[config_id_str]
                logger.warning(f"=== DEBUG: 从内存配置中找到同步配置 ===")
            
            if not sync_config:
                # 从数据库加载配置
                logger.warning(f"=== DEBUG: 从数据库加载同步配置 ===")
                db_config = await db_session.get(CozeSyncConfig, config_uuid)
                if db_config:
                    # 转换为字典格式（与内存配置保持一致）
                    sync_config = {
                        "config_id": str(db_config.uuid),
                        "table_name": db_config.table_name,
                        "coze_workflow_id": db_config.coze_workflow_id,
                        "coze_workflow_id_insert": db_config.coze_workflow_id_insert,
                        "coze_workflow_id_update": db_config.coze_workflow_id_update,
                        "coze_workflow_id_delete": db_config.coze_workflow_id_delete,
                        "coze_api_url": db_config.coze_api_url,
                        "coze_api_key": db_config.coze_api_key,
                        "sync_on_insert": db_config.sync_on_insert,
                        "sync_on_update": db_config.sync_on_update,
                        "sync_on_delete": db_config.sync_on_delete,
                        "selected_fields": db_config.selected_fields or [],
                        "config_title": db_config.config_title,
                        "enabled": db_config.enabled,
                        "status": db_config.status,
                        "created_at": db_config.created_at,
                        "created_by": db_config.created_by,
                        "is_dynamic": False  # 默认值
                    }
                    # 添加到内存配置中
                    cls._sync_configs[config_id_str] = sync_config
                    logger.warning(f"=== DEBUG: 从数据库加载同步配置成功 ===")
            
            if not sync_config:
                logger.warning(f"=== DEBUG: 同步配置不存在 ===")
                raise ValueError(f"同步配置不存在: {config_uuid}")
            
            if not sync_config.get("enabled", False):
                logger.warning(f"=== DEBUG: 同步配置未启用 ===")
                raise ValueError(f"同步配置未启用: {config_uuid}")
            
            # 检查是否有可用的工作流ID
            workflow_id = sync_config.get("coze_workflow_id")
            workflow_id_insert = sync_config.get("coze_workflow_id_insert")
            workflow_id_update = sync_config.get("coze_workflow_id_update")
            workflow_id_delete = sync_config.get("coze_workflow_id_delete")
            
            # 确定使用哪个工作流ID（优先使用新增操作的工作流ID）
            effective_workflow_id = workflow_id_insert or workflow_id_update or workflow_id_delete or workflow_id
            
            if not effective_workflow_id:
                logger.warning(f"=== DEBUG: 没有可用的工作流ID ===")
                raise ValueError("同步配置中没有设置有效的工作流ID")
            
            logger.warning(f"=== DEBUG: 同步配置信息 - 表名: {sync_config['table_name']}, 工作流ID: {effective_workflow_id}, 启用状态: {sync_config['enabled']} ===")
            logger.warning(f"=== DEBUG: 工作流ID详情 - 新增: {workflow_id_insert}, 更新: {workflow_id_update}, 删除: {workflow_id_delete}, 通用: {workflow_id} ===")
            
            # 获取表数据
            logger.warning(f"=== DEBUG: 开始获取表数据 ===")
            table_data = await cls._get_table_data(sync_config["table_name"])
            logger.warning(f"=== DEBUG: 获取到表数据条数: {len(table_data) if table_data else 0} ===")
            
            if not table_data:
                logger.warning(f"=== DEBUG: 表 {sync_config['table_name']} 没有数据需要同步 ===")
                return {
                    "success": True,
                    "message": "没有数据需要同步",
                    "records_synced": 0
                }
            
            # 启动上传任务
            logger.warning(f"=== DEBUG: 开始启动上传任务 ===")
            upload_id = cls.start_upload_task(
                table_name=sync_config["table_name"],
                coze_workflow_id=effective_workflow_id,
                coze_api_url=sync_config["coze_api_url"],
                coze_api_key=sync_config["coze_api_key"]
            )
            logger.warning(f"=== DEBUG: 上传任务ID: {upload_id} ===")
            
            # 等待任务完成
            max_wait_time = 300  # 5分钟超时
            wait_interval = 2  # 每2秒检查一次
            
            for _ in range(max_wait_time // wait_interval):
                await asyncio.sleep(wait_interval)
                
                task_info = cls._upload_tasks.get(upload_id)
                if not task_info:
                    break
                    
                status = task_info["status"]
                if status.status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    break
            
            # 获取最终状态
            task_info = cls._upload_tasks.get(upload_id)
            if task_info:
                status = task_info["status"]
                
                if status.status == "COMPLETED":
                    success_records = status.processedRecords - status.failedRecords
                    
                    # 更新同步统计信息
                    await cls._update_sync_statistics(config_uuid, db_session, True, success_records, "MANUAL")
                    
                    return {
                        "success": True,
                        "message": f"同步完成，成功同步 {success_records} 条记录",
                        "records_synced": success_records,
                        "upload_id": upload_id
                    }
                else:
                    # 更新同步统计信息（失败）
                    await cls._update_sync_statistics(config_uuid, db_session, False, 0, "MANUAL")
                    
                    return {
                        "success": False,
                        "message": f"同步失败: {status.status}",
                        "records_synced": 0,
                        "upload_id": upload_id
                    }
            else:
                # 更新同步统计信息（失败）
                await cls._update_sync_statistics(config_uuid, db_session, False, 0, "MANUAL")
                
                return {
                    "success": False,
                    "message": "同步任务不存在",
                    "records_synced": 0
                }
                
        except Exception as e:
            logger.error(f"手动同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"同步失败: {str(e)}",
                "records_synced": 0
            }
    
    @classmethod
    async def _process_upload_task(cls, upload_id: str):
        """处理数据上传任务"""
        try:
            task_info = cls._upload_tasks.get(upload_id)
            if not task_info:
                logger.error(f"上传任务不存在: {upload_id}")
                return
            
            status = task_info["status"]
            table_name = status.tableName
            coze_workflow_id = task_info["coze_workflow_id"]
            filters = task_info["filters"]
            
            # 使用logger.warning确保调试信息被输出
            logger.warning(f"=== DEBUG: 开始处理上传任务 ===")
            logger.warning(f"任务ID: {upload_id}")
            logger.warning(f"表名: {table_name}")
            logger.warning(f"工作流ID: {coze_workflow_id}")
            
            logger.warning(f"开始处理上传任务: {upload_id}, 表名: {table_name}, 工作流ID: {coze_workflow_id}")
            
            # 更新任务状态为处理中
            status.status = "PROCESSING"
            
            # 获取数据
            logger.warning(f"=== DEBUG: 开始获取表数据 ===")
            logger.warning(f"开始获取表数据: {table_name}")
            data = await cls._get_table_data(table_name, filters)
            status.totalRecords = len(data)
            logger.warning(f"=== DEBUG: 获取到表数据条数: {status.totalRecords} ===")
            logger.warning(f"获取到表数据条数: {status.totalRecords}")
            
            if status.totalRecords == 0:
                logger.warning(f"=== DEBUG: 表 {table_name} 没有数据需要同步 ===")
                logger.warning(f"表 {table_name} 没有数据需要同步")
                status.status = "COMPLETED"
                status.progress = 100
                status.endTime = datetime.now()
                return
            
            # 分批上传数据到Coze
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                
                # 上传批次数据，使用配置中保存的API密钥和URL
                logger.warning(f"=== DEBUG: _process_upload_task调用_upload_batch_to_coze ===")
                logger.warning(f"=== DEBUG: task_info中的API URL: {task_info.get('coze_api_url')} ===")
                logger.warning(f"=== DEBUG: task_info中的API密钥长度: {len(task_info.get('coze_api_key')) if task_info.get('coze_api_key') else 0} ===")
                
                success_count = await cls._upload_batch_to_coze(
                    coze_workflow_id, 
                    batch_data,
                    task_info.get("coze_api_url"),
                    task_info.get("coze_api_key"),
                    table_name
                )
                
                status.processedRecords += len(batch_data)
                status.failedRecords += (len(batch_data) - success_count)
                status.progress = int((status.processedRecords / status.totalRecords) * 100)
                
                # 检查是否取消
                if upload_id not in cls._upload_tasks:
                    logger.info(f"上传任务被取消: {upload_id}")
                    return
            
            # 完成任务
            status.status = "COMPLETED"
            status.progress = 100
            status.endTime = datetime.now()
            
            logger.info(f"上传任务完成: {upload_id}, 成功: {status.processedRecords - status.failedRecords}, 失败: {status.failedRecords}")
            
        except Exception as e:
            logger.error(f"上传任务处理失败: {upload_id}, 错误: {str(e)}")
            
            if upload_id in cls._upload_tasks:
                status = cls._upload_tasks[upload_id]["status"]
                status.status = "FAILED"
                status.errorMessage = str(e)
                status.endTime = datetime.now()
    
    @classmethod
    async def _get_table_data(cls, table_name: str, filters: Optional[List[CozeUploadFilter]] = None) -> List[Dict[str, Any]]:
        """获取表数据"""
        logger.warning(f"开始获取表数据，表名: {table_name}")
        
        # 使用PREDEFINED_TABLES替代AVAILABLE_TABLES
        if table_name not in cls.PREDEFINED_TABLES:
            logger.warning(f"表名 {table_name} 不在预定义表中，可用表: {list(cls.PREDEFINED_TABLES.keys())}")
            return []
        
        config = cls.PREDEFINED_TABLES[table_name]
        model = config["model"]
        fields = config["fields"]
        
        logger.warning(f"找到表配置，模型: {model}, 字段列表: {fields}")
        
        try:
            async for session in get_db():
                logger.warning(f"数据库会话已建立，开始构建查询")
                
                # 构建查询 - 使用SQLAlchemy 2.0的正确语法
                from sqlalchemy import select
                query = select(model)
                
                # 应用筛选条件
                if filters:
                    logger.warning(f"应用筛选条件: {filters}")
                    for filter_cond in filters:
                        field = getattr(model, filter_cond.field, None)
                        if field:
                            if filter_cond.operator == "=":
                                query = query.where(field == filter_cond.value)
                            elif filter_cond.operator == ">":
                                query = query.where(field > filter_cond.value)
                            elif filter_cond.operator == "<":
                                query = query.where(field < filter_cond.value)
                            elif filter_cond.operator == ">=":
                                query = query.where(field >= filter_cond.value)
                            elif filter_cond.operator == "<=":
                                query = query.where(field <= filter_cond.value)
                            elif filter_cond.operator == "LIKE":
                                query = query.where(field.like(f"%{filter_cond.value}%"))
                            elif filter_cond.operator == "IN":
                                if isinstance(filter_cond.value, list):
                                    query = query.where(field.in_(filter_cond.value))
                
                # 获取数据
                logger.warning(f"执行SQL查询")
                result = await session.execute(query)
                records = result.scalars().all()
                logger.warning(f"查询执行完成，获取到 {len(records)} 条原始记录")
                
                # 转换为字典格式
                data = []
                logger.warning(f"开始转换记录到字典格式，字段列表: {fields}")
                
                for i, record in enumerate(records):
                    record_dict = {}
                    for field in fields:
                        # 将蛇形命名字段转换为大驼峰命名，以匹配API响应格式
                        # 例如：customer_name -> customerName
                        camel_field = field
                        if '_' in field:
                            parts = field.split('_')
                            camel_field = parts[0] + ''.join(part.capitalize() for part in parts[1:])
                        
                        value = getattr(record, field, None)
                        if isinstance(value, UUID):
                            value = str(value)
                        elif isinstance(value, datetime):
                            value = value.isoformat()
                        record_dict[camel_field] = value
                    
                    if i < 3:  # 只记录前3条数据的详细信息，避免日志过多
                        logger.warning(f"第{i+1}条记录数据: {record_dict}")
                    data.append(record_dict)
                
                logger.warning(f"数据转换完成，转换后的数据条数: {len(data)}")
                
                return data
            
        except Exception as e:
            logger.error(f"获取表数据失败: {table_name}, 错误: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return []
    
    @classmethod
    async def _upload_batch_to_coze(cls, workflow_id: str, data: List[Dict[str, Any]], coze_api_url: str = None, coze_api_key: str = None, table_name: str = None) -> int:
        """上传批次数据到Coze"""
        try:
            # 强制输出调试信息到标准输出
            import sys
            print(f"=== DEBUG _upload_batch_to_coze开始 ===", file=sys.stderr)
            print(f"=== 传入参数: workflow_id={workflow_id}, coze_api_url={coze_api_url}, coze_api_key长度={len(coze_api_key) if coze_api_key else 0} ===", file=sys.stderr)
            
            # 使用配置中保存的API密钥和URL，如果没有提供则使用全局配置
            if coze_api_url and coze_api_key:
                # 合成完整的workflow run API地址
                if not coze_api_url.endswith('/v1/workflow/run'):
                    if coze_api_url.endswith('/'):
                        api_url = coze_api_url + 'v1/workflow/run'
                    else:
                        api_url = coze_api_url + '/v1/workflow/run'
                else:
                    api_url = coze_api_url
                api_key = coze_api_key
                print(f"=== DEBUG: 使用传入的API配置 - URL: {api_url}, 密钥长度: {len(api_key) if api_key else 0} ===", file=sys.stderr)
                logger.warning(f"=== DEBUG: 使用传入的API配置 - URL: {api_url}, 密钥长度: {len(api_key) if api_key else 0} ===")
            else:
                api_config = cls._get_coze_api_config()
                # 合成完整的workflow run API地址
                base_url = api_config.base_url
                if not base_url.endswith('/v1/workflow/run'):
                    if base_url.endswith('/'):
                        api_url = base_url + 'v1/workflow/run'
                    else:
                        api_url = base_url + '/v1/workflow/run'
                else:
                    api_url = base_url
                api_key = api_config.api_key
                print(f"=== DEBUG: 使用全局API配置 - URL: {api_url}, 密钥长度: {len(api_key) if api_key else 0} ===", file=sys.stderr)
                logger.warning(f"=== DEBUG: 使用全局API配置 - URL: {api_url}, 密钥长度: {len(api_key) if api_key else 0} ===")
            
            async with httpx.AsyncClient(timeout=30) as client:
                success_count = 0
                error_count = 0
                
                # 逐条传输数据，每条数据间隔1秒（与前端测试传输保持一致）
                for i, record in enumerate(data):
                    # 构建单条数据的parameters
                    parameters = {}
                    
                    # 根据表名动态处理字段映射
                    if table_name == 'customers':
                        # 客户表的特定字段映射
                        for field_name, field_value in record.items():
                            # 处理datetime对象的序列化
                            if hasattr(field_value, 'isoformat'):
                                field_value = field_value.isoformat()
                            
                            # 客户表字段映射到Coze工作流参数
                            if field_name == 'uuid':
                                parameters['user_id'] = field_value
                            elif field_name == 'customerName':
                                parameters['customer_name'] = field_value
                            elif field_name == 'customerCode':
                                parameters['customer_code'] = field_value
                            elif field_name == 'contactPerson':
                                parameters['contact_person'] = field_value
                            elif field_name == 'phone':
                                parameters['phone'] = field_value
                            elif field_name == 'email':
                                parameters['email'] = field_value
                            elif field_name == 'address':
                                parameters['address'] = field_value
                            elif field_name == 'isActive':
                                parameters['is_active'] = field_value
                            elif field_name == 'createdAt':
                                parameters['created_at'] = field_value
                            elif field_name == 'updatedAt':
                                parameters['updated_at'] = field_value
                            elif field_name == 'deletedAt':
                                parameters['deleted_at'] = field_value
                            else:
                                parameters[field_name] = field_value
                    else:
                        # 其他表的通用字段映射
                        for field_name, field_value in record.items():
                            # 处理datetime对象的序列化
                            if hasattr(field_value, 'isoformat'):
                                field_value = field_value.isoformat()
                            
                            # 通用规则：将uuid字段映射为user_id，避免与Coze数据库中的uuid字段冲突
                            if field_name == 'uuid':
                                parameters['user_id'] = field_value
                            else:
                                # 直接使用数据库的蛇形命名字段，符合Coze工作流参数格式
                                parameters[field_name] = field_value
                    
                    # 构建请求数据（与前端测试传输保持一致）
                    payload = {
                        "workflow_id": workflow_id,
                        "parameters": parameters
                    }
                    
                    # 添加认证头
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    logger.info(f"发送第{i+1}条数据到Coze API: {payload}")
                    
                    try:
                        # 使用正确的API端点：直接使用配置的完整URL
                        logger.warning(f"=== DEBUG: 发送第{i+1}条数据到Coze API ===")
                        logger.warning(f"API URL: {api_url}")
                        logger.warning(f"Headers: {headers}")
                        logger.warning(f"Payload: {payload}")
                        
                        response = await client.post(
                            api_url,
                            json=payload,
                            headers=headers
                        )
                        
                        logger.warning(f"=== DEBUG: 第{i+1}条数据响应状态码: {response.status_code} ===")
                        logger.warning(f"响应头: {dict(response.headers)}")
                        
                        response_text = response.text
                        logger.warning(f"响应内容: {response_text}")
                        
                        # 只有状态码200才表示成功，其他状态码都表示失败
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"第{i+1}条数据传输成功: {result}")
                            success_count += 1
                        else:
                            error_text = response.text
                            logger.error(f"第{i+1}条数据传输失败: 状态码={response.status_code}, 错误信息={error_text}")
                            error_count += 1
                            
                    except Exception as e:
                        logger.error(f"第{i+1}条数据传输异常: {str(e)}")
                        error_count += 1
                    
                    # 如果不是最后一条数据，等待1秒后再发送下一条（与前端测试传输保持一致）
                    if i < len(data) - 1:
                        await asyncio.sleep(1)
                
                logger.info(f"批次数据传输完成: 成功 {success_count} 条，失败 {error_count} 条")
                return success_count
                    
        except Exception as e:
            logger.error(f"上传数据到Coze失败: {str(e)}")
            return 0
    
    @classmethod
    def _get_coze_api_config(cls) -> CozeApiConfig:
        """获取Coze API配置"""
        from app.core.config import settings
        
        # 从配置设置中读取配置
        api_key = settings.COZE_API_KEY
        base_url = settings.COZE_API_BASE_URL
        timeout = settings.COZE_API_TIMEOUT
        
        # 检查是否配置了实际的API密钥
        if api_key == "your_coze_api_key_here":
            logger.warning("使用默认的Coze API密钥，请配置COZE_API_KEY环境变量")
        
        return CozeApiConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
    
    @classmethod
    def get_upload_status(cls, upload_id: str) -> Optional[CozeUploadStatus]:
        """获取上传任务状态"""
        task_info = cls._upload_tasks.get(upload_id)
        if task_info:
            return task_info["status"]
        return None
    
    @classmethod
    def get_upload_history(cls, page: int = 1, size: int = 20) -> List[CozeUploadHistory]:
        """获取上传历史记录"""
        # 这里可以从数据库查询实际的历史记录
        # 目前返回模拟数据
        
        history = []
        for upload_id, task_info in cls._upload_tasks.items():
            status = task_info["status"]
            
            # 使用字典方式创建对象，确保命名转换正确应用
            history_data = {
                "upload_id": upload_id,
                "table_name": status.tableName,
                "coze_workflow_id": task_info["coze_workflow_id"],
                "status": status.status,
                "total_records": status.totalRecords,
                "success_records": status.processedRecords - status.failedRecords,
                "failed_records": status.failedRecords,
                "start_time": status.startTime,
                "end_time": status.endTime,
                "operator_name": "系统用户"  # 由于移除了用户认证，使用默认名称
            }
            
            history_item = CozeUploadHistory(**history_data)
            history.append(history_item)
        
        # 分页处理
        start_index = (page - 1) * size
        end_index = start_index + size
        
        return history[start_index:end_index]
    
    @classmethod
    def cancel_upload(cls, upload_id: str) -> bool:
        """取消上传任务"""
        task_info = cls._upload_tasks.get(upload_id)
        if not task_info:
            return False
        
        # 更新任务状态为取消
        status = task_info["status"]
        if status.status in ["PENDING", "PROCESSING"]:
            status.status = "CANCELLED"
            status.endTime = datetime.now()
            
            # 从任务列表中移除
            del cls._upload_tasks[upload_id]
            
            return True
        
        return False
    
    @classmethod
    async def _update_sync_statistics(cls, config_uuid: str, db: AsyncSession, is_success: bool, success_records: int = 0, sync_type: str = "MANUAL") -> None:
        """更新同步统计信息
        
        Args:
            config_uuid: 同步配置UUID
            db: 数据库会话
            is_success: 是否成功
            success_records: 成功同步的记录数
            sync_type: 同步类型 (MANUAL/AUTO)
        """
        try:
            # 查询同步配置
            config = await db.get(CozeSyncConfig, config_uuid)
            if not config:
                logger.warning(f"同步配置不存在: {config_uuid}")
                return
            
            # 更新统计信息
            config.total_sync_count += 1
            
            if is_success:
                config.success_sync_count += 1
                config.failed_sync_count = config.failed_sync_count  # 保持不变
            else:
                config.success_sync_count = config.success_sync_count  # 保持不变
                config.failed_sync_count += 1
            
            # 根据同步类型更新手动/自动同步统计
            if sync_type == "MANUAL":
                config.manual_sync_count += 1
                config.last_manual_sync_time = datetime.now()
            elif sync_type == "AUTO":
                config.auto_sync_count += 1
                config.last_auto_sync_time = datetime.now()
            
            config.last_sync_type = sync_type
            config.last_sync_time = datetime.now()
            
            # 保存到数据库
            await db.commit()
            
            logger.info(f"更新同步统计信息 - 配置: {config.config_title}, 类型: {sync_type}, 成功: {is_success}, 成功记录数: {success_records}")
            
        except Exception as e:
            logger.error(f"更新同步统计信息失败: {str(e)}")
            await db.rollback()