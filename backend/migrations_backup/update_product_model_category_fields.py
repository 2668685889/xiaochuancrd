"""
数据库迁移脚本：更新product_models表的category相关字段
确保category_uuid字段存在
"""

import asyncio
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

async def update_product_model_category_fields():
    """更新product_models表的category相关字段"""
    
    async with engine.connect() as conn:
        try:
            # 检查category_uuid字段是否存在
            check_category_uuid_sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'product_models' 
            AND COLUMN_NAME = 'category_uuid';
            """
            
            result = await conn.execute(text(check_category_uuid_sql))
            category_uuid_exists = result.fetchone() is not None
            
            # 执行必要的字段更新操作
            if not category_uuid_exists:
                # 添加category_uuid字段
                add_category_uuid_sql = """
                ALTER TABLE product_models 
                ADD COLUMN category_uuid CHAR(36) NULL,
                ADD CONSTRAINT fk_product_models_category_uuid 
                FOREIGN KEY (category_uuid) REFERENCES product_categories(uuid);
                """
                await conn.execute(text(add_category_uuid_sql))
                print("✅ 成功为product_models表添加category_uuid字段")
            
            # 提交事务
            await conn.commit()
            
            # 验证字段更新结果
            print("\n📊 字段更新结果:")
            
            # 检查最终字段状态
            final_check_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'product_models'
            AND COLUMN_NAME = 'category_uuid';
            """
            
            result = await conn.execute(text(final_check_sql))
            column = result.fetchone()
            
            if column:
                print(f"   {column[0]} ({column[1]}) - 可为空: {column[2]}")
            else:
                print("   category_uuid字段不存在")
            
            print("\n✅ 产品型号表category相关字段更新完成")
            
        except Exception as e:
            print(f"❌ 更新字段失败: {e}")
            await conn.rollback()

if __name__ == "__main__":
    asyncio.run(update_product_model_category_fields())