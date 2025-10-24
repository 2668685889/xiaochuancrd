"""
API密钥管理服务
实现安全的API密钥存储和引用方案
"""

import os
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.api_key_management import APIKeyModel, APIKeyReferenceModel

logger = logging.getLogger(__name__)


class APIKeyService:
    """API密钥管理服务"""
    
    def __init__(self):
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        self.session = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_api_key_by_reference(self, workspace_uuid: str, reference_key: str) -> Optional[Dict[str, Any]]:
        """
        通过引用密钥获取真实的API密钥
        
        Args:
            workspace_uuid: 工作空间UUID
            reference_key: 引用密钥标识符
            
        Returns:
            包含真实API密钥的配置字典，如果找不到则返回None
        """
        try:
            # 获取密钥引用配置
            reference_result = await self.session.execute(
                select(APIKeyReferenceModel).where(
                    APIKeyReferenceModel.workspace_uuid == workspace_uuid,
                    APIKeyReferenceModel.reference_key == reference_key,
                    APIKeyReferenceModel.is_active == True
                )
            )
            reference = reference_result.scalars().first()
            
            if not reference:
                logger.warning(f"未找到引用密钥配置: {reference_key}, 工作空间: {workspace_uuid}")
                return None
            
            # 获取对应的密钥配置
            key_result = await self.session.execute(
                select(APIKeyModel).where(
                    APIKeyModel.workspace_uuid == workspace_uuid,
                    APIKeyModel.key_type == reference.key_type,
                    APIKeyModel.is_active == True
                )
            )
            api_key_config = key_result.scalars().first()
            
            if not api_key_config:
                logger.warning(f"未找到API密钥配置: {reference.key_type}, 工作空间: {workspace_uuid}")
                return None
            
            # 从环境变量获取真实密钥
            real_api_key = os.getenv(api_key_config.env_variable)
            if not real_api_key:
                logger.error(f"环境变量中未找到API密钥: {api_key_config.env_variable}")
                return None
            
            # 构建完整的配置
            config_data = reference.config_data or {}
            config_data.update({
                "api_key": real_api_key,
                "key_reference": reference_key,
                "key_type": reference.key_type
            })
            
            logger.info(f"成功获取API密钥配置: {reference_key}, 类型: {reference.key_type}")
            return config_data
            
        except Exception as e:
            logger.error(f"获取API密钥失败: {e}")
            return None
    
    async def get_deepseek_config(self, workspace_uuid: str = "default-workspace") -> Optional[Dict[str, Any]]:
        """
        获取DeepSeek API配置
        
        Args:
            workspace_uuid: 工作空间UUID
            
        Returns:
            DeepSeek配置字典
        """
        return await self.get_api_key_by_reference(workspace_uuid, "deepseek_default")
    
    async def get_deepseek_mcp_config(self, workspace_uuid: str = "default-workspace") -> Optional[Dict[str, Any]]:
        """
        获取MCP服务专用的DeepSeek API配置
        
        Args:
            workspace_uuid: 工作空间UUID
            
        Returns:
            DeepSeek MCP配置字典
        """
        return await self.get_api_key_by_reference(workspace_uuid, "deepseek_mcp")
    
    async def create_api_key_reference(self, 
                                     workspace_uuid: str, 
                                     key_type: str, 
                                     env_variable: str,
                                     description: str = "") -> bool:
        """
        创建API密钥引用
        
        Args:
            workspace_uuid: 工作空间UUID
            key_type: 密钥类型
            env_variable: 环境变量名称
            description: 描述信息
            
        Returns:
            创建是否成功
        """
        try:
            # 生成引用密钥标识符
            reference_key = f"{key_type}_default"
            
            # 检查是否已存在
            existing_result = await self.session.execute(
                select(APIKeyReferenceModel).where(
                    APIKeyReferenceModel.workspace_uuid == workspace_uuid,
                    APIKeyReferenceModel.reference_key == reference_key
                )
            )
            existing = existing_result.scalars().first()
            
            # 构建配置数据（不包含真实密钥）
            config_data = {
                "env_variable": env_variable,
                "description": description,
                "base_url": "https://api.deepseek.com",
                "model_name": "deepseek-chat"
            }
            
            if existing:
                # 更新现有配置
                existing.config_data = config_data
                existing.key_type = key_type
                existing.env_variable = env_variable
                existing.description = description
            else:
                # 创建新配置
                import uuid
                new_reference = APIKeyReferenceModel(
                    uuid=str(uuid.uuid4()),
                    workspace_uuid=workspace_uuid,
                    reference_key=reference_key,
                    key_type=key_type,
                    env_variable=env_variable,
                    description=description,
                    config_data=config_data
                )
                self.session.add(new_reference)
            
            await self.session.commit()
            logger.info(f"成功创建/更新API密钥引用: {reference_key}, 工作空间: {workspace_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"创建API密钥引用失败: {e}")
            await self.session.rollback()
            return False


# 全局服务实例
_api_key_service_instance: Optional[APIKeyService] = None


def get_api_key_service() -> APIKeyService:
    """获取API密钥服务实例"""
    global _api_key_service_instance
    if _api_key_service_instance is None:
        _api_key_service_instance = APIKeyService()
    return _api_key_service_instance


async def get_deepseek_api_config(workspace_uuid: str = "default-workspace") -> Optional[Dict[str, Any]]:
    """获取DeepSeek API配置（便捷函数）"""
    async with APIKeyService() as service:
        return await service.get_deepseek_config(workspace_uuid)


async def get_deepseek_mcp_api_config(workspace_uuid: str = "default-workspace") -> Optional[Dict[str, Any]]:
    """获取MCP服务专用的DeepSeek API配置（便捷函数）"""
    async with APIKeyService() as service:
        return await service.get_deepseek_mcp_config(workspace_uuid)