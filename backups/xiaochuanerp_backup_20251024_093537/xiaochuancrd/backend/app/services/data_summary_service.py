"""
数据总结服务
使用DeepSeek模型对SQL查询结果进行智能总结和格式化
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.deepseek_service import get_deepseek_service, get_configured_deepseek_service
from app.services.assistant_config_service import AssistantConfigService

logger = logging.getLogger(__name__)


class DataSummaryService:
    """数据总结服务类"""
    
    def __init__(self, workspace_id: str = "default", db: Optional[AsyncSession] = None):
        """
        初始化数据总结服务
        
        Args:
            workspace_id: 工作空间ID
            db: 数据库会话
        """
        self.workspace_id = workspace_id
        self.db = db
        self.config_service = AssistantConfigService(db) if db else None
        self.deepseek_service = None
        self.is_initialized = False
    
    async def initialize(self):
        """初始化服务"""
        try:
            # 如果没有数据库会话，使用默认配置
            if not self.config_service:
                self.deepseek_service = get_deepseek_service()
                self.is_initialized = True
                logger.info(f"✅ 使用默认配置初始化DeepSeek服务，工作空间: {self.workspace_id}")
                return
            
            # 获取专门用于数据总结的模型配置
            summary_config = await self.config_service.get_model_config_by_type(self.workspace_id, "summary")
            
            if summary_config:
                # 使用专门的总结配置创建DeepSeek服务
                self.deepseek_service = get_configured_deepseek_service(summary_config)
                await self.deepseek_service.initialize()
                logger.info(f"✅ 使用总结配置初始化DeepSeek服务成功，工作空间: {self.workspace_id}")
            else:
                # 回退到默认配置
                self.deepseek_service = get_deepseek_service()
                logger.warning(f"⚠️ 未找到总结模型配置，使用默认配置，工作空间: {self.workspace_id}")
            
            self.is_initialized = True
            logger.info("✅ 数据总结服务初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 数据总结服务初始化失败: {e}")
            # 回退到默认配置
            self.deepseek_service = get_deepseek_service()
            self.is_initialized = True
    
    async def generate_summary(
        self,
        data: List[Dict[str, Any]],
        query: str,
        query_type: Optional[str] = None,
        sql_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成数据摘要
        
        Args:
            data: 查询结果数据列表
            query: 用户的原始查询
            query_type: 查询类型（如"销售订单"、"库存查询"等）
            sql_query: 执行的SQL查询
            
        Returns:
            包含总结内容的字典
        """
        # 构造查询结果字典
        query_result = {"data": data}
        
        # 调用现有的summarize_query_result方法
        return await self.summarize_query_result(
            original_query=query,
            sql_query=sql_query or "",
            query_result=query_result,
            query_type=query_type
        )
    
    async def summarize_query_result(
        self,
        original_query: str,
        sql_query: str,
        query_result: Dict[str, Any],
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        总结查询结果
        
        Args:
            original_query: 用户的原始查询
            sql_query: 执行的SQL查询
            query_result: SQL查询结果
            query_type: 查询类型（如"销售订单"、"库存查询"等）
            
        Returns:
            包含总结内容的字典
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # 准备数据总结提示词
            summary_prompt = self._build_summary_prompt(original_query, sql_query, query_result, query_type)
            
            # 调用DeepSeek生成总结
            result = await self.deepseek_service.generate_response(
                message="请总结以下查询结果",
                system_prompt=summary_prompt
            )
            
            if result["success"]:
                # 解析总结结果
                summary_content = result["response"]
                
                # 尝试从总结中提取结构化信息
                structured_summary = self._parse_summary_content(summary_content, query_result)
                
                return {
                    "success": True,
                    "summary": summary_content,
                    "structured_summary": structured_summary,
                    "original_query": original_query,
                    "sql_query": sql_query,
                    "query_type": query_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # 如果DeepSeek总结失败，回退到基本格式化
                logger.warning(f"DeepSeek总结失败，回退到基本格式化: {result.get('error', '未知错误')}")
                return self._fallback_summary(original_query, sql_query, query_result, query_type)
                
        except Exception as e:
            logger.error(f"数据总结处理失败: {e}")
            # 回退到基本格式化
            return self._fallback_summary(original_query, sql_query, query_result, query_type)
    
    def _build_summary_prompt(
        self,
        original_query: str,
        sql_query: str,
        query_result: Dict[str, Any],
        query_type: Optional[str] = None
    ) -> str:
        """构建数据总结提示词"""
        
        # 提取查询结果数据
        result_data = []
        if "results" in query_result and query_result["results"]:
            result_data = query_result["results"]
        elif "data" in query_result and query_result["data"]:
            result_data = query_result["data"]
        
        # 计算总记录数
        total_records = len(result_data)
        
        # 构建提示词
        prompt = f"""
你是一个专业的ERP数据分析师。请根据以下信息，对查询结果进行智能总结和格式化：

## 用户原始查询
{original_query}

## 执行的SQL查询
```sql
{sql_query}
```

## 查询结果
- 总记录数: {total_records}
- 查询类型: {query_type or '未知'}

### 数据内容
{json.dumps(result_data[:1000], ensure_ascii=False, indent=2) if result_data else "无数据"}

## 总结要求
请按照以下要求对查询结果进行总结：

1. **总体概述**: 简要说明查询的目的和结果概况
2. **关键数据**: 提取最重要的数据点和指标
3. **数据洞察**: 基于数据提供有价值的观察和建议
4. **格式化输出**: 使用以下格式输出结果

```
**{query_type or '数据'}查询结果**

**总记录数**: {total_records}

**关键数据**:
- [关键数据点1]
- [关键数据点2]
- [关键数据点3]

**数据洞察**:
[基于数据的观察和建议]

**详细数据**:
[以表格或列表形式展示前10条重要记录]
```

注意事项：
- 如果没有数据，请明确说明"未找到相关数据"
- 总记录数必须准确反映实际查询结果
- 使用简洁、专业的语言
- 确保输出格式易于前端解析和显示
"""
        
        return prompt
    
    def _parse_summary_content(self, summary_content: str, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """解析总结内容，提取结构化信息"""
        
        # 提取总记录数
        total_records = 0
        if "results" in query_result and query_result["results"]:
            total_records = len(query_result["results"])
        elif "data" in query_result and query_result["data"]:
            total_records = len(query_result["data"])
        
        # 尝试从总结内容中提取关键信息
        structured_summary = {
            "total_records": total_records,
            "summary_text": summary_content,
            "key_points": [],
            "insights": []
        }
        
        # 简单的文本解析，提取关键点和洞察
        lines = summary_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("**关键数据**"):
                current_section = "key_points"
            elif line.startswith("**数据洞察**"):
                current_section = "insights"
            elif line.startswith("- ") and current_section:
                if current_section == "key_points":
                    structured_summary["key_points"].append(line[2:])
                elif current_section == "insights":
                    structured_summary["insights"].append(line[2:])
        
        return structured_summary
    
    def _fallback_summary(
        self,
        original_query: str,
        sql_query: str,
        query_result: Dict[str, Any],
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """回退总结方法，当DeepSeek不可用时使用"""
        
        # 提取查询结果数据
        result_data = []
        if "results" in query_result and query_result["results"]:
            result_data = query_result["results"]
        elif "data" in query_result and query_result["data"]:
            result_data = query_result["data"]
        
        # 计算总记录数
        total_records = len(result_data)
        
        # 构建基本总结
        summary_text = f"""**{query_type or '数据'}查询结果**

**总记录数**: {total_records}

**查询说明**: 已执行{query_type or '数据'}查询，共找到{total_records}条记录。

**详细数据**:
{self._format_data_as_table(result_data[:10])}
"""
        
        structured_summary = {
            "total_records": total_records,
            "summary_text": summary_text,
            "key_points": [f"共找到{total_records}条记录"],
            "insights": []
        }
        
        return {
            "success": True,
            "summary": summary_text,
            "structured_summary": structured_summary,
            "original_query": original_query,
            "sql_query": sql_query,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat(),
            "fallback": True  # 标记这是回退结果
        }
    
    def _format_data_as_table(self, data: List[Dict[str, Any]]) -> str:
        """将数据格式化为Markdown表格"""
        if not data:
            return "无数据"
        
        # 获取所有键
        keys = set()
        for item in data:
            keys.update(item.keys())
        
        # 排序键，确保常用字段在前
        key_order = ["uuid", "id", "name", "code", "created_at", "updated_at"]
        sorted_keys = []
        
        # 先添加有序键
        for key in key_order:
            if key in keys:
                sorted_keys.append(key)
                keys.remove(key)
        
        # 添加剩余键
        sorted_keys.extend(list(keys))
        
        # 构建表格
        table_lines = []
        
        # 表头
        header = "| " + " | ".join(sorted_keys) + " |"
        table_lines.append(header)
        
        # 分隔符
        separator = "| " + " | ".join(["---"] * len(sorted_keys)) + " |"
        table_lines.append(separator)
        
        # 数据行
        for item in data:
            row = []
            for key in sorted_keys:
                value = item.get(key, "")
                # 处理长文本
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                row.append(str(value))
            
            table_lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(table_lines)


# 全局服务实例
_summary_services = {}


def get_data_summary_service(workspace_id: str = "default", db: Optional[AsyncSession] = None) -> DataSummaryService:
    """获取数据总结服务实例"""
    if workspace_id not in _summary_services:
        _summary_services[workspace_id] = DataSummaryService(workspace_id, db)
    return _summary_services[workspace_id]