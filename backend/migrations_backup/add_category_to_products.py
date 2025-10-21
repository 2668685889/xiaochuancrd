"""
数据库迁移脚本：为products表添加category字段
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def add_category_column():
    """为products表添加category字段"""
    
    # SQL语句添加category字段
    alter_table_sql = """
    ALTER TABLE products 
    ADD COLUMN category VARCHAR(50) NULL,
    ADD INDEX idx_category (category);
    """
    
    async with engine.connect() as conn:
        try:
            # 执行SQL语句
            await conn.execute(text(alter_table_sql))
            await conn.commit()
            print("✅ 成功为products表添加category字段")
            
            # 检查字段是否添加成功
            check_sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'products' 
            AND COLUMN_NAME = 'category';
            """
            
            result = await conn.execute(text(check_sql))
            if result.fetchone():
                print("✅ category字段已成功添加到products表")
            else:
                print("❌ category字段添加失败")
                
        except Exception as e:
            print(f"❌ 添加category字段失败: {e}")
            await conn.rollback()

if __name__ == "__main__":
    asyncio.run(add_category_column())