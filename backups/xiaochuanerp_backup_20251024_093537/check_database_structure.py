#!/usr/bin/env python3
"""
检查数据库表结构和数据格式
"""

import asyncio
import json
import sys
import os
from sqlalchemy import text

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db

async def check_database_structure():
    """检查数据库表结构和数据格式"""
    
    print("=== 检查数据库表结构和数据格式 ===\n")
    
    # 1. 检查sys_data_source表结构
    print("1. 检查sys_data_source表结构")
    async for db in get_db():
        # 获取表结构
        result = await db.execute(
            text("DESCRIBE sys_data_source")
        )
        
        print("表结构:")
        for row in result.fetchall():
            print(f"  {row[0]}: {row[1]} ({row[2]})")
        
        # 2. 检查所有数据源记录
        print("\n2. 检查所有数据源记录")
        data_sources = await db.execute(
            text("SELECT * FROM sys_data_source")
        )
        
        for record in data_sources.fetchall():
            print(f"\n记录ID: {record[0]}")
            print(f"名称: {record[1]}")
            print(f"类型: {record[2]}")
            print(f"连接配置: {record[3]}")
            print(f"连接配置类型: {type(record[3])}")
            
            # 尝试解析连接配置
            if record[3]:
                try:
                    # 先尝试JSON解析
                    config = json.loads(record[3])
                    print(f"JSON解析成功: {config}")
                except json.JSONDecodeError:
                    # 如果不是JSON，尝试其他格式
                    print("JSON解析失败，尝试其他格式...")
                    # 检查是否是简单的字符串
                    if isinstance(record[3], str):
                        print(f"字符串内容: {record[3]}")
        
        break
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    asyncio.run(check_database_structure())