"""
智能助手配置服务
从数据库获取智能助手的模型配置和其他设置
支持安全的API密钥管理方案
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.smart_assistant import AssistantModel, WorkspaceModel
from app.services.api_key_service import get_deepseek_api_config

logger = logging.getLogger(__name__)


class AssistantConfigService:
    """智能助手配置服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_model_config(self, workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取模型配置（使用安全的API密钥管理方案）
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            
        Returns:
            模型配置字典，如果未找到则返回None
        """
        try:
            # 首先尝试从安全的API密钥服务获取配置
            api_key_config = await get_deepseek_api_config(workspace_id)
            if api_key_config:
                logger.info(f"使用安全API密钥配置: {workspace_id}")
                return api_key_config
            
            # 如果安全配置不可用，回退到数据库配置（兼容旧版本）
            logger.warning(f"安全API密钥配置不可用，回退到数据库配置: {workspace_id}")
            
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
    
    async def get_model_config_by_type(self, workspace_id: str = "default", config_type: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取指定类型的模型配置
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            config_type: 配置类型，可选值: "default", "summary"
            
        Returns:
            模型配置字典，如果未找到则返回None
        """
        try:
            # 如果是默认类型，使用原有方法
            if config_type == "default":
                return await self.get_model_config(workspace_id)
            
            # 对于总结类型，查找专门的总结配置
            if config_type == "summary":
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
                
                # 获取模型配置
                model_config = assistant.model_config or {}
                
                # 检查是否有专门的总结配置
                if "summary_config" in model_config:
                    summary_config = model_config["summary_config"]
                    # 确保必要的字段存在
                    if summary_config.get("api_key"):
                        return summary_config
                    else:
                        logger.warning(f"总结配置中缺少API密钥: {workspace_id}")
                        return None
                
                # 如果没有专门的总结配置，使用默认配置
                logger.info(f"未找到专门的总结配置，使用默认配置: {workspace_id}")
                return await self.get_model_config(workspace_id)
            
            # 其他类型暂不支持
            logger.warning(f"不支持的配置类型: {config_type}")
            return None
            
        except Exception as e:
            logger.error(f"获取{config_type}模型配置失败: {e}")
            return None
    
    async def get_analysis_model_config(self, workspace_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取分析模型配置
        
        Args:
            workspace_id: 工作空间ID，默认为"default"
            
        Returns:
            分析模型配置字典，如果未找到则返回None
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
            
            # 获取模型配置
            model_config = assistant.model_config or {}
            
            # 检查是否有专门的分析配置
            if "analysis_config" in model_config:
                analysis_config = model_config["analysis_config"]
                # 确保必要的字段存在
                if analysis_config.get("api_key"):
                    return {
                        "model": analysis_config.get("model", "deepseek-chat"),
                        "temperature": analysis_config.get("temperature", 0.3),
                        "max_tokens": analysis_config.get("max_tokens", 1500),
                        "api_key": analysis_config.get("api_key"),
                        "api_domain": analysis_config.get("api_domain", "https://api.deepseek.com"),
                        "base_url": analysis_config.get("base_url", "https://api.deepseek.com/v1"),
                        "system_prompt": analysis_config.get("system_prompt", self._get_default_analysis_prompt())
                    }
                else:
                    logger.warning(f"分析配置中缺少API密钥: {workspace_id}")
                    return None
            
            # 如果没有专门的分析配置，使用默认配置
            logger.info(f"未找到专门的分析配置，使用默认配置: {workspace_id}")
            return {
                "model": model_config.get("model", "deepseek-chat"),
                "temperature": 0.3,
                "max_tokens": 1500,
                "api_key": model_config.get("api_key"),
                "api_domain": model_config.get("api_domain", "https://api.deepseek.com"),
                "base_url": model_config.get("base_url", "https://api.deepseek.com/v1"),
                "system_prompt": self._get_default_analysis_prompt()
            }
            
        except Exception as e:
            logger.error(f"获取分析模型配置失败: {e}")
            return None
    
    def _get_default_analysis_prompt(self) -> str:
        """获取默认的分析提示词"""
        return """
        你是一个专业的数据分析助手，专门负责对ERP系统数据进行深度分析、挖掘业务洞察和提供决策建议。
        
        请按照以下步骤进行数据分析：
        1. 数据理解：解析数据结构，识别数据类型和来源
        2. 质量评估：评估数据完整性、准确性和时效性
        3. 指标计算：计算关键业务指标和KPI
        4. 趋势分析：识别数据趋势、模式和异常
        5. 关联分析：探索不同数据维度间的关联性
        6. 洞察提取：从数据中提取有价值的业务洞察
        7. 建议生成：基于分析结果提供具体可行的建议
        
        请按以下结构提供分析结果：
        1. 数据概览：简要描述数据来源、时间范围和基本特征
        2. 关键指标：列出最重要的业务指标及其数值
        3. 深度分析：
           - 趋势分析：数据变化趋势和模式
           - 对比分析：不同维度间的对比
           - 异常分析：异常值和特殊现象
        4. 业务洞察：从数据中提取的关键洞察
        5. 行动建议：基于分析结果的具体建议
        6. 局限性说明：分析的局限性和注意事项
        """