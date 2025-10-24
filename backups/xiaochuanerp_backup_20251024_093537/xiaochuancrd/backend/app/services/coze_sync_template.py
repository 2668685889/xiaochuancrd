"""
通用Coze同步模板服务

提供通用的同步模板，支持不同表单的配置化同步
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime

from app.services.coze_service import CozeService
from app.models.coze_sync_config import CozeSyncConfig
from app.core.database import get_db

logger = logging.getLogger(__name__)


class CozeSyncTemplate:
    """通用Coze同步模板类"""
    
    @classmethod
    async def create_sync_template(
        cls,
        table_name: str,
        config_title: str,
        coze_workflow_id: str,
        coze_api_url: str = "https://api.coze.cn",
        coze_api_key: Optional[str] = None,
        selected_fields: Optional[List[str]] = None,
        sync_on_insert: bool = True,
        sync_on_update: bool = True,
        sync_on_delete: bool = False,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        创建通用同步模板
        
        Args:
            table_name: 数据表名
            config_title: 配置标题
            coze_workflow_id: Coze工作流ID
            coze_api_url: Coze API地址
            coze_api_key: Coze API密钥
            selected_fields: 选择的字段列表
            sync_on_insert: 是否同步插入操作
            sync_on_update: 是否同步更新操作
            sync_on_delete: 是否同步删除操作
            created_by: 创建者UUID
            
        Returns:
            创建的同步配置信息
        """
        try:
            # 验证表是否存在
            all_tables = await CozeService.get_all_tables()
            if table_name not in all_tables:
                raise ValueError(f"表 {table_name} 不存在")
            
            # 获取表的字段信息
            table_info = all_tables[table_name]
            table_fields = table_info.get("fields", [])
            
            # 如果没有指定字段，使用所有字段
            if not selected_fields:
                selected_fields = [field["name"] for field in table_fields]
            
            # 验证字段是否存在
            for field in selected_fields:
                if field not in [f["name"] for f in table_fields]:
                    raise ValueError(f"字段 {field} 在表 {table_name} 中不存在")
            
            # 创建同步配置
            sync_config = CozeSyncConfig(
                config_title=config_title,
                table_name=table_name,
                coze_workflow_id=coze_workflow_id,
                coze_api_url=coze_api_url,
                coze_api_key=coze_api_key,
                sync_on_insert=sync_on_insert,
                sync_on_update=sync_on_update,
                sync_on_delete=sync_on_delete,
                selected_fields=selected_fields,
                created_by=created_by
            )
            
            # 保存到数据库
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                session.add(sync_config)
                await session.commit()
                await session.refresh(sync_config)
            
            # 启动实时同步（如果启用）
            if sync_on_insert or sync_on_update or sync_on_delete:
                await CozeService._start_real_time_sync(sync_config)
            
            return {
                "success": True,
                "message": "同步模板创建成功",
                "config": {
                    "uuid": sync_config.uuid,
                    "config_title": sync_config.config_title,
                    "table_name": sync_config.table_name,
                    "coze_workflow_id": sync_config.coze_workflow_id,
                    "selected_fields": sync_config.selected_fields,
                    "enabled": sync_config.enabled
                }
            }
            
        except Exception as e:
            logger.error(f"创建同步模板失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建同步模板失败: {str(e)}"
            }
    
    @classmethod
    async def manual_sync_all_records(
        cls,
        config_uuid: UUID,
        batch_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        手动同步所有记录到Coze
        
        Args:
            config_uuid: 同步配置UUID
            batch_size: 批次大小
            filters: 数据过滤条件
            
        Returns:
            同步结果
        """
        try:
            # 获取同步配置
            sync_config = None
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                db_config = await session.get(CozeSyncConfig, config_uuid)
                if db_config:
                    sync_config = {
                        "config_id": str(db_config.uuid),
                        "table_name": db_config.table_name,
                        "coze_workflow_id": db_config.coze_workflow_id,
                        "coze_api_url": db_config.coze_api_url,
                        "coze_api_key": db_config.coze_api_key,
                        "selected_fields": db_config.selected_fields or [],
                        "enabled": db_config.enabled
                    }
            
            if not sync_config:
                raise ValueError(f"同步配置不存在: {config_uuid}")
            
            if not sync_config["enabled"]:
                raise ValueError(f"同步配置未启用: {config_uuid}")
            
            logger.info(f"开始手动同步表 {sync_config['table_name']} 的所有记录")
            
            # 获取所有数据
            table_data = await CozeService.get_table_data(
                sync_config["table_name"],
                limit=0,  # 0表示获取所有数据
                filters=filters
            )
            
            if not table_data:
                return {
                    "success": True,
                    "message": "没有数据需要同步",
                    "records_synced": 0
                }
            
            # 如果指定了字段选择，过滤数据
            if sync_config["selected_fields"]:
                filtered_data = []
                for record in table_data:
                    filtered_record = {}
                    for field in sync_config["selected_fields"]:
                        if field in record:
                            filtered_record[field] = record[field]
                    filtered_data.append(filtered_record)
                table_data = filtered_data
            
            total_records = len(table_data)
            logger.info(f"需要同步 {total_records} 条记录")
            
            # 分批上传
            success_count = 0
            for i in range(0, total_records, batch_size):
                batch_data = table_data[i:i + batch_size]
                
                batch_success = await CozeService._upload_batch_to_coze(
                    sync_config["coze_workflow_id"],
                    batch_data,
                    sync_config["coze_api_url"],
                    sync_config["coze_api_key"],
                    sync_config["table_name"]
                )
                
                success_count += batch_success
                
                # 记录进度
                progress = min(100, int((i + len(batch_data)) / total_records * 100))
                logger.info(f"同步进度: {progress}% ({i + len(batch_data)}/{total_records})")
                
                # 短暂延迟，避免API限制
                await asyncio.sleep(0.5)
            
            # 更新最后同步时间
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                db_config = await session.get(CozeSyncConfig, config_uuid)
                if db_config:
                    db_config.last_sync_time = datetime.now()
                    await session.commit()
            
            return {
                "success": True,
                "message": f"同步完成，成功同步 {success_count} 条记录",
                "records_synced": success_count,
                "total_records": total_records
            }
            
        except Exception as e:
            logger.error(f"手动同步失败: {str(e)}")
            
            # 更新错误信息
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                db_config = await session.get(CozeSyncConfig, config_uuid)
                if db_config:
                    db_config.last_error = str(e)
                    db_config.status = "ERROR"
                    await session.commit()
            
            return {
                "success": False,
                "message": f"同步失败: {str(e)}",
                "records_synced": 0
            }
    
    @classmethod
    async def get_sync_templates(cls) -> List[Dict[str, Any]]:
        """获取所有同步模板"""
        try:
            templates = []
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                from sqlalchemy import text
                configs = await session.execute(
                    text("SELECT * FROM coze_sync_configs WHERE enabled = TRUE")
                )
                
                for config in configs.fetchall():
                    template = {
                        "uuid": config.uuid,
                        "config_title": config.config_title,
                        "table_name": config.table_name,
                        "coze_workflow_id": config.coze_workflow_id,
                        "sync_on_insert": config.sync_on_insert,
                        "sync_on_update": config.sync_on_update,
                        "sync_on_delete": config.sync_on_delete,
                        "selected_fields": config.selected_fields or [],
                        "status": config.status,
                        "last_sync_time": config.last_sync_time,
                        "created_at": config.created_at
                    }
                    templates.append(template)
            
            return templates
            
        except Exception as e:
            logger.error(f"获取同步模板失败: {str(e)}")
            return []
    
    @classmethod
    async def update_sync_template(
        cls,
        config_uuid: UUID,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新同步模板"""
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                config = await session.get(CozeSyncConfig, config_uuid)
                if not config:
                    raise ValueError(f"同步配置不存在: {config_uuid}")
                
                # 更新字段
                allowed_fields = [
                    "config_title", "coze_workflow_id", "coze_api_url", 
                    "coze_api_key", "sync_on_insert", "sync_on_update", 
                    "sync_on_delete", "selected_fields", "enabled", "status"
                ]
                
                for field, value in updates.items():
                    if field in allowed_fields and hasattr(config, field):
                        setattr(config, field, value)
                
                await session.commit()
                await session.refresh(config)
            
            return {
                "success": True,
                "message": "同步模板更新成功",
                "config": {
                    "uuid": config.uuid,
                    "config_title": config.config_title,
                    "table_name": config.table_name
                }
            }
            
        except Exception as e:
            logger.error(f"更新同步模板失败: {str(e)}")
            return {
                "success": False,
                "message": f"更新同步模板失败: {str(e)}"
            }
    
    @classmethod
    async def delete_sync_template(cls, config_uuid: UUID) -> Dict[str, Any]:
        """删除同步模板"""
        try:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                config = await session.get(CozeSyncConfig, config_uuid)
                if config:
                    await session.delete(config)
                    await session.commit()
            
            return {
                "success": True,
                "message": "同步模板删除成功"
            }
            
        except Exception as e:
            logger.error(f"删除同步模板失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除同步模板失败: {str(e)}"
            }
    
    @classmethod
    async def get_template_preview(
        cls,
        table_name: str,
        selected_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取同步模板预览"""
        try:
            # 获取表信息
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                all_tables = await CozeService.get_all_tables(session)
                if table_name not in all_tables:
                    raise ValueError(f"表 {table_name} 不存在")
                
                table_info = all_tables[table_name]
                table_fields = table_info.get("fields", [])
                
                # 获取样本数据
                sample_data = await CozeService.get_table_sample_data(table_name)
                
                # 如果指定了字段，过滤样本数据
                if selected_fields:
                    filtered_data = []
                    for record in sample_data:
                        filtered_record = {}
                        for field in selected_fields:
                            if field in record:
                                filtered_record[field] = record[field]
                        filtered_data.append(filtered_record)
                    sample_data = filtered_data
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "table_display_name": table_info.get("display_name", table_name),
                    "available_fields": table_fields,
                    "selected_fields": selected_fields or [f["name"] for f in table_fields],
                    "sample_data": sample_data,
                    "sample_size": len(sample_data)
                }
            
        except Exception as e:
            logger.error(f"获取模板预览失败: {str(e)}")
            return {
                "success": False,
                "message": f"获取模板预览失败: {str(e)}"
            }