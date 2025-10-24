#!/usr/bin/env python3
"""
测试自定义提示词功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_async_db
from app.services.assistant_config_service import AssistantConfigService
from app.services.mcp_mysql_service import MCPMySQLService

async def test_custom_prompt():
    """测试自定义提示词获取"""
    print("=== 测试自定义提示词功能 ===")
    
    try:
        # 获取数据库会话
        async for db in get_async_db():
            # 测试AssistantConfigService
            config_service = AssistantConfigService(db)
            
            # 获取自定义提示词
            custom_prompt = await config_service.get_custom_prompt("default")
            
            if custom_prompt:
                print("✅ 成功获取自定义提示词")
                print(f"提示词长度: {len(custom_prompt)} 字符")
                print(f"前200字符预览: {custom_prompt[:200]}...")
            else:
                print("⚠️ 未找到自定义提示词")
            
            # 测试MCP MySQL服务
            print("\n=== 测试MCP MySQL服务 ===")
            mcp_service = MCPMySQLService(db)
            
            # 测试SQL生成（包含自定义提示词）
            test_query = "查询所有商品信息"
            print(f"测试查询: {test_query}")
            
            result = await mcp_service._generate_sql_with_deepseek(test_query)
            
            if result["success"]:
                print("✅ SQL生成成功")
                print(f"生成的SQL: {result['sql']}")
                if result.get('explanation'):
                    print(f"解释: {result['explanation']}")
            else:
                print(f"❌ SQL生成失败: {result.get('error', '未知错误')}")
            
            break  # 只处理第一个会话
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_custom_prompt())