"""MCP 服务 - 直接调用 MCP 服务器"""

import httpx
import json
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)


class MCPService:
    """MCP 服务类"""
    
    def __init__(self):
        self.mcp_base_url = "http://localhost:8001"  # MCP 服务器地址
        self.is_initialized = False
        self.client = None
    
    async def initialize(self):
        """初始化 MCP 服务"""
        try:
            self.client = httpx.AsyncClient(timeout=30.0)
            
            # 测试 MCP 服务器连接
            response = await self.client.get(f"{self.mcp_base_url}/health")
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("✅ MCP 服务初始化成功")
            else:
                logger.error(f"❌ MCP 服务健康检查失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ MCP 服务初始化失败: {str(e)}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """检查 MCP 服务是否就绪"""
        if not self.is_initialized:
            return False
            
        try:
            response = await self.client.get(f"{self.mcp_base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def process_chat_message(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理聊天消息 - 调用 MCP 服务器的自然语言查询功能
        
        Args:
            message: 用户输入的消息
            session_id: 会话ID
            workspace_id: 工作空间ID
            
        Returns:
            处理结果字典
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not await self.is_ready():
            return {
                "success": False,
                "response": "MCP 服务未就绪，请稍后再试",
                "session_id": session_id or str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "mcp"
            }
        
        try:
            # 调用 MCP 服务器的查询接口
            query_data = {
                "natural_language_query": message,
                "session_id": session_id or str(uuid.uuid4()),
                "workspace_id": workspace_id or "default"
            }
            
            response = await self.client.post(
                f"{self.mcp_base_url}/query",
                json=query_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 DEBUG: MCP服务器返回原始结果: {json.dumps(result, ensure_ascii=False, indent=2)}")  # 调试日志
                logger.info(f"🔍 MCP服务器返回结果: {result}")  # 调试日志
                
                # 解析MCP服务器返回的结果
                response_content = "查询成功"
                data_content = None
                
                # 检查MCP服务器返回的数据结构
                if "content" in result and len(result["content"]) > 0:
                    # 获取第一个内容项
                    first_content = result["content"][0]
                    print(f"🔍 DEBUG: 第一个内容项: {json.dumps(first_content, ensure_ascii=False, indent=2)}")  # 调试日志
                    logger.info(f"🔍 第一个内容项: {first_content}")  # 调试日志
                    
                    # 提取文本内容
                    if "text" in first_content:
                        response_content = first_content["text"]
                        print(f"🔍 DEBUG: 提取的响应内容: {response_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 提取的响应内容: {response_content[:200]}...")  # 调试日志
                    else:
                        print(f"🔍 DEBUG: 第一个内容项中没有text字段，可用字段: {list(first_content.keys())}")  # 调试日志
                        logger.warning(f"⚠️ 第一个内容项中没有text字段，可用字段: {list(first_content.keys())}")
                    
                    # 提取完整的响应数据，包括metadata
                    data_content = {
                        "content": first_content.get("text", ""),
                        "metadata": result.get("metadata", {}),
                        "raw_response": result  # 包含完整的原始响应
                    }
                    print(f"🔍 DEBUG: 构建的data_content: {json.dumps(data_content, ensure_ascii=False, indent=2)[:500]}...")  # 调试日志
                elif "results" in result and len(result["results"]) > 0:
                    # 兼容旧版本格式
                    first_result = result["results"][0]
                    print(f"🔍 DEBUG: 第一个结果内容: {json.dumps(first_result, ensure_ascii=False, indent=2)}")  # 调试日志
                    logger.info(f"🔍 第一个结果内容: {first_result}")  # 调试日志
                    
                    # 直接使用MCP服务器返回的完整内容作为响应
                    if "content" in first_result:
                        response_content = first_result["content"]
                        print(f"🔍 DEBUG: 提取的响应内容: {response_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 提取的响应内容: {response_content[:200]}...")  # 调试日志
                    else:
                        print(f"🔍 DEBUG: 第一个结果中没有content字段，可用字段: {list(first_result.keys())}")  # 调试日志
                        logger.warning(f"⚠️ 第一个结果中没有content字段，可用字段: {list(first_result.keys())}")
                    
                    # 提取完整的响应数据，包括metadata
                    data_content = {
                        "content": first_result.get("content", ""),
                        "metadata": first_result.get("metadata", {}),
                        "raw_response": result  # 包含完整的原始响应
                    }
                    print(f"🔍 DEBUG: 构建的data_content: {json.dumps(data_content, ensure_ascii=False, indent=2)[:500]}...")  # 调试日志
                else:
                    print(f"🔍 DEBUG: 结果中没有content或results字段，可用字段: {list(result.keys())}")  # 调试日志
                    logger.warning(f"⚠️ 结果中没有content或results字段，可用字段: {list(result.keys())}")
                
                return_value = {
                    "success": True,
                    "response": response_content,  # 这里现在包含实际的商品数据
                    "session_id": session_id or str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "mcp",
                    "data": data_content,
                    "sql": result.get("sql"),
                    "chart": result.get("chart")
                }
                print(f"🔍 DEBUG: 最终返回值: {json.dumps(return_value, ensure_ascii=False, indent=2)}")  # 调试日志
                return return_value
            else:
                error_msg = f"MCP 查询失败: {response.status_code}"
                if response.text:
                    error_detail = response.json().get("detail", response.text)
                    error_msg = f"MCP 查询失败: {error_detail}"
                
                return {
                    "success": False,
                    "response": error_msg,
                    "session_id": session_id or str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "mcp"
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"MCP 服务调用异常: {str(e)}",
                "session_id": session_id or str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "mcp"
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """获取 MCP 服务能力信息"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            response = await self.client.get(f"{self.mcp_base_url}/capabilities")
            if response.status_code == 200:
                return response.json()
            else:
                return {"capabilities": ["自然语言查询", "数据分析", "报表生成"]}
        except Exception:
            return {"capabilities": ["自然语言查询", "数据分析", "报表生成"]}
    
    async def close(self):
        """关闭 MCP 服务"""
        if self.client:
            await self.client.aclose()
            self.is_initialized = False


# 全局 MCP 服务实例
_mcp_service_instance: Optional[MCPService] = None


def get_mcp_service() -> MCPService:
    """获取 MCP 服务实例"""
    global _mcp_service_instance
    if _mcp_service_instance is None:
        _mcp_service_instance = MCPService()
    return _mcp_service_instance


async def initialize_mcp_service():
    """初始化 MCP 服务"""
    service = get_mcp_service()
    await service.initialize()


async def close_mcp_service():
    """关闭 MCP 服务"""
    global _mcp_service_instance
    if _mcp_service_instance:
        await _mcp_service_instance.close()
        _mcp_service_instance = None