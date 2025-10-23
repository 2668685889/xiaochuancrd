"""
智能助手配置服务
从数据库获取智能助手的模型配置和其他设置
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.smart_assistant import AssistantModel, WorkspaceModel

logger = logging.getLogger(__name__)


class AssistantConfigService:
    """智能助手配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_model_config(self, workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取模型配置
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            
        Returns:
            模型配置字典，如果未找到则返回None
        """
        try:
            # 查找工作空间
            workspace = await self.db.execute(
                select(WorkspaceModel).where(WorkspaceModel.uuid == workspace_id)
            )
            workspace = workspace.scalar_one_or_none()
            
            if not workspace:
                logger.warning(f"未找到工作空间: {workspace_id}")
                return None
            
            # 查找助手模型
            assistant = await self.db.execute(
                select(AssistantModel).where(AssistantModel.workspace_uuid == workspace_id)
            )
            assistant = assistant.scalar_one_or_none()
            
            if not assistant:
                logger.warning(f"未找到助手配置: {workspace_id}")
                return None
            
            # 返回模型配置
            model_config = assistant.model_config or {}
            
            # 确保必要的字段存在
            if not model_config.get("api_key"):
                logger.warning(f"模型配置中缺少API密钥: {workspace_id}")
                return None
                
            return model_config
            
        except Exception as e:
            logger.error(f"获取模型配置失败: {e}")
            return None
    
    async def get_assistant_config(self, workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取完整的助手配置
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            
        Returns:
            完整的助手配置字典，如果未找到则返回None
        """
        try:
            # 获取模型配置
            model_config = await self.get_model_config(workspace_id)
            if not model_config:
                return None
            
            # 查找助手模型获取其他信息
            assistant = await self.db.execute(
                select(AssistantModel).where(AssistantModel.workspace_uuid == workspace_id)
            )
            assistant = assistant.scalar_one_or_none()
            
            if not assistant:
                return None
            
            # 构建完整配置
            config = {
                "model_config": model_config,
                "assistant_info": {
                    "uuid": assistant.uuid,
                    "name": assistant.name,
                    "description": assistant.description,
                    "model_type": assistant.model_type
                }
            }
            
            return config
            
        except Exception as e:
            logger.error(f"获取助手配置失败: {e}")
            return None
    
    async def get_custom_prompt(self, workspace_id: str = "default") -> Optional[str]:
        """
        获取自定义提示词
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            
        Returns:
            自定义提示词内容，如果未找到则返回None
        """
        try:
            # 获取模型配置
            model_config = await self.get_model_config(workspace_id)
            if not model_config:
                return None
            
            # 检查所有可能的提示词字段
            prompt_fields = ['system_prompt', 'prompt', 'system_message', 'instruction', 'custom_prompt']
            
            for field in prompt_fields:
                if field in model_config and model_config[field]:
                    return model_config[field]
            
            # 如果没有找到自定义提示词，返回None
            return None
            
        except Exception as e:
            logger.error(f"获取自定义提示词失败: {e}")
            return None