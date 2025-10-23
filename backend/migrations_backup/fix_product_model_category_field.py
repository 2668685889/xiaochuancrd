"""
数据库迁移脚本：修复product_models表的category字段问题
删除category字段或为它设置默认值
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def fix_product_model_category_field():
    """修复product_models表的category字段问题"""
    
    async with engine.connect() as conn:
        try:
            # 检查category字段的详细信息
            check_category_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'product_models' 
            AND COLUMN_NAME = 'category';
            """
            
            result = await conn.execute(text(check_category_sql))
            category_info = result.fetchone()
            
            if category_info:
                print(f"📊 当前category字段信息:")
                print(f"   字段名: {category_info[0]}")
                print(f"   类型: {category_info[1]}")
                print(f"   是否可为空: {category_info[2]}")
                print(f"   默认值: {category_info[3]}")
                
                # 由于category字段在模型中已删除，我们有两个选择：
                # 1. 删除category字段（推荐，因为模型已不再使用）
                # 2. 为category字段设置默认值
                
                # 选择1：删除category字段
                drop_category_sql = """
                ALTER TABLE product_models 
                DROP COLUMN category;
                """
                
                await conn.execute(text(drop_category_sql))
                print("✅ 成功删除product_models表的category字段")
                
            else:
                print("ℹ️ category字段不存在，无需修复")
            
            # 提交事务
            await conn.commit()
            
            # 验证修复结果
            print("\n📊 修复后字段状态:")
            
            final_check_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'product_models'
            ORDER BY ORDINAL_POSITION;
            """
            
            result = await conn.execute(text(final_check_sql))
            columns = result.fetchall()
            
            print("product_models表当前字段:")
            for col in columns:
                print(f"   {col[0]} ({col[1]}) - 可为空: {col[2]}")
            
            print("\n✅ product_models表category字段修复完成")
            
        except Exception as e:
            print(f"❌ 修复字段失败: {e}")
            await conn.rollback()

if __name__ == "__main__":
    asyncio.run(fix_product_model_category_field())