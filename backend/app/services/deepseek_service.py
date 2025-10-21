"""
DeepSeek API 服务
提供 DeepSeek 大模型的调用功能
"""

import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """DeepSeek API 服务类"""
    
    def __init__(self, api_key: str = None, api_domain: str = None, base_url: str = None, model_id: str = None):
        """
        初始化 DeepSeek 服务
        
        Args:
            api_key: DeepSeek API密钥
            api_domain: API域名
            base_url: API基础URL
            model_id: 模型ID，默认为"deepseek-chat"
        """
        self.api_key = api_key or getattr(settings, 'DEEPSEEK_API_KEY', None)
        self.api_domain = api_domain or getattr(settings, 'DEEPSEEK_API_DOMAIN', 'https://api.deepseek.com')
        self.base_url = base_url or getattr(settings, 'DEEPSEEK_BASE_URL', f'{self.api_domain}/v1')
        self.model_id = model_id or "deepseek-chat"
        self.client = None
        self.is_initialized = False
        
    async def initialize(self):
        """初始化服务"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            # 测试API连接
            response = await self.client.get("/models")
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("✅ DeepSeek API服务初始化成功")
            else:
                logger.error(f"❌ DeepSeek API连接失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API服务初始化失败: {str(e)}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """检查服务是否就绪"""
        if not self.is_initialized or not self.client:
            return False
            
        try:
            response = await self.client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def generate_sql_query(
        self,
        natural_language: str,
        database_schema: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据自然语言生成SQL查询语句
        
        Args:
            natural_language: 自然语言查询描述
            database_schema: 数据库模式描述
            examples: 示例查询列表
            custom_prompt: 自定义提示词
            
        Returns:
            包含SQL查询和元数据的字典
        """
        if not await self.is_ready():
            await self.initialize()
            
        if not await self.is_ready():
            return {
                "success": False,
                "error": "DeepSeek API服务未就绪",
                "sql": None
            }
        
        # 构建系统提示词
        system_prompt = self._build_sql_generation_prompt(database_schema, examples, custom_prompt)
        
        try:
            # 调用DeepSeek API
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": natural_language}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 尝试从响应中提取SQL查询
                sql_query = self._extract_sql_from_response(content)
                
                return {
                    "success": True,
                    "sql": sql_query,
                    "explanation": content,
                    "model": "deepseek-chat",
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                error_msg = f"API请求失败: {response.status_code}"
                if response.text:
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                    except:
                        error_msg += f" - {response.text}"
                
                logger.error(f"❌ DeepSeek API请求失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "sql": None
                }
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API调用异常: {str(e)}")
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
                "sql": None
            }
    
    async def generate_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成自然语言响应
        
        Args:
            message: 用户消息
            context: 上下文消息列表
            system_prompt: 系统提示词
            
        Returns:
            包含响应内容的字典
        """
        if not await self.is_ready():
            await self.initialize()
            
        if not await self.is_ready():
            return {
                "success": False,
                "error": "DeepSeek API服务未就绪",
                "response": "服务暂时不可用，请稍后再试"
            }
        
        # 构建消息列表
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system", 
                "content": "你是一个专业的ERP系统智能助手，帮助用户查询和分析业务数据。请用简洁、专业的语言回答用户问题。"
            })
        
        # 添加上下文消息
        if context:
            messages.extend(context)
        
        # 添加用户消息
        messages.append({"role": "user", "content": message})
        
        try:
            # 调用DeepSeek API
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return {
                    "success": True,
                    "response": content,
                    "model": "deepseek-chat",
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                error_msg = f"API请求失败: {response.status_code}"
                if response.text:
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                    except:
                        error_msg += f" - {response.text}"
                
                logger.error(f"❌ DeepSeek API请求失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "response": "服务暂时不可用，请稍后再试"
                }
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API调用异常: {str(e)}")
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
                "response": "服务暂时不可用，请稍后再试"
            }
    
    def _build_sql_generation_prompt(
        self, 
        database_schema: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """构建SQL生成的系统提示词"""
        
        # 如果提供了自定义提示词，直接使用它
        if custom_prompt:
            prompt = custom_prompt
            
            # 如果自定义提示词中不包含数据库模式，自动添加
            if database_schema and "数据库模式" not in custom_prompt:
                prompt += f"\n\n数据库模式:\n{database_schema}\n"
            
            # 如果自定义提示词中不包含示例，自动添加
            if examples and "示例" not in custom_prompt:
                prompt += "\n示例查询:\n"
                for i, example in enumerate(examples, 1):
                    prompt += f"{i}. 自然语言: {example.get('natural', '')}\n"
                    prompt += f"   SQL: {example.get('sql', '')}\n\n"
            
            return prompt
        
        # 否则使用默认提示词
        prompt = """你是一个专业的SQL查询生成助手。根据用户的自然语言描述，生成准确的MySQL查询语句。

规则:
1. 只返回SQL查询语句，不要包含任何解释
2. 使用标准的MySQL语法
3. 确保查询语句安全，避免SQL注入
4. 如果查询涉及多个表，使用适当的JOIN语句
5. 添加适当的WHERE条件进行过滤
6. 对于日期范围查询，使用BETWEEN语句

"""
        
        if database_schema:
            prompt += f"\n数据库模式:\n{database_schema}\n"
        
        if examples:
            prompt += "\n示例查询:\n"
            for i, example in enumerate(examples, 1):
                prompt += f"{i}. 自然语言: {example.get('natural', '')}\n"
                prompt += f"   SQL: {example.get('sql', '')}\n\n"
        
        return prompt
    
    def _extract_sql_from_response(self, content: str) -> Optional[str]:
        """从响应中提取SQL查询语句"""
        # 尝试提取SQL代码块
        import re
        
        # 查找SQL代码块
        sql_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(sql_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 查找通用代码块
        code_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_pattern, content, re.DOTALL)
        if match:
            # 检查是否包含SQL关键字
            code = match.group(1).strip()
            if any(keyword in code.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "FROM"]):
                return code
        
        # 如果没有代码块，尝试查找SELECT语句
        select_pattern = r"(SELECT\s+.*?)(?:\n\n|\Z)"
        match = re.search(select_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 如果都找不到，返回原始内容
        return content.strip()
    
    async def close(self):
        """关闭服务"""
        if self.client:
            await self.client.aclose()
            self.is_initialized = False


# 全局服务实例
_deepseek_service_instance: Optional[DeepSeekService] = None


def get_deepseek_service(
    api_key: str = None,
    api_domain: str = None,
    base_url: str = None
) -> DeepSeekService:
    """获取DeepSeek服务实例"""
    global _deepseek_service_instance
    if _deepseek_service_instance is None:
        _deepseek_service_instance = DeepSeekService(api_key, api_domain, base_url)
    return _deepseek_service_instance


def get_configured_deepseek_service(model_config: Dict[str, Any]) -> DeepSeekService:
    """
    获取使用数据库配置的DeepSeek服务实例
    
    Args:
        model_config: 从数据库获取的模型配置
        
    Returns:
        配置好的DeepSeek服务实例
    """
    api_key = model_config.get("api_key")
    api_domain = model_config.get("api_domain", "https://api.deepseek.com")
    base_url = model_config.get("base_url", f'{api_domain}/v1')
    model_id = model_config.get("model_id", "deepseek-chat")
    
    # 创建新的服务实例
    service = DeepSeekService(api_key, api_domain, base_url, model_id)
    
    return service


async def initialize_deepseek_service(
    api_key: str = None,
    api_domain: str = None,
    base_url: str = None
):
    """初始化DeepSeek服务"""
    service = get_deepseek_service(api_key, api_domain, base_url)
    await service.initialize()


async def initialize_configured_deepseek_service(model_config: Dict[str, Any]) -> DeepSeekService:
    """
    初始化使用数据库配置的DeepSeek服务
    
    Args:
        model_config: 从数据库获取的模型配置
        
    Returns:
        初始化完成的DeepSeek服务实例
    """
    service = get_configured_deepseek_service(model_config)
    await service.initialize()
    return service


async def close_deepseek_service():
    """关闭DeepSeek服务"""
    global _deepseek_service_instance
    if _deepseek_service_instance:
        await _deepseek_service_instance.close()
        _deepseek_service_instance = None