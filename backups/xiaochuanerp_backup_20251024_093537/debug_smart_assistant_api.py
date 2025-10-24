#!/usr/bin/env python3
"""
调试smart_assistant API的数据库配置保存功能
"""

import asyncio
import json
import aiohttp
import sys
import os
from sqlalchemy import text

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db
from app.models.smart_assistant import DataSourceModel

async def debug_smart_assistant_api():
    """调试smart_assistant API的数据库配置保存功能"""
    
    print("=== 调试smart_assistant API数据库配置保存功能 ===\n")
    
    # 1. 首先检查数据库中的当前状态
    print("1. 检查数据库中的当前数据源记录")
    async for db in get_db():
        data_sources = await db.execute(
            text("SELECT * FROM sys_data_source WHERE name = '主数据库'")
        )
        current_record = data_sources.fetchone()
        
        if current_record:
            print(f"当前记录: ID={current_record[0]}, 名称={current_record[1]}")
            print(f"连接配置: {current_record[3]}")
            
            # 解析连接配置
            try:
                config = json.loads(current_record[3])
                print(f"当前密码: {config.get('password', '未设置')}")
            except json.JSONDecodeError:
                print("连接配置解析失败")
        else:
            print("未找到'主数据库'记录")
        break
    
    print("\n2. 模拟发送POST请求到smart-assistant/database-config")
    
    # 准备请求数据
    config_data = {
        "host": "localhost",
        "port": 3306,
        "database": "xiaochuanERP",
        "username": "root",
        "password": "DebugTestPassword123!",
        "schema_name": "xiaochuanERP"
    }
    
    print(f"发送的配置数据: {json.dumps(config_data, indent=2)}")
    
    # 发送POST请求
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/api/v1/smart-assistant/database-config",
                json=config_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"响应状态码: {response.status}")
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    print(f"API返回结果: {json.dumps(result, indent=2)}")
                else:
                    print("❌ API请求失败")
                    
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    # 等待一段时间让事务提交
    print("\n3. 等待事务提交...")
    await asyncio.sleep(2)
    
    # 4. 再次检查数据库状态
    print("\n4. 检查数据库更新后的状态")
    async for db in get_db():
        data_sources = await db.execute(
            text("SELECT * FROM sys_data_source WHERE name = '主数据库'")
        )
        updated_record = data_sources.fetchone()
        
        if updated_record:
            print(f"更新后记录: ID={updated_record[0]}, 名称={updated_record[1]}")
            print(f"连接配置: {updated_record[3]}")
            
            # 解析连接配置
            try:
                config = json.loads(updated_record[3])
                new_password = config.get('password', '未设置')
                print(f"更新后密码: {new_password}")
                
                if new_password == "DebugTestPassword123!":
                    print("✅ 密码更新成功！")
                else:
                    print("❌ 密码更新失败！")
                    print(f"期望密码: DebugTestPassword123!")
                    print(f"实际密码: {new_password}")
                    
            except json.JSONDecodeError:
                print("连接配置解析失败")
        else:
            print("未找到'主数据库'记录")
        break
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    asyncio.run(debug_smart_assistant_api())