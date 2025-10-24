"""
DeepSeek API 服务
提供 DeepSeek 大模型的调用功能
"""

import aiohttp
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
        self.session = None
        self.is_initialized = False
        
    async def initialize(self):
        """初始化服务"""
        try:
            # 确保使用正确的API基础URL
            if not self.base_url.endswith('/'):
                self.base_url = f"{self.base_url.rstrip('/')}/"
            
            logger.info(f"正在初始化DeepSeek API服务，URL: {self.base_url}")
            
            # 创建连接器，禁用SSL验证
            connector = aiohttp.TCPConnector(verify_ssl=False)
            
            # 创建会话
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=60.0),
                connector=connector
            )
            
            # 测试API连接
            async with self.session.get("/models") as response:
                logger.info(f"API连接测试状态码: {response.status}")
                
                if response.status == 200:
                    self.is_initialized = True
                    logger.info("✅ DeepSeek API服务初始化成功")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ DeepSeek API连接失败: {response.status} - {error_text}")
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API服务初始化失败: {str(e)}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """检查服务是否就绪"""
        if not self.is_initialized or not self.session:
            return False
            
        try:
            async with self.session.get("/models") as response:
                return response.status == 200
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
            async with self.session.post(
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
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
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
                    error_msg = f"API请求失败: {response.status}"
                    error_text = await response.text()
                    try:
                        error_detail = json.loads(error_text)
                        error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                    except:
                        error_msg += f" - {error_text}"
                    
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
            async with self.session.post(
                "/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    return {
                        "success": True,
                        "response": content,
                        "model": "deepseek-chat",
                        "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    error_msg = f"API请求失败: {response.status}"
                    error_text = await response.text()
                    try:
                        error_detail = json.loads(error_text)
                        error_msg += f" - {error_detail.get('error', {}).get('message', '未知错误')}"
                    except:
                        error_msg += f" - {error_text}"
                    
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
    
    async def analyze_data(
        self,
        query: str,
        data: List[Dict[str, Any]],
        prompt: str = None
    ) -> Dict[str, Any]:
        """
        分析数据并提供洞察
        
        Args:
            query: 原始查询
            data: 要分析的数据
            prompt: 分析提示词
            
        Returns:
            包含分析结果的字典
        """
        if not await self.is_ready():
            await self.initialize()
            
        if not await self.is_ready():
            return {
                "success": False,
                "error": "DeepSeek API服务未就绪",
                "analysis": "服务暂时不可用，请稍后再试"
            }
        
        # 如果没有提供提示词，使用默认提示词
        if not prompt:
            prompt = f"""
            请分析以下查询结果，提供有价值的洞察和建议：
            
            查询内容：{query}
            
            数据概览：
            {self._format_data_for_analysis(data)}
            
            请提供：
            1. 数据关键发现
            2. 潜在问题或机会
            3. 建议的后续操作
            """
        
        try:
            # 调用DeepSeek API
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的数据分析助手，请提供简洁、专业的数据分析结果。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return {
                    "success": True,
                    "analysis": content,
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
                    "analysis": "数据分析失败，请稍后再试"
                }
                
        except Exception as e:
            logger.error(f"❌ DeepSeek API调用异常: {str(e)}")
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}",
                "analysis": "数据分析失败，请稍后再试"
            }
    
    def _format_data_for_analysis(self, data: List[Dict[str, Any]]) -> str:
        """格式化数据用于分析"""
        if not data:
            return "没有数据可供分析"
        
        # 获取数据概览
        data_overview = f"数据量: {len(data)} 条记录\n"
        
        # 获取字段信息
        if data and isinstance(data[0], dict):
            columns = list(data[0].keys())
            data_overview += f"字段: {', '.join(columns)}\n"
            
            # 添加前几条数据示例
            data_overview += "\n数据示例:\n"
            for i, row in enumerate(data[:5]):  # 只显示前5条
                data_overview += f"{i+1}. "
                for col in columns:
                    value = str(row.get(col, ""))
                    # 限制长度，避免过长
                    if len(value) > 50:
                        value = value[:47] + "..."
                    data_overview += f"{col}: {value}; "
                data_overview += "\n"
            
            # 如果数据超过5条，添加说明
            if len(data) > 5:
                data_overview += f"... 还有 {len(data) - 5} 条数据\n"
        
        return data_overview
    
    async def close(self):
        """关闭服务，清理资源"""
        if self.session:
            await self.session.close()
            self.session = None
            self.is_initialized = False
            logger.info("DeepSeek API服务已关闭")


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