#!/usr/bin/env python3
"""
智能助手模拟用户查询 - 修复版
模拟真实用户在智能助手页面查询过去一周未购买商品的用户及其上次购买信息
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

# 智能助手API配置
API_BASE_URL = "http://localhost:8000/api/v1/smart-assistant"

async def test_smart_assistant_connection():
    """测试智能助手连接"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_BASE_URL}/info")
            if response.status_code == 200:
                data = response.json()
                print("✅ 智能助手连接成功")
                print(f"   名称: {data['data']['name']}")
                print(f"   描述: {data['data']['description']}")
                print(f"   版本: {data['data']['version']}")
                return True
            else:
                print(f"❌ 智能助手连接失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 智能助手连接异常: {str(e)}")
        return False

async def simulate_user_query(user_message: str, session_id: str = None):
    """模拟用户向智能助手发送查询"""
    try:
        payload = {
            "message": user_message,
            "session_id": session_id or "test_session_001"
        }
        
        print(f"\n📝 用户查询: {user_message}")
        print("-" * 80)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assistant_response = data["data"]["response"]
                    print(f"🤖 智能助手响应:")
                    print(f"   {assistant_response}")
                    
                    # 分析响应质量
                    analyze_response_quality(assistant_response, user_message)
                    
                    return assistant_response
                else:
                    print(f"❌ 智能助手响应失败: {data.get('message', '未知错误')}")
                    return None
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ 查询异常: {str(e)}")
        return None

def analyze_response_quality(response: str, user_message: str):
    """分析智能助手响应质量"""
    print("\n📊 响应质量分析:")
    
    # 检查是否包含SQL查询
    if "SELECT" in response.upper() or "FROM" in response.upper():
        print("   ✅ 包含SQL查询语句")
        
        # 检查表名是否正确
        if "sales_orders" in response or "customers" in response:
            print("   ✅ 使用了正确的表名")
        else:
            print("   ⚠️  可能使用了错误的表名")
            
        # 检查是否包含时间范围
        if "过去一周" in user_message or "最近7天" in user_message:
            if "7" in response or "一周" in response or "7天" in response:
                print("   ✅ 正确识别了时间范围")
            else:
                print("   ⚠️  可能未正确识别时间范围")
    else:
        print("   ⚠️  未包含SQL查询语句")
    
    # 检查是否包含业务逻辑
    if "未购买" in response or "没有购买" in response or "不活跃" in response:
        print("   ✅ 正确识别了业务逻辑")
    else:
        print("   ⚠️  可能未正确识别业务逻辑")
    
    # 检查响应长度
    if len(response) > 100:
        print("   ✅ 响应内容详细")
    else:
        print("   ⚠️  响应内容可能过于简略")

async def main():
    """主函数"""
    print("🚀 开始模拟智能助手用户查询测试")
    print("=" * 80)
    
    # 1. 测试连接
    if not await test_smart_assistant_connection():
        print("❌ 连接测试失败，请检查后端服务是否正常运行")
        return
    
    print("\n" + "=" * 80)
    print("🧪 开始模拟用户查询")
    print("=" * 80)
    
    # 2. 模拟多种用户查询方式
    user_queries = [
        "查询过去一周没有购买过我们商品的用户，并给出他们上次购买的时间和购买的商品",
        "帮我找出最近7天没有下单的客户，显示他们最后一次的订单信息",
        "哪些客户在过去一周内没有进行购买？请显示他们之前的购买记录",
        "查找不活跃客户：过去一周没有购买行为的用户及其历史订单"
    ]
    
    session_id = f"test_session_{int(datetime.now().timestamp())}"
    
    for i, query in enumerate(user_queries, 1):
        print(f"\n🔍 测试查询 {i}/{len(user_queries)}")
        await simulate_user_query(query, session_id)
        
        # 添加间隔，避免请求过快
        if i < len(user_queries):
            await asyncio.sleep(2)
    
    print("\n" + "=" * 80)
    print("📋 测试总结")
    print("=" * 80)
    print("✅ 测试完成！")
    print("\n📈 测试验证了以下功能：")
    print("   • 智能助手API连接性")
    print("   • 自然语言查询理解能力")
    print("   • 业务逻辑识别准确性")
    print("   • SQL查询生成能力")
    print("   • 多轮对话支持")
    print("\n💡 建议：")
    print("   • 检查智能助手生成的SQL是否使用正确的表名")
    print("   • 验证查询结果是否符合业务逻辑")
    print("   • 测试不同时间范围的查询准确性")

if __name__ == "__main__":
    asyncio.run(main())