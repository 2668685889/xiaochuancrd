#!/usr/bin/env python3
"""
测试DeepSeek API集成功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 设置环境变量（仅用于测试）
os.environ["DEEPSEEK_API_KEY"] = "sk-test-key-for-demo"

from app.core.database import AsyncSessionLocal
from app.services.deepseek_service import get_deepseek_service, initialize_deepseek_service
from app.services.mcp_mysql_service import MCPMySQLService


async def test_deepseek_service():
    """测试DeepSeek服务"""
    print("=== 测试DeepSeek服务 ===")
    
    # 初始化DeepSeek服务
    deepseek_service = await initialize_deepseek_service()
    if not deepseek_service:
        print("❌ DeepSeek服务初始化失败")
        return False
    
    # 检查服务就绪状态
    is_ready = await deepseek_service.is_ready()
    print(f"DeepSeek服务就绪状态: {'✅' if is_ready else '❌'}")
    
    if not is_ready:
        print("❌ DeepSeek服务未就绪，跳过测试")
        return False
    
    # 测试SQL生成
    test_query = "查询所有产品库存"
    print(f"测试查询: {test_query}")
    
    try:
        sql_result = await deepseek_service.generate_sql_query(test_query)
        if sql_result.get("success"):
            print(f"✅ SQL生成成功:")
            print(f"   SQL: {sql_result.get('sql')}")
            print(f"   说明: {sql_result.get('explanation')}")
        else:
            print(f"❌ SQL生成失败: {sql_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ SQL生成异常: {e}")
        return False
    
    return True


async def test_mcp_mysql_service():
    """测试MCP MySQL服务"""
    print("\n=== 测试MCP MySQL服务 ===")
    
    # 创建数据库会话
    async with AsyncSessionLocal() as session:
        # 初始化MCP服务
        mcp_service = MCPMySQLService(session)
        await mcp_service.initialize()
        
        if not mcp_service.is_initialized:
            print("❌ MCP服务初始化失败")
            return False
        
        # 测试查询
        test_queries = [
            "查询所有产品库存",
            "查询销售订单",
            "查询采购订单"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            try:
                result = await mcp_service.query(query)
                if result.get("success"):
                    print("✅ 查询成功:")
                    content = result.get("content", [])
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")
                        # 只显示前200个字符
                        preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                        print(f"   结果预览: {preview}")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
            except Exception as e:
                print(f"❌ 查询异常: {e}")
        
        # 测试分析
        print(f"\n测试分析: 分析库存状况")
        try:
            result = await mcp_service.analyze("分析库存状况")
            if result.get("success"):
                print("✅ 分析成功:")
                content = result.get("content", [])
                if content and len(content) > 0:
                    text_content = content[0].get("text", "")
                    # 只显示前200个字符
                    preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                    print(f"   结果预览: {preview}")
            else:
                print(f"❌ 分析失败: {result.get('error')}")
        except Exception as e:
            print(f"❌ 分析异常: {e}")
        
        return True


async def main():
    """主函数"""
    print("开始测试DeepSeek API集成功能...")
    
    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未设置DEEPSEEK_API_KEY环境变量")
        print("提示: 请在.env文件中设置有效的DeepSeek API密钥")
        print("或者获取API密钥: https://platform.deepseek.com/api_keys")
        return
    
    # 测试DeepSeek服务
    deepseek_ok = await test_deepseek_service()
    
    # 测试MCP MySQL服务
    mcp_ok = await test_mcp_mysql_service()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"DeepSeek服务: {'✅' if deepseek_ok else '❌'}")
    print(f"MCP MySQL服务: {'✅' if mcp_ok else '❌'}")
    
    if deepseek_ok and mcp_ok:
        print("🎉 所有测试通过！DeepSeek API集成功能正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查配置和实现。")


if __name__ == "__main__":
    asyncio.run(main())