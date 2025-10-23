#!/usr/bin/env python3
"""智能助手系统数据库索引优化脚本"""

import os
import sys

def optimize_database_indexes():
    """优化数据库索引"""
    print("🔧 优化数据库索引...")
    
    # 常用查询字段索引建议
    index_suggestions = [
        # 产品表索引
        "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
        "CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);",
        
        # 智能助手相关表索引
        "CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);",
        
        # 模型配置表索引
        "CREATE INDEX IF NOT EXISTS idx_model_config_name ON model_config(name);",
        
        # 采购订单相关索引
        "CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);",
        "CREATE INDEX IF NOT EXISTS idx_purchase_orders_created_at ON purchase_orders(created_at);",
        
        # 库存相关索引
        "CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_inventory_warehouse_id ON inventory(warehouse_id);",
    ]
    
    print("📋 建议创建的索引:")
    for i, index_sql in enumerate(index_suggestions, 1):
        print(f"{i}. {index_sql}")
    
    print("\n💡 请在数据库管理工具中执行以上SQL语句")
    print("💡 或者联系数据库管理员进行索引优化")
    
    return index_suggestions

def generate_performance_monitoring_queries():
    """生成性能监控查询"""
    print("\n🔍 性能监控查询:")
    
    monitoring_queries = [
        # 慢查询监控
        """-- 查看慢查询
        SELECT * FROM information_schema.processlist 
        WHERE command != 'Sleep' AND time > 2 
        ORDER BY time DESC;""",
        
        # 表大小统计
        """-- 查看表大小
        SELECT 
            table_name,
            round(((data_length + index_length) / 1024 / 1024), 2) as size_mb
        FROM information_schema.tables 
        WHERE table_schema = 'xiaochuanerp'
        ORDER BY size_mb DESC;""",
        
        # 索引使用情况
        """-- 查看索引使用情况
        SELECT 
            index_name,
            table_name,
            non_unique
        FROM information_schema.statistics 
        WHERE table_schema = 'xiaochuanerp';"""
    ]
    
    for i, query in enumerate(monitoring_queries, 1):
        print(f"\n{i}. {query}")

def main():
    """主函数"""
    print("🚀 开始数据库索引优化分析...")
    
    try:
        # 生成索引优化建议
        optimize_database_indexes()
        
        # 生成性能监控查询
        generate_performance_monitoring_queries()
        
        print("\n✅ 数据库索引优化分析完成")
        print("💡 请根据建议优化数据库索引结构")
        
    except Exception as e:
        print(f"❌ 数据库优化分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
