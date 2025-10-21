"""
数据库迁移脚本：更新products表的category相关字段
将category字段重命名为category_name，并确保category_uuid字段存在
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def update_product_category_fields():
    """更新products表的category相关字段"""
    
    async with engine.connect() as conn:
        try:
            # 检查category字段是否存在
            check_category_sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'products' 
            AND COLUMN_NAME = 'category';
            """
            
            result = await conn.execute(text(check_category_sql))
            category_exists = result.fetchone() is not None
            
            # 检查category_name字段是否存在
            check_category_name_sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'products' 
            AND COLUMN_NAME = 'category_name';
            """
            
            result = await conn.execute(text(check_category_name_sql))
            category_name_exists = result.fetchone() is not None
            
            # 检查category_uuid字段是否存在
            check_category_uuid_sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'products' 
            AND COLUMN_NAME = 'category_uuid';
            """
            
            result = await conn.execute(text(check_category_uuid_sql))
            category_uuid_exists = result.fetchone() is not None
            
            # 执行必要的字段更新操作
            if category_exists and not category_name_exists:
                # 将category字段重命名为category_name
                rename_sql = """
                ALTER TABLE products 
                CHANGE COLUMN category category_name VARCHAR(50) NULL;
                """
                await conn.execute(text(rename_sql))
                print("✅ 成功将category字段重命名为category_name")
            
            if not category_uuid_exists:
                # 添加category_uuid字段
                add_category_uuid_sql = """
                ALTER TABLE products 
                ADD COLUMN category_uuid CHAR(36) NULL,
                ADD CONSTRAINT fk_products_category_uuid 
                FOREIGN KEY (category_uuid) REFERENCES product_categories(uuid);
                """
                await conn.execute(text(add_category_uuid_sql))
                print("✅ 成功添加category_uuid字段")
            
            # 提交事务
            await conn.commit()
            
            # 验证字段更新结果
            print("\n📊 字段更新结果:")
            
            # 检查最终字段状态
            final_check_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'products'
            AND COLUMN_NAME IN ('category', 'category_name', 'category_uuid');
            """
            
            result = await conn.execute(text(final_check_sql))
            columns = result.fetchall()
            
            for column in columns:
                print(f"   {column[0]} ({column[1]}) - 可为空: {column[2]}")
            
            print("\n✅ 产品表category相关字段更新完成")
            
        except Exception as e:
            print(f"❌ 更新字段失败: {e}")
            await conn.rollback()

if __name__ == "__main__":
    asyncio.run(update_product_category_fields())