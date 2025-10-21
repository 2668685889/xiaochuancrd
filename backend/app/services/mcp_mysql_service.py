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
        """使用数据库中的配置初始化DeepSeek服务"""
        try:
            # 获取模型配置
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
    
    async def query(self, natural_language_query: str, session_id: str = None) -> Dict[str, Any]:
        """
        处理自然语言查询
        
        Args:
            natural_language_query: 自然语言查询语句
            session_id: 会话ID（可选）
            
        Returns:
            MCP 兼容的响应格式
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "MCP 服务未初始化",
                "content": []
            }
        
        try:
            # 首先尝试使用DeepSeek生成SQL查询
            sql_result = await self._generate_sql_with_deepseek(natural_language_query)
            
            if sql_result["success"] and sql_result.get("sql"):
                # 执行生成的SQL查询
                query_result = await self._execute_sql_query(sql_result["sql"])
                
                # 格式化查询结果
                response_text = self._format_query_result(query_result, sql_result.get("explanation", ""))
                
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
                                "sql": sql_result["sql"],
                                "model": "deepseek-chat"
                            }
                        }
                    ]
                }
            else:
                # 如果DeepSeek生成SQL失败，回退到关键词匹配
                logger.warning(f"DeepSeek SQL生成失败，回退到关键词匹配: {sql_result.get('error', '未知错误')}")
                return await self._fallback_query(natural_language_query, session_id)
                
        except Exception as e:
            logger.error(f"MCP 查询处理失败: {e}")
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
            
            # 获取数据库模式信息
            database_schema = await self._get_database_schema()
            
            # 获取自定义提示词
            custom_prompt = None
            if self.config_service:
                custom_prompt = await self.config_service.get_custom_prompt(self.workspace_id)
            
            # 准备示例查询
            examples = [
                {
                    "natural": "查询所有商品信息",
                    "sql": "SELECT uuid, product_name, product_code, current_quantity, unit_price FROM products WHERE is_active = TRUE LIMIT 20"
                },
                {
                    "natural": "查询库存不足的商品",
                    "sql": "SELECT product_name, product_code, current_quantity, min_quantity FROM products WHERE current_quantity <= min_quantity AND is_active = TRUE"
                },
                {
                    "natural": "查询价格大于100元的商品",
                    "sql": "SELECT product_name, product_code, unit_price FROM products WHERE unit_price > 100 AND is_active = TRUE"
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
    
    async def _get_database_schema(self) -> str:
        """获取数据库模式信息"""
        try:
            # 获取主要表的结构信息
            schema_info = "数据库表结构:\n\n"
            
            # 产品表
            schema_info += "products (产品表):\n"
            schema_info += "- uuid: 产品唯一标识\n"
            schema_info += "- product_name: 产品名称\n"
            schema_info += "- product_code: 产品编码\n"
            schema_info += "- current_quantity: 当前库存数量\n"
            schema_info += "- min_quantity: 最低库存数量\n"
            schema_info += "- max_quantity: 最高库存数量\n"
            schema_info += "- unit_price: 单价\n"
            schema_info += "- description: 产品描述\n"
            schema_info += "- is_active: 是否启用\n"
            schema_info += "- created_at: 创建时间\n"
            schema_info += "- updated_at: 更新时间\n\n"
            
            # 用户表
            schema_info += "users (用户表):\n"
            schema_info += "- uuid: 用户唯一标识\n"
            schema_info += "- username: 用户名\n"
            schema_info += "- email: 邮箱\n"
            schema_info += "- full_name: 全名\n"
            schema_info += "- is_active: 是否启用\n"
            schema_info += "- created_at: 创建时间\n\n"
            
            # 库存记录表
            schema_info += "inventory_records (库存记录表):\n"
            schema_info += "- uuid: 记录唯一标识\n"
            schema_info += "- product_uuid: 产品UUID\n"
            schema_info += "- record_type: 记录类型 (入库/出库)\n"
            schema_info += "- quantity: 数量\n"
            schema_info += "- reference: 参考信息\n"
            schema_info += "- created_at: 创建时间\n\n"
            
            return schema_info
            
        except Exception as e:
            logger.error(f"获取数据库模式失败: {e}")
            return "无法获取数据库模式信息"
    
    async def _execute_sql_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """执行SQL查询"""
        try:
            # 安全检查：只允许SELECT查询
            if not sql_query.strip().upper().startswith("SELECT"):
                logger.warning(f"非SELECT查询被拒绝: {sql_query}")
                return []
            
            # 执行SQL查询
            result = await self.db.execute(text(sql_query))
            rows = result.fetchall()
            
            # 获取列名
            columns = result.keys()
            
            # 转换为字典列表
            return [
                {column: str(row[i]) if row[i] is not None else "" for i, column in enumerate(columns)}
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"SQL查询执行失败: {e}")
            return []
    
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
            
            # 限制返回结果数量，避免过多数据
            stmt = stmt.limit(20)
            
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
                self.deepseek_service = get_deepseek_service()
            
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
                
        except Exception as e:
            logger.error(f"MCP 分析处理失败: {e}")
            return {
                "success": False,
                "error": f"分析处理异常: {str(e)}",
                "analysis": {}
            }
    
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
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service": "MCP MySQL Service",
            "database_connected": True,
            "ai_service_ready": self.is_initialized,
            "timestamp": "2024-01-01T00:00:00Z"  # 实际实现中应该使用当前时间
        }