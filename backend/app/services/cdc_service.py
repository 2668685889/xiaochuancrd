"""CDC (Change Data Capture) 服务"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from app.core.database import get_db
from app.models.data_change_log import DataChangeLog

logger = logging.getLogger(__name__)


class CDCService:
    """CDC服务类"""
    
    # 存储活跃的同步配置
    _active_sync_configs: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_sync_config(cls, config_id: str, config: Dict[str, Any]):
        """注册同步配置"""
        cls._active_sync_configs[config_id] = config
        logger.info(f"注册同步配置: {config_id}, 表: {config.get('table_name')}")
    
    @classmethod
    def unregister_sync_config(cls, config_id: str):
        """注销同步配置"""
        if config_id in cls._active_sync_configs:
            del cls._active_sync_configs[config_id]
            logger.info(f"注销同步配置: {config_id}")
    
    @classmethod
    async def start_cdc_monitoring(cls):
        """启动CDC监控"""
        logger.info("启动CDC数据变化监控")
        
        while True:
            try:
                # 检查是否有活跃的同步配置
                if not cls._active_sync_configs:
                    await asyncio.sleep(10)  # 没有配置时等待10秒
                    continue
                
                # 处理未处理的数据变化
                await cls._process_pending_changes()
                
                # 等待一段时间后再次检查
                await asyncio.sleep(5)  # 5秒检查一次
                
            except Exception as e:
                logger.error(f"CDC监控异常: {str(e)}")
                await asyncio.sleep(10)  # 异常时等待10秒
    
    @classmethod
    async def _process_pending_changes(cls):
        """处理待处理的数据变化"""
        try:
            # 使用异步数据库会话
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                # 查询未处理的数据变化日志
                query = session.query(DataChangeLog).filter(
                    DataChangeLog.processed == 0
                ).order_by(DataChangeLog.created_at.asc()).limit(100)
                
                result = await session.execute(query)
                pending_changes = result.scalars().all()
                
                if not pending_changes:
                    return
                
                logger.info(f"发现 {len(pending_changes)} 条待处理数据变化")
                
                # 按表名分组处理
                changes_by_table = {}
                for change in pending_changes:
                    if change.table_name not in changes_by_table:
                        changes_by_table[change.table_name] = []
                    changes_by_table[change.table_name].append(change)
                
                # 处理每个表的变化
                for table_name, changes in changes_by_table.items():
                    await cls._process_table_changes(table_name, changes, session)
                
                # 提交事务
                await session.commit()
                
        except Exception as e:
            logger.error(f"处理待处理数据变化失败: {str(e)}")
    
    @classmethod
    async def _process_table_changes(cls, table_name: str, changes: List[DataChangeLog], session):
        """处理指定表的数据变化"""
        try:
            # 查找相关的同步配置
            related_configs = []
            for config_id, config in cls._active_sync_configs.items():
                if config.get("table_name") == table_name and config.get("enabled", False):
                    related_configs.append((config_id, config))
            
            if not related_configs:
                logger.info(f"表 {table_name} 没有启用的同步配置，跳过处理")
                return
            
            logger.info(f"处理表 {table_name} 的 {len(changes)} 条数据变化，关联 {len(related_configs)} 个同步配置")
            
            # 为每个同步配置处理数据变化
            for config_id, config in related_configs:
                await cls._process_changes_for_config(config_id, config, changes, session)
                
        except Exception as e:
            logger.error(f"处理表 {table_name} 数据变化失败: {str(e)}")
    
    @classmethod
    async def _process_changes_for_config(
        cls, 
        config_id: str, 
        config: Dict[str, Any], 
        changes: List[DataChangeLog], 
        session
    ):
        """为指定配置处理数据变化"""
        try:
            # 过滤符合配置条件的变化
            filtered_changes = []
            
            for change in changes:
                # 检查操作类型是否符合配置
                if change.operation_type == "INSERT" and not config.get("sync_on_insert", True):
                    continue
                if change.operation_type == "UPDATE" and not config.get("sync_on_update", True):
                    continue
                if change.operation_type == "DELETE" and not config.get("sync_on_delete", False):
                    continue
                
                filtered_changes.append(change)
            
            if not filtered_changes:
                return
            
            logger.info(f"配置 {config_id} 需要处理 {len(filtered_changes)} 条数据变化")
            
            # 准备同步数据
            sync_data = []
            for change in filtered_changes:
                # 解析变化数据
                change_data = change.change_data or {}
                
                # 添加操作类型标记
                sync_record = {
                    "operation_type": change.operation_type,
                    "record_uuid": change.record_uuid,
                    "change_timestamp": change.created_at.isoformat() if change.created_at else datetime.now().isoformat()
                }
                
                # 如果配置了字段筛选，只保留选择的字段
                selected_fields = config.get("selected_fields", [])
                if selected_fields:
                    for field in selected_fields:
                        if field in change_data:
                            sync_record[field] = change_data[field]
                else:
                    # 保留所有字段
                    sync_record.update(change_data)
                
                sync_data.append(sync_record)
            
            # 调用Coze服务进行同步
            from app.services.coze_service import CozeService
            
            # 根据操作类型选择合适的工作流ID
            workflow_id = None
            
            # 检查所有变化记录的操作类型，确定使用哪个工作流ID
            operation_types = set(change.operation_type for change in filtered_changes)
            
            # 优先使用特定操作类型的工作流ID
            if "INSERT" in operation_types and config.get("coze_workflow_id_insert"):
                workflow_id = config.get("coze_workflow_id_insert")
            elif "UPDATE" in operation_types and config.get("coze_workflow_id_update"):
                workflow_id = config.get("coze_workflow_id_update")
            elif "DELETE" in operation_types and config.get("coze_workflow_id_delete"):
                workflow_id = config.get("coze_workflow_id_delete")
            else:
                # 回退到通用工作流ID
                workflow_id = config.get("coze_workflow_id")
            
            if not workflow_id:
                logger.error(f"配置 {config_id} 缺少必要的workflow_id信息")
                return
            
            # 使用同步配置中保存的API地址和密钥
            coze_api_url = config.get("coze_api_url")
            coze_api_key = config.get("coze_api_key")
            
            success_count = await CozeService._upload_batch_to_coze(
                workflow_id, sync_data, coze_api_url, coze_api_key, config.get("table_name")
            )
            
            logger.info(f"配置 {config_id} 同步完成，成功: {success_count}/{len(sync_data)}")
            
            # 标记已处理的变化
            for change in filtered_changes:
                change.processed = 1
                change.processed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"为配置 {config_id} 处理数据变化失败: {str(e)}")
    
    @classmethod
    async def get_pending_changes_count(cls) -> int:
        """获取待处理的数据变化数量"""
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                query = session.query(DataChangeLog).filter(
                    DataChangeLog.processed == 0
                )
                result = await session.execute(query)
                return len(result.scalars().all())
        except Exception as e:
            logger.error(f"获取待处理变化数量失败: {str(e)}")
            return 0
    
    @classmethod
    async def cleanup_processed_changes(cls, days: int = 7):
        """清理已处理的数据变化记录"""
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = session.query(DataChangeLog).filter(
                    DataChangeLog.processed == 1,
                    DataChangeLog.processed_at < cutoff_date
                )
                
                result = await session.execute(query)
                changes_to_delete = result.scalars().all()
                
                if changes_to_delete:
                    # 删除已处理的记录
                    for change in changes_to_delete:
                        await session.delete(change)
                    
                    await session.commit()
                    logger.info(f"清理了 {len(changes_to_delete)} 条已处理的数据变化记录")
        except Exception as e:
            logger.error(f"清理已处理数据变化记录失败: {str(e)}")


# 启动CDC监控的辅助函数
async def start_cdc_service():
    """启动CDC服务"""
    cdc_task = asyncio.create_task(CDCService.start_cdc_monitoring())
    return cdc_task