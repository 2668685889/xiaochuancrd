"""MCP 服务 - 直接调用 MCP 服务器"""

import httpx
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.services.deepseek_service import get_deepseek_service

logger = logging.getLogger(__name__)


class MCPService:
    """MCP 服务类"""
    
    def __init__(self):
        self.mcp_base_url = "http://localhost:8001"  # MCP 服务器地址
        self.is_initialized = False
        self.client = None
        self.deepseek_service = None
    
    async def initialize(self):
        """初始化 MCP 服务"""
        try:
            # 尝试使用requests库而不是httpx
            import requests
            
            # 测试 MCP 服务器连接
            response = requests.get(f"{self.mcp_base_url}/health", timeout=30)
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("✅ MCP 服务初始化成功")
                # 创建httpx客户端用于后续请求
                self.client = httpx.AsyncClient(timeout=30.0)
            else:
                logger.error(f"❌ MCP 服务健康检查失败: {response.status_code}")
                self.is_initialized = False
                
        except Exception as e:
            logger.error(f"❌ MCP 服务初始化失败: {str(e)}")
            self.is_initialized = False
    
    async def is_ready(self) -> bool:
        """检查 MCP 服务是否就绪"""
        if not self.is_initialized:
            return False
            
        try:
            # 使用同步的requests库检查连接
            import requests
            response = requests.get(f"{self.mcp_base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"MCP服务健康检查失败: {str(e)}")
            return False
    
    async def _analyze_query_result(self, query: str, data: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """
        分析查询结果并调用分析模型
        
        Args:
            query: 原始查询
            data: 查询结果数据，包含response和metadata
            session_id: 会话ID
            
        Returns:
            分析结果
        """
        try:
            # 从响应中提取表格数据
            response_text = data.get('response', '')
            table_data = self._parse_table_from_text(response_text)
            
            # 如果没有解析到表格数据，使用原始响应
            if not table_data:
                formatted_data = response_text
            else:
                formatted_data = self._format_data_for_analysis(table_data)
            
            # 获取用户设置中的分析模型配置
            from app.core.database import get_async_db
            from app.models.smart_assistant import WorkspaceModel
            from sqlalchemy import select
            
            # 获取当前用户的分析模型配置
            analysis_model_config = None
            try:
                async for db in get_async_db():
                    # 这里简化处理，使用工作空间设置
                    stmt = select(WorkspaceModel).where(WorkspaceModel.is_active == True)
                    result = await db.execute(stmt)
                    workspace = result.scalar_one_or_none()
                    
                    if workspace and workspace.settings:
                        settings_data = workspace.settings
                        if 'analysis_model' in settings_data:
                            analysis_model_config = settings_data['analysis_model']
                    break
            except Exception as e:
                logger.warning(f"获取分析模型配置失败: {e}")
            
            # 如果没有配置分析模型，使用默认的DeepSeek服务
            if not analysis_model_config:
                # 开发环境下使用模拟数据
                if getattr(settings, 'DEBUG', False):
                    logger.info("使用模拟分析结果")
                    return {
                        "success": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"""# 销售订单数据分析

## 数据概况
- 共找到 {len(table_data) if table_data else 0} 条销售订单记录
- 所有订单状态均为 CONFIRMED（已确认）
- 订单总金额范围：14,997.00 - 44,991.00

## 关键发现
1. 所有订单均来自同一客户：上海贸易有限公司
2. 订单日期集中在2025年10月11日至13日
3. 订单金额呈递增趋势：14,997.00 → 29,994.00 → 44,991.00

## 趋势分析
- 订单金额每日翻倍，显示业务量快速增长
- 预计交货日期统一为2025-10-20，表明集中处理模式

## 建议
1. 关注大额订单的交付能力
2. 考虑分散交货日期以降低交付压力
3. 维护与上海贸易有限公司的良好合作关系
""",
                                "metadata": {
                                    "source": "mcp_analysis",
                                    "query_type": "data_analysis",
                                    "model": "deepseek-chat",
                                    "timestamp": datetime.now().isoformat(),
                                    "data_count": len(table_data) if table_data else 0,
                                    "analysis_model": "default_deepseek"
                                }
                            }
                        ]
                    }
                
                if not self.deepseek_service:
                    self.deepseek_service = get_deepseek_service()
                
                # 构建分析提示词
                analysis_prompt = f"""
                你是一个专业的数据分析助手。请根据以下查询结果，提供深入的数据分析。
                
                用户查询: {query}
                
                查询结果数据:
                {formatted_data}
                
                请提供简洁、专业的数据分析结果，包括：
                1. 数据概况总结
                2. 关键发现和洞察
                3. 趋势分析（如果适用）
                4. 建议和行动项
                """
                
                # 调用DeepSeek生成分析结果
                result = await self.deepseek_service.generate_response(
                    message=query,
                    system_prompt=analysis_prompt
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "content": [
                            {
                                "type": "text",
                                "text": result["response"],
                                "metadata": {
                                    "source": "mcp_analysis",
                                    "query_type": "data_analysis",
                                    "model": "deepseek-chat",
                                    "timestamp": datetime.now().isoformat(),
                                    "data_count": len(table_data) if table_data else 0,
                                    "analysis_model": "default_deepseek"
                                }
                            }
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "分析生成失败"),
                        "content": []
                    }
            else:
                # 使用配置的分析模型
                # 这里可以根据配置调用不同的分析服务
                # 暂时返回错误，表示需要实现其他分析模型
                return {
                    "success": False,
                    "error": f"暂不支持配置的分析模型: {analysis_model_config.get('model_id', 'unknown')}",
                    "content": []
                }
                
        except Exception as e:
            logger.error(f"分析查询结果失败: {e}")
            return {
                "success": False,
                "error": f"分析处理异常: {str(e)}",
                "content": []
            }
    
    def _parse_table_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中解析表格数据
        
        Args:
            text: 包含表格的文本
            
        Returns:
            解析后的数据列表
        """
        try:
            lines = text.split('\n')
            table_lines = []
            
            # 找到表格的开始和结束
            start_index = -1
            for i, line in enumerate(lines):
                if '|' in line and '---' in line:
                    # 找到表头分隔符，上一行是表头
                    start_index = i - 1
                    break
            
            if start_index < 0 or start_index >= len(lines):
                return []
            
            # 提取表格行
            for i in range(start_index, len(lines)):
                if '|' in lines[i]:
                    table_lines.append(lines[i])
                else:
                    # 遇到非表格行，停止
                    break
            
            if len(table_lines) < 3:  # 至少需要表头、分隔符、一行数据
                return []
            
            # 解析表头
            headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]  # 去掉首尾空元素
            
            # 解析数据行（跳过分隔符行）
            data_rows = []
            for line in table_lines[2:]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]  # 去掉首尾空元素
                if len(cells) == len(headers):
                    row_data = {}
                    for i, header in enumerate(headers):
                        row_data[header] = cells[i]
                    data_rows.append(row_data)
            
            return data_rows
        except Exception as e:
            logger.error(f"解析表格数据失败: {e}")
            return []
    
    def _format_data_for_analysis(self, data: List[Dict[str, Any]]) -> str:
        """
        格式化数据用于分析
        
        Args:
            data: 查询结果数据
            
        Returns:
            格式化后的数据字符串
        """
        if not data:
            return "无数据"
        
        # 获取所有列名
        columns = list(data[0].keys())
        
        # 构建格式化数据
        formatted_data = f"数据概览: 共 {len(data)} 条记录\n\n"
        formatted_data += "字段列表: " + ", ".join(columns) + "\n\n"
        
        # 添加前几条数据示例
        formatted_data += "数据示例:\n"
        for i, row in enumerate(data[:5]):  # 只显示前5条
            formatted_data += f"记录 {i+1}:\n"
            for col in columns:
                value = row.get(col, "")
                # 截断长字符串
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                formatted_data += f"  {col}: {value}\n"
            formatted_data += "\n"
        
        # 如果数据超过5条，添加说明
        if len(data) > 5:
            formatted_data += f"... 还有 {len(data) - 5} 条记录\n"
        
        return formatted_data
    
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
            # 使用同步的requests库调用MCP服务器
            import requests
            
            # 调用 MCP 服务器的查询接口
            query_data = {
                "natural_language_query": message,
                "session_id": session_id or str(uuid.uuid4()),
                "workspace_id": workspace_id or "default",
                "enable_analysis": False  # 默认禁用分析功能，提高查询速度
            }
            
            response = requests.post(
                f"{self.mcp_base_url}/query",
                json=query_data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 DEBUG: MCP服务器返回原始结果: {json.dumps(result, ensure_ascii=False, indent=2)}")  # 调试日志
                logger.info(f"🔍 MCP服务器返回结果: {result}")  # 调试日志
                
                # 解析MCP服务器返回的结果
                response_content = "查询成功"
                data_content = None
                analysis_content = None
                raw_data_content = None
                
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
                    
                    # 检查是否有分析结果 - 从响应根级别获取
                    if "analysis" in result:
                        analysis_content = result["analysis"].get("content") if isinstance(result["analysis"], dict) else result["analysis"]
                        print(f"🔍 DEBUG: 从响应根级别提取的分析内容: {str(analysis_content)[:200]}...")  # 调试日志
                        logger.info(f"🔍 从响应根级别提取的分析内容: {str(analysis_content)[:200]}...")  # 调试日志
                    # 兼容旧格式，从content内部获取
                    elif "analysis" in first_content:
                        analysis_content = first_content["analysis"]
                        print(f"🔍 DEBUG: 从content内部提取的分析内容: {analysis_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 从content内部提取的分析内容: {analysis_content[:200]}...")  # 调试日志
                    
                    # 检查是否有原始数据
                    if "raw_data" in first_content:
                        raw_data_content = first_content["raw_data"]
                        print(f"🔍 DEBUG: 提取的原始数据: {raw_data_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 提取的原始数据: {raw_data_content[:200]}...")  # 调试日志
                        
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
                    
                    # 检查是否有分析结果 - 从响应根级别获取
                    if "analysis" in result:
                        analysis_content = result["analysis"].get("content") if isinstance(result["analysis"], dict) else result["analysis"]
                        print(f"🔍 DEBUG: 从响应根级别提取的分析内容: {str(analysis_content)[:200]}...")  # 调试日志
                        logger.info(f"🔍 从响应根级别提取的分析内容: {str(analysis_content)[:200]}...")  # 调试日志
                    # 兼容旧格式，从results内部获取
                    elif "analysis" in first_result:
                        analysis_content = first_result["analysis"]
                        print(f"🔍 DEBUG: 从results内部提取的分析内容: {analysis_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 从results内部提取的分析内容: {analysis_content[:200]}...")  # 调试日志
                    
                    # 检查是否有原始数据
                    if "raw_data" in first_result:
                        raw_data_content = first_result["raw_data"]
                        print(f"🔍 DEBUG: 提取的原始数据: {raw_data_content[:200]}...")  # 调试日志
                        logger.info(f"🔍 提取的原始数据: {raw_data_content[:200]}...")  # 调试日志
                else:
                    print(f"🔍 DEBUG: 结果中没有content或results字段，可用字段: {list(result.keys())}")  # 调试日志
                    logger.warning(f"⚠️ 结果中没有content或results字段，可用字段: {list(result.keys())}")
                
                # 提取SQL语句 - 从metadata中获取
                sql_content = None
                if "metadata" in result and "sql" in result["metadata"]:
                    sql_content = result["metadata"]["sql"]
                elif "content" in result and len(result["content"]) > 0:
                    first_content = result["content"][0]
                    if "metadata" in first_content and "sql" in first_content["metadata"]:
                        sql_content = first_content["metadata"]["sql"]
                
                # 提取原始数据用于分析
                raw_data_for_analysis = None
                if "data" in result:
                    raw_data_for_analysis = result["data"]
                elif "content" in result and len(result["content"]) > 0:
                    first_content = result["content"][0]
                    if "data" in first_content:
                        raw_data_for_analysis = first_content["data"]
                    # 尝试从metadata中获取数据
                    elif "metadata" in first_content and "raw_data" in first_content["metadata"]:
                        raw_data_for_analysis = first_content["metadata"]["raw_data"]
                    # 如果没有找到数据，但有SQL查询结果，则尝试从数据库重新获取
                    elif "metadata" in first_content and "sql" in first_content["metadata"]:
                        sql = first_content["metadata"]["sql"]
                        if sql and "SELECT" in sql.upper():
                            try:
                                logger.info(f"🔍 尝试执行SQL获取原始数据: {sql[:100]}...")
                                # 这里可以执行SQL获取原始数据，但需要数据库连接
                                # 暂时跳过，因为需要额外的数据库连接
                                logger.warning("⚠️ 无法执行SQL获取原始数据，需要数据库连接")
                            except Exception as e:
                                logger.error(f"❌ 执行SQL获取原始数据失败: {e}")
                
                # 如果没有找到原始数据，但有文本内容，尝试从文本中提取表格数据
                if not raw_data_for_analysis and "content" in result and len(result["content"]) > 0:
                    first_content = result["content"][0]
                    if "text" in first_content:
                        text_content = first_content["text"]
                        # 简单检查文本中是否包含表格数据
                        if "|" in text_content and "---" in text_content:
                            logger.info("🔍 从文本内容中检测到表格数据，将用于分析")
                            print("🔍 从文本内容中检测到表格数据，将用于分析")  # 添加控制台输出
                            # 尝试将表格文本转换为结构化数据
                            try:
                                raw_data_for_analysis = self._parse_table_from_text(text_content)
                                if raw_data_for_analysis:
                                    logger.info(f"✅ 成功解析表格数据，共 {len(raw_data_for_analysis)} 条记录")
                                    print(f"✅ 成功解析表格数据，共 {len(raw_data_for_analysis)} 条记录")  # 添加控制台输出
                                else:
                                    # 如果解析失败，将整个文本内容作为原始数据
                                    raw_data_for_analysis = text_content
                                    logger.warning("⚠️ 表格数据解析失败，使用原始文本")
                                    print("⚠️ 表格数据解析失败，使用原始文本")  # 添加控制台输出
                            except Exception as e:
                                logger.error(f"❌ 表格数据解析异常: {e}")
                                print(f"❌ 表格数据解析异常: {e}")  # 添加控制台输出
                                # 如果解析失败，将整个文本内容作为原始数据
                                raw_data_for_analysis = text_content
                
                # 添加调试日志
                logger.info(f"🔍 DEBUG: raw_data_for_analysis存在: {raw_data_for_analysis is not None}")
                logger.info(f"🔍 DEBUG: analysis_content存在: {analysis_content is not None}")
                print(f"🔍 DEBUG: raw_data_for_analysis存在: {raw_data_for_analysis is not None}")  # 添加控制台输出
                print(f"🔍 DEBUG: analysis_content存在: {analysis_content is not None}")  # 添加控制台输出
                
                # 如果有数据且没有分析结果，且启用了分析功能，则调用分析模型
                analysis_result = None
                # 注意：这里检查query_data中的enable_analysis参数，而不是硬编码调用分析模型
                if raw_data_for_analysis and not analysis_content and query_data.get("enable_analysis", False):
                    try:
                        logger.info(f"🔍 开始调用分析模型处理查询结果，数据量: {len(raw_data_for_analysis) if isinstance(raw_data_for_analysis, list) else '未知'}")
                        analysis_result = await self._analyze_query_result(
                            query=message,
                            data=raw_data_for_analysis,
                            session_id=session_id
                        )
                        
                        if analysis_result["success"]:
                            analysis_content = analysis_result["content"][0]["text"]
                            logger.info(f"✅ 分析模型处理成功，分析结果长度: {len(analysis_content)}")
                        else:
                            logger.warning(f"⚠️ 分析模型处理失败: {analysis_result.get('error', '未知错误')}")
                    except Exception as e:
                        logger.error(f"❌ 分析模型处理异常: {e}")
                
                return_value = {
                    "success": True,
                    "response": response_content,  # 这里现在包含实际的商品数据
                    "session_id": session_id or str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "mcp",
                    "data": data_content,
                    "sql": sql_content,
                    "chart": result.get("chart"),
                    "analysis": analysis_content,
                    "raw_data": raw_data_content
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