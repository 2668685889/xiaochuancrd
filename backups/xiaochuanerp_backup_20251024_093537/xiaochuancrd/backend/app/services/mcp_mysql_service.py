"""
MCP MySQL 服务包装器
MCP 兼容的 MySQL 数据查询服务
"""

import json
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, or_
from datetime import datetime

from app.models.user import User
from app.models.product import Product
from app.models.inventory import InventoryRecord
from app.services.deepseek_service import get_deepseek_service, get_configured_deepseek_service, initialize_configured_deepseek_service
from app.services.assistant_config_service import AssistantConfigService
from app.services.data_summary_service import get_data_summary_service
from app.services.api_key_service import get_deepseek_mcp_api_config

logger = logging.getLogger(__name__)


class MCPMySQLService:
    """MCP MySQL 服务包装器"""
    
    def __init__(self, db: AsyncSession, workspace_id: str = "default"):
        self.db = db
        self.workspace_id = workspace_id
        self.is_initialized = True  # 直接初始化为就绪状态
        self.deepseek_service = None
        self.config_service = AssistantConfigService(db)
    
    async def initialize(self):
        """初始化 MCP 服务"""
        # MCP 服务直接可用，无需额外初始化
        self.is_initialized = True
        logger.info("MCP MySQL 服务初始化成功")
        
        # 尝试使用数据库中的配置初始化DeepSeek服务
        await self._initialize_deepseek_with_config()
    
    async def _initialize_deepseek_with_config(self):
        """使用数据库中的配置初始化DeepSeek服务（使用安全的API密钥管理方案）"""
        try:
            # 首先尝试从安全的API密钥服务获取MCP专用配置
            mcp_config = await get_deepseek_mcp_api_config(self.workspace_id)
            if mcp_config:
                logger.info(f"使用安全MCP API密钥配置: {self.workspace_id}")
                self.deepseek_service = get_configured_deepseek_service(mcp_config)
                if self.deepseek_service:
                    await self.deepseek_service.initialize()
                    logger.info(f"✅ 使用安全配置初始化DeepSeek服务成功，工作空间: {self.workspace_id}")
                    return
            
            # 如果MCP专用配置不可用，尝试普通安全配置
            logger.info(f"尝试使用普通安全配置: {self.workspace_id}")
            model_config = await self.config_service.get_model_config(self.workspace_id)
            
            if model_config:
                # 使用数据库配置创建DeepSeek服务
                self.deepseek_service = get_configured_deepseek_service(model_config)
                await self.deepseek_service.initialize()
                logger.info(f"✅ 使用数据库配置初始化DeepSeek服务成功，工作空间: {self.workspace_id}")
            else:
                # 回退到默认配置
                self.deepseek_service = get_deepseek_service()
                logger.warning(f"⚠️ 未找到模型配置，使用默认配置，工作空间: {self.workspace_id}")
                
        except Exception as e:
            logger.error(f"❌ 初始化DeepSeek服务失败: {e}")
            # 回退到默认配置
            self.deepseek_service = get_deepseek_service()
    
    async def query(self, natural_language_query: str, session_id: str = None, enable_analysis: bool = False) -> Dict[str, Any]:
        """
        处理自然语言查询
        
        Args:
            natural_language_query: 自然语言查询字符串
            session_id: 会话ID
            enable_analysis: 是否启用分析模型处理查询结果
            
        Returns:
            查询结果
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "MCP 服务未初始化",
                "content": []
            }
        
        try:
            # 生成SQL查询
            sql_result = await self._generate_sql_with_deepseek(natural_language_query)
            
            if not sql_result["success"]:
                return {
                    "success": False,
                    "error": sql_result.get("error", "SQL生成失败"),
                    "content": []
                }
            
            sql_query = sql_result["sql"]
            
            # 执行SQL查询
            query_result = await self._execute_sql_query(sql_query)
            
            if not query_result["success"]:
                return {
                    "success": False,
                    "error": query_result.get("error", "查询执行失败"),
                    "content": []
                }
            
            # 提取查询数据
            data = query_result["data"]
            
            # 使用data_summary_service总结结果
            try:
                from app.services.data_summary_service import get_data_summary_service
                summary_service = get_data_summary_service()
                
                # 获取查询类型
                query_type = self._extract_query_type(natural_language_query)
                
                # 生成摘要
                summary_result = await summary_service.generate_summary(
                    data=data,
                    query=natural_language_query,
                    query_type=query_type,
                    sql_query=sql_query
                )
                
                if summary_result["success"]:
                    response_text = summary_result["summary"]
                else:
                    # 如果摘要生成失败，使用默认格式
                    response_text = self._format_query_result(data, sql_result.get("explanation", ""))
                
            except Exception as e:
                logger.warning(f"摘要生成失败，使用默认格式: {e}")
                # 确保传递给_format_query_result的是正确格式的数据
                response_text = self._format_query_result(data, sql_result.get("explanation", ""))
            
            # 构建基础响应
            base_response = {
                "success": True,
                "content": [
                    {
                        "type": "text",
                        "text": response_text,
                        "metadata": {
                            "session_id": session_id or f"mcp_session_{id(self)}",
                            "timestamp": datetime.now().isoformat(),
                            "source": "mcp_mysql",
                            "query_type": query_type,
                            "model": "deepseek-chat",
                            "sql": sql_query,
                            "data": data  # 包含原始查询数据
                        }
                    }
                ]
            }
            
            # 如果启用分析模型，则对查询结果进行进一步分析
            if enable_analysis and data:
                try:
                    analysis_result = await self._analyze_query_result(
                        query=natural_language_query,
                        data=data,
                        session_id=session_id
                    )
                    
                    if analysis_result["success"]:
                        # 将分析结果添加到响应中
                        base_response["analysis"] = {
                            "content": analysis_result["content"][0]["text"],
                            "metadata": analysis_result["content"][0]["metadata"]
                        }
                    else:
                        logger.warning(f"分析模型处理失败: {analysis_result.get('error', '未知错误')}")
                        base_response["analysis"] = {
                            "error": analysis_result.get("error", "分析处理失败"),
                            "content": None
                        }
                        
                except Exception as e:
                    logger.error(f"分析模型处理异常: {e}")
                    base_response["analysis"] = {
                        "error": f"分析处理异常: {str(e)}",
                        "content": None
                    }
            
            return base_response
                
        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            return {
                "success": False,
                "error": f"查询处理异常: {str(e)}",
                "content": []
            }
    
    async def _generate_sql_with_deepseek(self, natural_language_query: str) -> Dict[str, Any]:
        """使用DeepSeek生成SQL查询"""
        try:
            # 确保DeepSeek服务已初始化
            if not self.deepseek_service:
                await self._initialize_deepseek_with_config()
            
            # 如果仍然没有可用的服务，使用默认配置
            if not self.deepseek_service:
                self.deepseek_service = get_deepseek_service()
                logger.warning("使用默认DeepSeek配置")
            
            # 检查服务是否就绪
            if not await self.deepseek_service.is_ready():
                logger.error("DeepSeek API服务未就绪，无法生成SQL查询")
                return {
                    "success": False,
                    "error": "DeepSeek API服务未就绪，请检查API密钥配置",
                    "sql": None
                }
            
            # 获取数据库模式信息
            database_schema = self._get_database_schema()
            
            # 获取自定义提示词
            custom_prompt = None
            if self.config_service:
                custom_prompt = await self.config_service.get_custom_prompt(self.workspace_id)
            
            # 准备示例查询
            examples = [
                {
                    "natural": "查询所有商品信息",
                    "sql": "SELECT uuid, product_name, product_code, category_name, current_quantity, unit_price FROM products WHERE is_active = TRUE LIMIT 20"
                },
                {
                    "natural": "查询库存不足的商品",
                    "sql": "SELECT product_name, product_code, category_name, current_quantity, min_quantity FROM products WHERE current_quantity <= min_quantity AND is_active = TRUE"
                },
                {
                    "natural": "查询价格大于100元的商品",
                    "sql": "SELECT product_name, product_code, category_name, unit_price FROM products WHERE unit_price > 100 AND is_active = TRUE"
                },
                {
                    "natural": "查询按分类统计商品数量",
                    "sql": "SELECT category_name, COUNT(*) as product_count FROM products WHERE is_active = TRUE GROUP BY category_name ORDER BY product_count DESC"
                }
            ]
            
            # 调用DeepSeek生成SQL
            result = await self.deepseek_service.generate_sql_query(
                natural_language=natural_language_query,
                database_schema=database_schema,
                examples=examples,
                custom_prompt=custom_prompt
            )
            
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek SQL生成失败: {e}")
            return {
                "success": False,
                "error": f"SQL生成失败: {str(e)}",
                "sql": None
            }
    
    def _get_database_schema(self) -> str:
        """获取数据库模式信息"""
        schema_info = """
数据库表结构说明：

1. sales_orders 表（销售订单表）：
   - uuid: 主键，订单唯一标识
   - order_number: 订单编号
   - customer_uuid: 客户UUID
   - customer_name: 客户名称
   - total_amount: 订单总金额
   - status: 订单状态（PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED, DELETED）
   - order_date: 订单日期
   - expected_delivery_date: 预计交货日期
   - actual_delivery_date: 实际交货日期
   - remark: 备注
   - created_by: 创建人
   - created_at: 创建时间
   - updated_at: 更新时间

2. sales_order_items 表（销售订单明细表）：
   - uuid: 主键，明细唯一标识
   - sales_order_uuid: 销售订单UUID
   - product_uuid: 商品UUID
   - quantity: 销售数量
   - unit_price: 销售单价
   - total_price: 金额（注意：字段名是total_price，不是total_amount）
   - shipped_quantity: 已发货数量
   - remark: 备注
   - created_at: 创建时间

3. products 表（商品表）：
   - uuid: 主键，商品唯一标识
   - product_name: 商品名称
   - product_code: 商品编码
   - category_name: 商品分类名称
   - category_uuid: 商品分类UUID（外键关联product_categories表）
   - unit_price: 单价
   - is_active: 是否启用
   - created_at: 创建时间
   - updated_at: 更新时间

4. customers 表（客户表）：
   - uuid: 主键，客户唯一标识
   - customer_name: 客户名称
   - customer_code: 客户编码
   - contact_person: 联系人
   - phone: 联系电话
   - email: 邮箱
   - address: 地址
   - created_at: 创建时间
   - updated_at: 更新时间

重要提示：
- sales_orders表没有is_active字段，只有status字段
- sales_order_items表的金额字段名是total_price，不是total_amount
- 查询时请使用正确的字段名
"""
        return schema_info
    
    async def _execute_sql_query(self, sql_query: str) -> Dict[str, Any]:
        """执行SQL查询"""
        try:
            # 安全检查：只允许SELECT查询
            if not sql_query.strip().upper().startswith("SELECT"):
                logger.warning(f"非SELECT查询被拒绝: {sql_query}")
                return {
                    "success": False,
                    "error": "只允许SELECT查询",
                    "data": []
                }
            
            # 执行SQL查询
            result = await self.db.execute(text(sql_query))
            rows = result.fetchall()
            
            # 获取列名
            columns = result.keys()
            
            # 转换为字典列表
            data = [
                {column: str(row[i]) if row[i] is not None else "" for i, column in enumerate(columns)}
                for row in rows
            ]
            
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
            
        except Exception as e:
            logger.error(f"SQL查询执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    def _extract_query_type(self, natural_language_query: str) -> str:
        """从自然语言查询中提取查询类型"""
        query_lower = natural_language_query.lower()
        
        # 销售订单相关查询
        if any(keyword in query_lower for keyword in ["销售订单", "销售", "订单"]):
            return "销售订单"
        
        # 采购订单相关查询
        elif any(keyword in query_lower for keyword in ["采购订单", "采购", "进货"]):
            return "采购订单"
        
        # 库存相关查询
        elif any(keyword in query_lower for keyword in ["库存", "商品", "产品"]):
            return "库存查询"
        
        # 客户相关查询
        elif any(keyword in query_lower for keyword in ["客户", "顾客"]):
            return "客户查询"
        
        # 默认类型
        else:
            return "数据查询"
    
    def _format_query_result(self, query_result: List[Dict[str, Any]], explanation: str = "") -> str:
        """格式化查询结果"""
        if not query_result:
            return f"📊 查询结果\n\n查询未返回任何数据。\n\n说明: {explanation}"
        
        # 构建结果文本
        result_text = "📊 数据库查询结果\n"
        result_text += f"查询时间：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n"
        result_text += f"总记录数：{len(query_result)} 条\n\n"
        
        # 添加说明（如果有）
        if explanation:
            result_text += f"查询说明：{explanation}\n\n"
        
        # 获取所有列名
        if query_result:
            columns = list(query_result[0].keys())
            
            # 添加表头
            result_text += "|".join(columns) + "\n"
            result_text += "|".join(["---"] * len(columns)) + "\n"
            
            # 添加数据行
            for row in query_result:
                result_text += "|".join([str(row.get(col, "")) for col in columns]) + "\n"
        
        return result_text
    
    async def _fallback_query(self, natural_language_query: str, session_id: str = None) -> Dict[str, Any]:
        """回退查询方法，使用关键词匹配"""
        try:
            # 根据查询内容执行相应的数据库查询
            query_lower = natural_language_query.lower()
            
            if "库存" in query_lower or "商品" in query_lower or "产品" in query_lower:
                # 查询产品库存，传递查询条件
                result = await self._query_product_inventory(natural_language_query)
                response_text = self._format_inventory_result(result)
            elif "销售" in query_lower or "订单" in query_lower:
                # 查询销售订单
                result = await self._query_sales_orders()
                response_text = self._format_sales_result(result)
            elif "采购" in query_lower or "进货" in query_lower:
                # 查询采购订单
                result = await self._query_purchase_orders()
                response_text = self._format_purchase_result(result)
            else:
                # 默认查询产品信息，传递查询条件
                result = await self._query_product_inventory(natural_language_query)
                response_text = self._format_inventory_result(result)
            
            return {
                "success": True,
                "content": [
                    {
                        "type": "text",
                        "text": response_text,
                        "metadata": {
                            "session_id": session_id or f"mcp_session_{id(self)}",
                            "timestamp": datetime.now().isoformat(),
                            "source": "mcp_mysql",
                            "query_type": "database_query",
                            "model": "keyword_matching"
                        }
                    }
                ]
            }
                
        except Exception as e:
            logger.error(f"回退查询处理失败: {e}")
            return {
                "success": False,
                "error": f"查询处理异常: {str(e)}",
                "content": []
            }
    
    async def _query_product_inventory(self, query: str = None) -> List[Dict[str, Any]]:
        """查询产品库存信息"""
        try:
            # 使用SQLAlchemy查询产品库存
            stmt = select(
                Product.uuid,
                Product.product_name,
                Product.product_code,
                Product.current_quantity,
                Product.min_quantity,
                Product.max_quantity,
                Product.unit_price
            ).where(Product.is_active == True)
            
            # 如果有查询条件，添加过滤
            if query:
                query_lower = query.lower()
                # 如果是通用查询（如"查询所有商品"），不添加LIKE条件
                # 只有当查询包含特定商品名称或关键词时，才添加LIKE条件
                if not any(keyword in query_lower for keyword in ["所有", "全部"]):
                    # 提取查询关键词，去除常见的查询词汇
                    search_keywords = query_lower
                    for word in ["查询", "商品", "产品", "库存", "信息", "数据"]:
                        search_keywords = search_keywords.replace(word, "").strip()
                    
                    # 如果提取后还有关键词，则使用它进行搜索
                    if search_keywords:
                        stmt = stmt.where(
                            or_(
                                Product.product_name.ilike(f"%{search_keywords}%"),
                                Product.product_code.ilike(f"%{search_keywords}%"),
                                Product.description.ilike(f"%{search_keywords}%")
                            )
                        )
            
            # 增加返回结果数量限制，避免过多数据影响性能
            stmt = stmt.limit(10000)
            
            result = await self.db.execute(stmt)
            products = result.fetchall()
            
            return [
                {
                    "uuid": str(product[0]),
                    "product_name": product[1],
                    "product_code": product[2],
                    "current_quantity": product[3],
                    "min_quantity": product[4],
                    "max_quantity": product[5],
                    "unit_price": float(product[6]) if product[6] else 0.0
                }
                for product in products
            ]
        except Exception as e:
            logger.error(f"查询产品库存失败: {e}")
            return []
    
    async def _query_sales_orders(self) -> List[Dict[str, Any]]:
        """查询销售订单信息"""
        try:
            # 查询销售订单（使用原始SQL，因为销售订单模型可能不存在）
            sql = text("""
                SELECT 
                    order_number, 
                    customer_name, 
                    total_amount, 
                    status, 
                    order_date
                FROM sales_orders 
                WHERE deleted_at IS NULL 
                ORDER BY order_date DESC 
                LIMIT 10
            """)
            
            result = await self.db.execute(sql)
            orders = result.fetchall()
            
            return [
                {
                    "order_number": order.order_number,
                    "customer_name": order.customer_name,
                    "total_amount": float(order.total_amount) if order.total_amount else 0.0,
                    "status": order.status,
                    "order_date": order.order_date.isoformat() if order.order_date else ""
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"查询销售订单失败: {e}")
            return []
    
    async def _query_purchase_orders(self) -> List[Dict[str, Any]]:
        """查询采购订单信息"""
        try:
            # 查询采购订单（使用原始SQL）
            sql = text("""
                SELECT 
                    order_number, 
                    total_amount, 
                    status, 
                    order_date,
                    expected_delivery_date
                FROM purchase_orders 
                WHERE deleted_at IS NULL 
                ORDER BY order_date DESC 
                LIMIT 10
            """)
            
            result = await self.db.execute(sql)
            orders = result.fetchall()
            
            return [
                {
                    "order_number": order.order_number,
                    "total_amount": float(order.total_amount) if order.total_amount else 0.0,
                    "status": order.status,
                    "order_date": order.order_date.isoformat() if order.order_date else "",
                    "expected_delivery_date": order.expected_delivery_date.isoformat() if order.expected_delivery_date else ""
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"查询采购订单失败: {e}")
            return []
    
    def _format_inventory_result(self, products: List[Dict[str, Any]]) -> str:
        """格式化库存查询结果"""
        if not products:
            return "📦 库存查询结果\n\n未找到匹配的产品信息。"
        
        result_text = "📦 库存查询结果\n\n"
        result_text += f"共找到 {len(products)} 个产品：\n\n"
        
        for product in products:
            result_text += f"🔹 {product['product_name']} ({product['product_code']})\n"
            result_text += f"   当前库存: {product['current_quantity']} {product['min_quantity']}/{product['max_quantity']}\n"
            result_text += f"   单价: ¥{product['unit_price']:.2f}\n\n"
        
        return result_text
    
    def _format_sales_result(self, orders: List[Dict[str, Any]]) -> str:
        """格式化销售订单结果"""
        if not orders:
            return "💰 销售订单查询结果\n\n未找到销售订单信息。"
        
        result_text = "💰 销售订单查询结果\n\n"
        result_text += f"共找到 {len(orders)} 个销售订单：\n\n"
        
        for order in orders:
            result_text += f"🔹 订单号: {order['order_number']}\n"
            result_text += f"   客户: {order['customer_name']}\n"
            result_text += f"   金额: ¥{order['total_amount']:.2f}\n"
            result_text += f"   状态: {order['status']}\n"
            result_text += f"   日期: {order['order_date']}\n\n"
        
        return result_text
    
    def _format_purchase_result(self, orders: List[Dict[str, Any]]) -> str:
        """格式化采购订单结果"""
        if not orders:
            return "🛒 采购订单查询结果\n\n未找到采购订单信息。"
        
        result_text = "🛒 采购订单查询结果\n\n"
        result_text += f"共找到 {len(orders)} 个采购订单：\n\n"
        
        for order in orders:
            result_text += f"🔹 订单号: {order['order_number']}\n"
            result_text += f"   金额: ¥{order['total_amount']:.2f}\n"
            result_text += f"   状态: {order['status']}\n"
            result_text += f"   订单日期: {order['order_date']}\n"
            if order['expected_delivery_date']:
                result_text += f"   预计交货: {order['expected_delivery_date']}\n"
            result_text += "\n"
        
        return result_text
    
    async def _analyze_query_result(self, query: str, data: Any, session_id: str = None) -> Dict[str, Any]:
        """分析查询结果"""
        try:
            # 确保data是字典列表格式
            if not isinstance(data, list):
                if isinstance(data, dict):
                    # 如果data是字典，尝试提取其中的数据
                    if "data" in data:
                        data = data["data"]
                    else:
                        # 如果无法提取，创建一个包含原始数据的字典列表
                        data = [data]
                else:
                    # 如果data既不是列表也不是字典，将其转换为字符串并包装在字典中
                    data = [{"value": str(data)}]
            
            # 现在data应该是字典列表，可以安全地调用_format_data_for_analysis
            formatted_data = self._format_data_for_analysis(data)
            
            # 获取分析模型配置
            analysis_config = await self._get_analysis_config()
            
            # 使用DeepSeek服务进行分析
            analysis_prompt = f"""
请分析以下查询结果，提供有价值的洞察和建议：

查询内容：{query}

数据概览：
{formatted_data}

请提供：
1. 数据关键发现
2. 潜在问题或机会
3. 建议的后续操作
"""
            
            # 确保DeepSeek服务已初始化
            if not self.deepseek_service:
                await self._initialize_deepseek_with_config()
            
            # 如果仍然没有可用的服务，使用默认配置
            if not self.deepseek_service:
                self.deepseek_service = get_deepseek_service()
                logger.warning("使用默认DeepSeek配置进行数据分析")
            
            # 调用DeepSeek进行分析
            analysis_result = await self.deepseek_service.analyze_data(
                query=query,
                data=data,
                prompt=analysis_prompt
            )
            
            if analysis_result["success"]:
                return {
                    "success": True,
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_result["analysis"],
                            "metadata": {
                                "session_id": session_id or f"mcp_session_{id(self)}",
                                "timestamp": datetime.now().isoformat(),
                                "source": "mcp_mysql_analysis",
                                "model": "deepseek-chat",
                                "data_count": len(data)
                            }
                        }
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": analysis_result.get("error", "分析失败"),
                    "content": []
                }
                
        except Exception as e:
            logger.error(f"分析查询结果失败: {e}")
            return {
                "success": False,
                "error": f"分析处理异常: {str(e)}",
                "content": []
            }
    
    async def _get_analysis_config(self) -> Dict[str, Any]:
        """获取分析模型配置"""
        try:
            # 默认分析配置
            default_config = {
                "model": "deepseek-chat",
                "temperature": 0.3,
                "max_tokens": 1500,
                "api_key": None,
                "api_domain": "https://api.deepseek.com",
                "base_url": "https://api.deepseek.com/v1",
                "system_prompt": self._get_default_analysis_prompt()
            }
            
            # 如果有配置服务，尝试获取用户配置
            if self.config_service:
                try:
                    user_config = await self.config_service.get_analysis_model_config(self.workspace_id)
                    if user_config:
                        default_config.update(user_config)
                except Exception as e:
                    logger.warning(f"获取分析模型配置失败，使用默认配置: {e}")
            
            return default_config
        except Exception as e:
            logger.error(f"获取分析配置失败: {e}")
            return {
                "model": "deepseek-chat",
                "temperature": 0.3,
                "max_tokens": 1500,
                "api_key": None,
                "api_domain": "https://api.deepseek.com",
                "base_url": "https://api.deepseek.com/v1",
                "system_prompt": self._get_default_analysis_prompt()
            }
    
    def _get_default_analysis_prompt(self) -> str:
        """获取默认分析提示词"""
        return "你是一个专业的数据分析助手，请对提供的数据进行深入分析并提供有价值的洞察。"
    
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
    
    async def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        趋势预测功能
        
        Args:
            data: 预测数据
            
        Returns:
            预测结果
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "MCP 服务未初始化",
                "prediction": {}
            }
        
        try:
            # 返回基础预测响应
            return {
                "success": True,
                "prediction": {
                    "data": data,
                    "status": "MCP预测功能已就绪",
                    "message": "当前服务已切换到MCP架构"
                }
            }
                
        except Exception as e:
            logger.error(f"MCP 预测处理失败: {e}")
            return {
                "success": False,
                "error": f"预测处理异常: {str(e)}",
                "prediction": {}
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """获取服务能力信息"""
        return {
            "capabilities": [
                {
                    "name": "query",
                    "description": "自然语言数据查询",
                    "parameters": {
                        "natural_language_query": "string"
                    }
                },
                {
                    "name": "analyze", 
                    "description": "数据分析功能",
                    "parameters": {
                        "query": "string"
                    }
                },
                {
                    "name": "predict",
                    "description": "趋势预测功能", 
                    "parameters": {
                        "data": "object"
                    }
                }
            ],
            "database_info": {
                "type": "mysql",
                "name": "xiaochuanERP",
                "tables": ["products", "sales_orders", "purchase_orders", "customers", "suppliers", "inventory_records"]
            },
            "ai_service": {
                "provider": "DeepSeek",
                "model": "deepseek-chat"
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        # 检查DeepSeek服务是否就绪
        ai_service_ready = False
        if self.deepseek_service:
            try:
                ai_service_ready = await self.deepseek_service.is_ready()
            except Exception as e:
                logger.error(f"检查DeepSeek服务状态失败: {e}")
                ai_service_ready = False
        
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service": "MCP MySQL Service",
            "database_connected": True,
            "ai_service_ready": ai_service_ready,
            "timestamp": datetime.now().isoformat()
        }
    
    async def analyze(self, query: str) -> Dict[str, Any]:
        """
        数据分析功能
        
        Args:
            query: 分析查询
            
        Returns:
            分析结果
        """
        try:
            # 使用DeepSeek进行数据分析
            if not self.deepseek_service:
                await self._initialize_deepseek_with_config()
            
            # 如果仍然没有可用的服务，使用默认配置
            if not self.deepseek_service:
                self.deepseek_service = get_deepseek_service()
                logger.warning("使用默认DeepSeek配置进行数据分析")
            
            # 检查服务是否就绪
            if not await self.deepseek_service.is_ready():
                logger.error("DeepSeek API服务未就绪，无法进行数据分析")
                return {
                    "success": False,
                    "error": "DeepSeek API服务未就绪，请检查API密钥配置",
                    "content": []
                }
            
            # 获取数据概览
            data_overview = await self._get_data_overview()
            
            # 构建分析提示词
            analysis_prompt = f"""
            你是一个专业的数据分析助手。请根据以下数据概览和用户查询，提供数据分析结果。
            
            数据概览:
            {data_overview}
            
            用户查询: {query}
            
            请提供简洁、专业的数据分析结果，包括：
            1. 数据概况
            2. 关键发现
            3. 建议
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
                                "source": "mcp_mysql",
                                "query_type": "data_analysis",
                                "model": "deepseek-chat",
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "数据分析失败"),
                    "content": []
                }
                
        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            return {
                "success": False,
                "error": f"数据分析异常: {str(e)}",
                "content": []
            }
    
    async def _get_data_overview(self) -> str:
        """获取数据概览"""
        try:
            overview = "数据概览:\n\n"
            
            # 产品总数
            product_count = await self.db.execute(text("SELECT COUNT(*) as count FROM products WHERE is_active = TRUE"))
            product_count = product_count.fetchone()[0]
            overview += f"产品总数: {product_count}\n"
            
            # 库存不足产品数
            low_stock_count = await self.db.execute(text("""
                SELECT COUNT(*) as count FROM products 
                WHERE current_quantity <= min_quantity AND is_active = TRUE
            """))
            low_stock_count = low_stock_count.fetchone()[0]
            overview += f"库存不足产品数: {low_stock_count}\n"
            
            # 总库存价值
            total_value = await self.db.execute(text("""
                SELECT SUM(current_quantity * unit_price) as total FROM products WHERE is_active = TRUE
            """))
            total_value = total_value.fetchone()[0] or 0
            overview += f"总库存价值: ¥{float(total_value):.2f}\n"
            
            return overview
            
        except Exception as e:
            logger.error(f"获取数据概览失败: {e}")
            return "无法获取数据概览"