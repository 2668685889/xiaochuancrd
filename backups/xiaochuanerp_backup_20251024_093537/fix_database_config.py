#!/usr/bin/env python3
"""
修复数据库中的连接配置格式问题
"""

import asyncio
import json
import sys
import os
from sqlalchemy import text

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db

async def fix_database_config():
    """修复数据库中的连接配置格式问题"""
    
    print("=== 修复数据库连接配置格式问题 ===\n")
    
    async for db in get_db():
        # 1. 首先检查当前的数据源记录
        print("1. 检查当前数据源记录")
        data_sources = await db.execute(
            text("SELECT * FROM sys_data_source WHERE name = '主数据库'")
        )
        
        current_record = data_sources.fetchone()
        if not current_record:
            print("❌ 未找到'主数据库'记录")
            return
        
        print(f"当前记录ID: {current_record[0]}")
        print(f"当前连接配置: {current_record[3]}")
        print(f"连接配置类型: {type(current_record[3])}")
        
        # 2. 修复连接配置格式
        print("\n2. 修复连接配置格式")
        
        # 正确的连接配置
        correct_config = {
            "host": "localhost",
            "port": 3306,
            "database": "xiaochuanERP",
            "username": "root",
            "password": "Xiaochuan123!",  # 使用原始密码
            "schema_name": None
        }
        
        # 更新数据库记录
        await db.execute(
            text("UPDATE sys_data_source SET connection_config = :config WHERE id = :id"),
            {"config": json.dumps(correct_config), "id": current_record[0]}
        )
        
        await db.commit()
        print("✅ 连接配置格式修复完成")
        
        # 3. 验证修复结果
        print("\n3. 验证修复结果")
        data_sources = await db.execute(
            text("SELECT * FROM sys_data_source WHERE name = '主数据库'")
        )
        
        updated_record = data_sources.fetchone()
        if updated_record:
            print(f"修复后连接配置: {updated_record[3]}")
            print(f"修复后配置类型: {type(updated_record[3])}")
            
            # 验证配置格式
            try:
                config = json.loads(updated_record[3])
                print(f"✅ JSON解析成功: {config}")
                print("✅ 连接配置格式修复成功！")
            except json.JSONDecodeError:
                print("❌ JSON解析失败，修复可能有问题")
        
        break
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    asyncio.run(fix_database_config())