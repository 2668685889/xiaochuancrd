#!/usr/bin/env python3
"""
深度检查数据库中的实际数据
"""

import asyncio
import json
import sys
import os
from sqlalchemy import text

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db

async def deep_check_database():
    """深度检查数据库中的实际数据"""
    
    print("=== 深度检查数据库中的实际数据 ===\n")
    
    async for db in get_db():
        # 1. 使用原始SQL查询检查数据
        print("1. 使用原始SQL查询检查数据")
        
        # 查询所有字段
        result = await db.execute(
            text("SELECT id, uuid, name, type, connection_config FROM sys_data_source")
        )
        
        for record in result.fetchall():
            print(f"\n记录ID: {record[0]}")
            print(f"UUID: {record[1]}")
            print(f"名称: {record[2]}")
            print(f"类型: {record[3]}")
            print(f"连接配置原始值: {repr(record[4])}")
            print(f"连接配置类型: {type(record[4])}")
            
            # 尝试不同的解析方式
            if record[4]:
                # 尝试直接JSON解析
                try:
                    config = json.loads(record[4])
                    print(f"✅ 直接JSON解析成功: {config}")
                except json.JSONDecodeError as e:
                    print(f"❌ 直接JSON解析失败: {e}")
                
                # 如果是字符串，检查内容
                if isinstance(record[4], str):
                    print(f"字符串长度: {len(record[4])}")
                    print(f"字符串内容: {record[4]}")
        
        # 2. 检查表结构详细信息
        print("\n2. 检查表结构详细信息")
        
        # 获取更详细的表信息
        table_info = await db.execute(
            text("SHOW COLUMNS FROM sys_data_source")
        )
        
        print("表字段信息:")
        for column in table_info.fetchall():
            print(f"  字段: {column[0]}, 类型: {column[1]}, 是否可为空: {column[2]}, 默认值: {column[3]}")
        
        # 3. 尝试直接使用MySQL的JSON函数查询
        print("\n3. 使用MySQL JSON函数查询")
        
        try:
            json_result = await db.execute(
                text("SELECT id, name, JSON_TYPE(connection_config) as json_type, JSON_VALID(connection_config) as is_valid FROM sys_data_source")
            )
            
            for row in json_result.fetchall():
                print(f"ID: {row[0]}, 名称: {row[1]}, JSON类型: {row[2]}, JSON是否有效: {row[3]}")
        except Exception as e:
            print(f"JSON函数查询失败: {e}")
        
        break
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    asyncio.run(deep_check_database())