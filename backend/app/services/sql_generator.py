"""
SQL生成引擎服务
将自然语言查询转换为SQL语句
"""
import json
import logging
import re
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


class SQLGenerator:
    """SQL生成引擎类"""
    
    def __init__(self, db: AsyncSession, assistant_prompt: str = "你是一个智能助手，请根据用户需求提供专业的帮助。"):
        self.db = db
        self.assistant_prompt = assistant_prompt
        self.database_schema = {}
        self.table_aliases = {
            '产品': 'products',
            '商品': 'products',
            '销售': 'sales_orders',
            '订单': 'sales_orders',
            '采购': 'purchase_orders',
            '供应商': 'suppliers',
            '客户': 'customers',
            '库存': 'inventory_records',
            '用户': 'customers',
            '分类': 'product_categories'
        }
    
    def set_assistant_prompt(self, assistant_prompt: str):
        """设置助手提示词"""
        self.assistant_prompt = assistant_prompt
        
    async def initialize(self):
        """初始化SQL生成器，获取数据库表结构"""
        try:
            await self._load_database_schema()
            logger.info("SQL生成器初始化完成")
        except Exception as e:
            logger.error(f"SQL生成器初始化失败: {e}")
    
    async def _load_database_schema(self):
        """加载数据库表结构信息"""
        try:
            # 获取所有表名
            result = await self.db.execute(text("""
                SELECT TABLE_NAME, TABLE_COMMENT 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'xiaochuanerp'
            """))
            
            tables = result.fetchall()
            
            for table in tables:
                table_name = table[0]
                table_comment = table[1] or table_name
                
                # 获取表字段信息
                columns_result = await self.db.execute(text(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'xiaochuanerp' AND TABLE_NAME = '{table_name}'
                """))
                
                columns = columns_result.fetchall()
                
                self.database_schema[table_name] = {
                    'name': table_name,
                    'comment': table_comment,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'comment': col[2] or col[0]
                        }
                        for col in columns
                    ]
                }
                
        except Exception as e:
            logger.error(f"加载数据库表结构失败: {e}")
            # 如果无法获取真实表结构，使用默认表结构
            self._load_default_schema()
    
    def _load_default_schema(self):
        """加载默认表结构（备用方案）"""
        self.database_schema = {
            'products': {
                'name': 'products',
                'comment': '产品表',
                'columns': [
                    {'name': 'uuid', 'type': 'char(36)', 'comment': '产品UUID'},
                    {'name': 'product_code', 'type': 'varchar(50)', 'comment': '产品编码'},
                    {'name': 'product_name', 'type': 'varchar(100)', 'comment': '产品名称'},
                    {'name': 'category_uuid', 'type': 'char(36)', 'comment': '分类UUID'},
                    {'name': 'category_name', 'type': 'varchar(50)', 'comment': '分类名称'},
                    {'name': 'unit_price', 'type': 'decimal', 'comment': '单价'},
                    {'name': 'stock_quantity', 'type': 'int', 'comment': '库存数量'},
                    {'name': 'min_stock', 'type': 'int', 'comment': '最小库存'},
                    {'name': 'max_stock', 'type': 'int', 'comment': '最大库存'},
                    {'name': 'description', 'type': 'text', 'comment': '产品描述'},
                    {'name': 'status', 'type': 'varchar', 'comment': '产品状态'},
                    {'name': 'created_by', 'type': 'char(36)', 'comment': '创建人'},
                    {'name': 'created_at', 'type': 'datetime', 'comment': '创建时间'},
                    {'name': 'updated_at', 'type': 'datetime', 'comment': '更新时间'}
                ]
            },
            'sales_orders': {
                'name': 'sales_orders',
                'comment': '销售订单表',
                'columns': [
                    {'name': 'uuid', 'type': 'char(36)', 'comment': '订单UUID'},
                    {'name': 'order_number', 'type': 'varchar(50)', 'comment': '订单编号'},
                    {'name': 'customer_uuid', 'type': 'char(36)', 'comment': '客户UUID'},
                    {'name': 'customer_name', 'type': 'varchar(100)', 'comment': '客户名称'},
                    {'name': 'customer_phone', 'type': 'varchar(20)', 'comment': '客户电话'},
                    {'name': 'customer_address', 'type': 'varchar(200)', 'comment': '客户地址'},
                    {'name': 'total_amount', 'type': 'decimal', 'comment': '总金额'},
                    {'name': 'status', 'type': 'varchar', 'comment': '订单状态'},
                    {'name': 'order_date', 'type': 'date', 'comment': '订单日期'},
                    {'name': 'expected_delivery_date', 'type': 'date', 'comment': '预计交货日期'},
                    {'name': 'actual_delivery_date', 'type': 'date', 'comment': '实际交货日期'},
                    {'name': 'remark', 'type': 'text', 'comment': '备注'},
                    {'name': 'created_by', 'type': 'char(36)', 'comment': '创建人'},
                    {'name': 'created_at', 'type': 'datetime', 'comment': '创建时间'},
                    {'name': 'updated_at', 'type': 'datetime', 'comment': '更新时间'}
                ]
            },
            'purchase_orders': {
                'name': 'purchase_orders',
                'comment': '采购订单表',
                'columns': [
                    {'name': 'id', 'type': 'int', 'comment': '采购ID'},
                    {'name': 'supplier_id', 'type': 'int', 'comment': '供应商ID'},
                    {'name': 'product_id', 'type': 'int', 'comment': '产品ID'},
                    {'name': 'quantity', 'type': 'int', 'comment': '数量'},
                    {'name': 'unit_price', 'type': 'decimal', 'comment': '单价'},
                    {'name': 'total_amount', 'type': 'decimal', 'comment': '总金额'},
                    {'name': 'order_date', 'type': 'datetime', 'comment': '订单日期'},
                    {'name': 'status', 'type': 'varchar', 'comment': '订单状态'}
                ]
            },
            'customers': {
                'name': 'customers',
                'comment': '客户表',
                'columns': [
                    {'name': 'uuid', 'type': 'char(36)', 'comment': '客户UUID'},
                    {'name': 'customer_code', 'type': 'varchar(50)', 'comment': '客户编码'},
                    {'name': 'customer_name', 'type': 'varchar(100)', 'comment': '客户名称'},
                    {'name': 'contact_person', 'type': 'varchar(50)', 'comment': '联系人'},
                    {'name': 'phone', 'type': 'varchar(20)', 'comment': '联系电话'},
                    {'name': 'email', 'type': 'varchar(100)', 'comment': '邮箱'},
                    {'name': 'address', 'type': 'varchar(200)', 'comment': '地址'},
                    {'name': 'customer_type', 'type': 'varchar(20)', 'comment': '客户类型'},
                    {'name': 'status', 'type': 'varchar', 'comment': '客户状态'},
                    {'name': 'remark', 'type': 'text', 'comment': '备注'},
                    {'name': 'created_by', 'type': 'char(36)', 'comment': '创建人'},
                    {'name': 'created_at', 'type': 'datetime', 'comment': '创建时间'},
                    {'name': 'updated_at', 'type': 'datetime', 'comment': '更新时间'}
                ]
            },
            'suppliers': {
                'name': 'suppliers',
                'comment': '供应商表',
                'columns': [
                    {'name': 'id', 'type': 'int', 'comment': '供应商ID'},
                    {'name': 'name', 'type': 'varchar', 'comment': '供应商名称'},
                    {'name': 'contact', 'type': 'varchar', 'comment': '联系方式'},
                    {'name': 'address', 'type': 'varchar', 'comment': '地址'}
                ]
            },
            'inventory_records': {
                'name': 'inventory_records',
                'comment': '库存记录表',
                'columns': [
                    {'name': 'id', 'type': 'int', 'comment': '库存记录ID'},
                    {'name': 'product_id', 'type': 'int', 'comment': '产品ID'},
                    {'name': 'quantity', 'type': 'int', 'comment': '库存数量'},
                    {'name': 'min_quantity', 'type': 'int', 'comment': '最小库存量'},
                    {'name': 'max_quantity', 'type': 'int', 'comment': '最大库存量'},
                    {'name': 'updated_at', 'type': 'datetime', 'comment': '更新时间'}
                ]
            }
        }
    
    async def generate_sql(self, natural_language_query: str) -> Dict[str, Any]:
        """
        将自然语言查询转换为SQL语句
        
        Args:
            natural_language_query: 自然语言查询
            
        Returns:
            包含SQL语句和元数据的字典
        """
        try:
            # 使用LLM生成SQL（基于实际数据库schema）
            sql_query = await self._generate_sql_with_llm(natural_language_query)
            
            if sql_query:
                # 验证SQL语法
                is_valid = await self._validate_sql(sql_query)
                
                return {
                    'success': True,
                    'sql_query': sql_query,
                    'intent': 'llm_generated',
                    'parameters': {},
                    'is_valid': is_valid,
                    'explanation': '使用LLM基于数据库schema生成的SQL查询'
                }
            else:
                # 如果LLM生成失败，回退到规则引擎
                return await self._generate_sql_with_rules(natural_language_query)
            
        except Exception as e:
            logger.error(f"SQL生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'sql_query': None,
                'intent': 'unknown',
                'parameters': {},
                'is_valid': False,
                'explanation': '无法生成有效的SQL查询'
            }
    
    async def _generate_sql_with_llm(self, query: str) -> str:
        """使用LLM基于数据库schema生成SQL"""
        try:
            # 智能识别用户查询中可能涉及的表
            suggested_tables = self._suggest_tables_for_query(query)
            
            # 构建简洁的schema提示词（只包含相关表）
            schema_prompt = self._build_focused_schema_prompt(suggested_tables)
            
            # 构建完整的提示词
            table_suggestions = "、".join(suggested_tables) if suggested_tables else "请根据查询内容选择合适的表"
            
            full_prompt = f"""
{self.assistant_prompt}

请根据以下数据库表结构和用户查询生成准确的SQL语句。

数据库表结构（仅显示相关表）：
{schema_prompt}

用户查询："{query}"

重要指令：
1. **必须使用数据库中的实际表名和字段名**，不要使用通用名称
2. **根据查询内容，必须使用以下表：{table_suggestions}**
3. **特别注意：数据库中不存在名为 'sales' 的表**，销售数据存储在 sales_orders 和 sales_order_items 表中
4. 如果查询涉及销售数据，必须使用 sales_orders 表
5. **绝对禁止使用以下不存在的表名：sales, sale, 销售表, 销售数据表**
6. **只能使用以下实际存在的表名：sales_orders, sales_order_items, products, customers, suppliers, purchase_orders, inventory_records, users**
7. **字段名必须完全匹配数据库中的实际字段名**：
   - sales_orders表的主键是uuid，不是id或order_id
   - sales_orders表的客户字段是customer_uuid，不是customer_id
   - sales_orders表的状态字段是status，不是order_status
   - 所有表的主键都是uuid字段，不是id字段

请生成标准的MySQL SQL查询语句，只返回SQL代码，不要解释。
确保使用正确的表名和字段名。

示例：
- 如果查询销售数据，使用：SELECT uuid, order_number, customer_uuid, total_amount, status FROM sales_orders WHERE ...
- 不要使用：SELECT id, order_number, customer_id, total_amount, order_status FROM sales_orders WHERE ...
"""
            
            # 调用LLM生成SQL（当前版本暂不支持AI功能）
            # TODO: 集成新的AI服务
            return None
            
        except Exception as e:
            logger.error(f"LLM SQL生成失败: {e}")
            return None
    
    def _build_schema_prompt(self) -> str:
        """构建数据库schema提示词"""
        schema_prompt = []
        
        for table_name, table_info in self.database_schema.items():
            table_desc = f"表名: {table_name}"
            if table_info.get('comment'):
                table_desc += f" ({table_info['comment']})"
            
            columns_desc = []
            for column in table_info.get('columns', []):
                col_desc = f"  - {column['name']} ({column['type']})"
                if column.get('comment'):
                    col_desc += f" - {column['comment']}"
                columns_desc.append(col_desc)
            
            schema_prompt.append(table_desc)
            schema_prompt.extend(columns_desc)
            schema_prompt.append("")
        
        return '\n'.join(schema_prompt)
    
    def _suggest_tables_for_query(self, query: str) -> List[str]:
        """根据用户查询智能推荐相关表名"""
        suggested_tables = []
        
        # 扩展的关键词到表名映射（包含同义词和业务术语）
        keyword_to_table = {
            # 销售相关（扩展同义词）
            "销售": ["sales_orders", "sales_order_items"],
            "销量": ["sales_orders", "sales_order_items"],
            "销售额": ["sales_orders", "sales_order_items"],
            "营业额": ["sales_orders", "sales_order_items"],
            "业绩": ["sales_orders", "sales_order_items"],
            "收入": ["sales_orders", "sales_order_items"],
            
            # 订单相关
            "订单": ["sales_orders", "sales_order_items"],
            "订购": ["sales_orders", "sales_order_items"],
            "下单": ["sales_orders", "sales_order_items"],
            
            # 客户相关
            "客户": ["customers"],
            "顾客": ["customers"],
            "买家": ["customers"],
            "用户": ["customers", "users"],
            
            # 产品相关
            "产品": ["products"],
            "商品": ["products"],
            "货品": ["products"],
            "物品": ["products"],
            
            # 库存相关
            "库存": ["inventory"],
            "存货": ["inventory"],
            "仓储": ["inventory"],
            "现货": ["inventory"],
            
            # 采购相关
            "采购": ["purchase_orders"],
            "进货": ["purchase_orders"],
            "购入": ["purchase_orders"],
            
            # 供应商相关
            "供应商": ["suppliers"],
            "供货商": ["suppliers"],
            "厂商": ["suppliers"],
            
            # 用户管理相关
            "管理员": ["users"],
            "员工": ["users"],
            "人员": ["users"],
            
            # 统计分析相关
            "统计": ["sales_orders", "purchase_orders", "inventory", "products"],
            "分析": ["sales_orders", "purchase_orders", "inventory", "products"],
            "报表": ["sales_orders", "purchase_orders", "inventory", "products"],
            "数据": ["sales_orders", "purchase_orders", "inventory", "products"],
            
            # 查询相关
            "查询": ["sales_orders", "purchase_orders", "products", "customers"],
            "查找": ["sales_orders", "purchase_orders", "products", "customers"],
            "搜索": ["sales_orders", "purchase_orders", "products", "customers"]
        }
        
        # 智能匹配：检查查询中的关键词（包含模糊匹配）
        query_lower = query.lower()
        
        for keyword, tables in keyword_to_table.items():
            # 精确匹配
            if keyword in query_lower:
                suggested_tables.extend(tables)
            # 模糊匹配：检查是否包含关键词的部分字符
            elif len(keyword) > 2 and any(char in query_lower for char in keyword):
                # 为模糊匹配的表赋予较低权重（通过重复添加实现）
                suggested_tables.extend(tables)
        
        # 去重
        suggested_tables = list(set(suggested_tables))
        
        # 如果没有任何匹配，使用基于词频的智能推荐
        if not suggested_tables:
            suggested_tables = self._intelligent_fallback(query_lower)
        
        # 应用增强推荐逻辑
        suggested_tables = self._enhance_table_recommendation(query_lower, suggested_tables)
        
        return suggested_tables
    
    def _intelligent_fallback(self, query: str) -> List[str]:
        """智能回退机制：基于查询内容分析推荐表"""
        # 分析查询中的业务关键词
        business_keywords = {
            '销售': ['sales_orders', 'sales_order_items'],
            '产品': ['products'],
            '客户': ['customers'],
            '库存': ['inventory'],
            '采购': ['purchase_orders'],
            '供应商': ['suppliers'],
            '用户': ['users']
        }
        
        # 检查是否包含业务领域关键词
        for domain, tables in business_keywords.items():
            if domain in query:
                return tables
        
        # 基于查询长度的智能推荐
        if len(query) > 20:  # 长查询通常需要多个表
            return ["sales_orders", "products", "customers", "sales_order_items"]
        elif len(query) > 10:  # 中等长度查询
            return ["sales_orders", "products", "customers"]
        else:  # 短查询
            return ["sales_orders", "products"]
    
    def _enhance_table_recommendation(self, query: str, initial_tables: List[str]) -> List[str]:
        """增强表推荐：基于查询复杂度调整推荐结果"""
        enhanced_tables = initial_tables.copy()
        
        # 如果查询包含时间相关词汇，确保包含时间字段的表
        time_keywords = ['最近', '本周', '本月', '今年', '日期', '时间', '天', '周', '月', '年']
        if any(keyword in query for keyword in time_keywords):
            if 'sales_orders' not in enhanced_tables:
                enhanced_tables.append('sales_orders')
        
        # 如果查询包含金额相关词汇，确保包含金额字段的表
        amount_keywords = ['金额', '价格', '费用', '成本', '总额', '单价']
        if any(keyword in query for keyword in amount_keywords):
            if 'sales_orders' not in enhanced_tables:
                enhanced_tables.append('sales_orders')
            if 'products' not in enhanced_tables:
                enhanced_tables.append('products')
        
        # 如果查询包含统计相关词汇，确保包含相关统计表
        stat_keywords = ['统计', '总数', '平均', '最大', '最小', '汇总']
        if any(keyword in query for keyword in stat_keywords):
            # 统计查询通常需要主表和关联表
            if 'sales_orders' not in enhanced_tables:
                enhanced_tables.append('sales_orders')
            if 'sales_order_items' not in enhanced_tables:
                enhanced_tables.append('sales_order_items')
        
        return list(set(enhanced_tables))
    
    def _build_focused_schema_prompt(self, table_names: List[str]) -> str:
        """构建只包含相关表的schema提示词"""
        if not table_names:
            return "无相关表信息"
        
        schema_prompt = ""
        
        for table_name in table_names:
            if table_name in self.database_schema:
                table_info = self.database_schema[table_name]
                schema_prompt += f"表名: {table_name}"
                
                if table_info.get('comment'):
                    schema_prompt += f" (注释: {table_info['comment']})"
                
                schema_prompt += "\n字段信息:\n"
                
                for column in table_info.get('columns', []):
                    schema_prompt += f"  - {column['name']} ({column['type']})"
                    if column.get('comment'):
                        schema_prompt += f" - {column['comment']}"
                    schema_prompt += "\n"
                
                schema_prompt += "\n"
        
        return schema_prompt
    
    def _extract_sql_from_response(self, response: str) -> str:
        """从LLM响应中提取SQL代码"""
        # 查找SQL代码块
        import re
        
        # 匹配```sql ... ```格式
        sql_block_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL)
        if sql_block_match:
            return sql_block_match.group(1).strip()
        
        # 匹配纯SQL语句（以SELECT/INSERT/UPDATE/DELETE开头）
        sql_match = re.search(r'(SELECT|INSERT|UPDATE|DELETE)\s+.*', response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return sql_match.group(0).strip()
        
        # 如果没有找到SQL，返回原始响应（可能是纯SQL）
        return response.strip()
    
    async def _generate_sql_with_rules(self, query: str) -> Dict[str, Any]:
        """使用规则引擎生成SQL（备用方案）"""
        try:
            # 分析查询意图
            intent = self._analyze_intent(query)
            
            # 提取查询参数
            params = self._extract_parameters(query, intent)
            
            # 生成SQL语句
            sql_query = self._build_sql_query(intent, params)
            
            # 验证SQL语法
            is_valid = await self._validate_sql(sql_query)
            
            return {
                'success': True,
                'sql_query': sql_query,
                'intent': intent,
                'parameters': params,
                'is_valid': is_valid,
                'explanation': self._generate_explanation(intent, params)
            }
            
        except Exception as e:
            logger.error(f"规则引擎SQL生成失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'sql_query': None,
                'intent': 'unknown',
                'parameters': {},
                'is_valid': False,
                'explanation': '无法生成有效的SQL查询'
            }
    
    def _analyze_intent(self, query: str) -> str:
        """分析查询意图"""
        query_lower = query.lower()
        
        # 统计查询
        if any(word in query_lower for word in ['统计', '总数', '数量', '多少', '几个']):
            return 'count'
        
        # 求和查询
        if any(word in query_lower for word in ['总和', '总计', '合计', '总金额', '总额']):
            return 'sum'
        
        # 平均查询
        if any(word in query_lower for word in ['平均', '平均值', '均价']):
            return 'avg'
        
        # 最大/最小查询
        if any(word in query_lower for word in ['最大', '最高', '最多', '最小', '最低', '最少']):
            return 'extreme'
        
        # 列表查询
        if any(word in query_lower for word in ['列表', '显示', '查看', '查询', '哪些']):
            return 'select'
        
        # 分组查询
        if any(word in query_lower for word in ['按', '分组', '分类', '类别']):
            return 'group_by'
        
        # 默认返回选择查询
        return 'select'
    
    def _extract_parameters(self, query: str, intent: str) -> Dict[str, Any]:
        """提取查询参数"""
        params = {
            'tables': [],
            'columns': [],
            'conditions': [],
            'group_by': [],
            'order_by': [],
            'limit': None
        }
        
        # 提取表名
        for chinese_name, table_name in self.table_aliases.items():
            if chinese_name in query:
                params['tables'].append(table_name)
        
        # 如果没有找到表名，使用默认表
        if not params['tables']:
            params['tables'] = ['products', 'sales_orders']
        
        # 提取时间条件
        time_patterns = [
            (r'(今天|今日)', 'CURDATE()'),
            (r'(昨天)', 'DATE_SUB(CURDATE(), INTERVAL 1 DAY)'),
            (r'(本周|这周)', 'WEEK(CURDATE())'),
            (r'(本月|这个月)', 'MONTH(CURDATE())'),
            (r'(今年)', 'YEAR(CURDATE())'),
            (r'(最近|近)(\d+)(天|日)', 'DATE_SUB(CURDATE(), INTERVAL \2 DAY)')
        ]
        
        for pattern, replacement in time_patterns:
            match = re.search(pattern, query)
            if match:
                if 'date' in pattern:
                    params['conditions'].append(f"order_date >= {replacement}")
                elif 'week' in pattern:
                    params['conditions'].append(f"WEEK(order_date) = {replacement}")
                elif 'month' in pattern:
                    params['conditions'].append(f"MONTH(order_date) = {replacement}")
                elif 'year' in pattern:
                    params['conditions'].append(f"YEAR(order_date) = {replacement}")
        
        # 提取数量限制
        limit_match = re.search(r'(前|显示)(\d+)(个|条)', query)
        if limit_match:
            params['limit'] = int(limit_match.group(2))
        
        return params
    
    def _build_sql_query(self, intent: str, params: Dict[str, Any]) -> str:
        """构建SQL查询语句"""
        tables = params['tables']
        
        if intent == 'count':
            return f"SELECT COUNT(*) as count FROM {tables[0]}"
        
        elif intent == 'sum':
            return f"SELECT SUM(total_amount) as total_sum FROM {tables[0]}"
        
        elif intent == 'avg':
            return f"SELECT AVG(price) as average_price FROM {tables[0]}"
        
        elif intent == 'extreme':
            if '最大' in params.get('conditions', [''])[0] or '最高' in params.get('conditions', [''])[0]:
                return f"SELECT MAX(price) as max_price FROM {tables[0]}"
            else:
                return f"SELECT MIN(price) as min_price FROM {tables[0]}"
        
        elif intent == 'group_by':
            return f"SELECT category_id, COUNT(*) as count FROM {tables[0]} GROUP BY category_id"
        
        else:  # select
            base_query = f"SELECT * FROM {tables[0]}"
            
            # 添加条件
            if params['conditions']:
                conditions = ' AND '.join(params['conditions'])
                base_query += f" WHERE {conditions}"
            
            # 添加排序
            if 'order_date' in self._get_table_columns(tables[0]):
                base_query += " ORDER BY order_date DESC"
            
            # 添加限制
            if params['limit']:
                base_query += f" LIMIT {params['limit']}"
            
            return base_query
    
    def _get_table_columns(self, table_name: str) -> List[str]:
        """获取表的列名"""
        if table_name in self.database_schema:
            return [col['name'] for col in self.database_schema[table_name]['columns']]
        return []
    
    async def _validate_sql(self, sql_query: str) -> bool:
        """验证SQL语法"""
        try:
            # 使用EXPLAIN来验证SQL语法
            explain_query = f"EXPLAIN {sql_query}"
            await self.db.execute(text(explain_query))
            return True
        except Exception:
            return False
    
    def _generate_explanation(self, intent: str, params: Dict[str, Any]) -> str:
        """生成查询解释"""
        table_name = params['tables'][0] if params['tables'] else '数据表'
        
        explanations = {
            'count': f"统计{table_name}表中的记录数量",
            'sum': f"计算{table_name}表中金额的总和",
            'avg': f"计算{table_name}表中价格的平均值",
            'extreme': f"查找{table_name}表中的极值",
            'group_by': f"按分类统计{table_name}表中的数据",
            'select': f"查询{table_name}表中的数据"
        }
        
        return explanations.get(intent, "执行数据查询")


# 全局SQL生成器实例
_sql_generator: Optional[SQLGenerator] = None


def get_sql_generator(db: AsyncSession, assistant_prompt: str = "你是一个智能助手，请根据用户需求提供专业的帮助。") -> SQLGenerator:
    """获取SQL生成器实例"""
    global _sql_generator
    if _sql_generator is None:
        _sql_generator = SQLGenerator(db, assistant_prompt)
    return _sql_generator


async def initialize_sql_generator(db: AsyncSession, assistant_prompt: str = "你是一个智能助手，请根据用户需求提供专业的帮助。"):
    """初始化SQL生成器"""
    global _sql_generator
    _sql_generator = SQLGenerator(db, assistant_prompt)
    await _sql_generator.initialize()