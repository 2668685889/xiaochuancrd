#!/usr/bin/env python3
"""
测试智能助手查询修复
"""
import asyncio
import json
import httpx

async def test_smart_assistant_query():
    """测试智能助手查询功能"""
    base_url = "http://localhost:8080"
    
    # 测试数据
    test_queries = [
        "查询所有商品",
        "查询笔记本电脑",
        "查询联想产品",
        "查询华为产品",
        "查询库存不足的商品",
        "查询价格大于5000的商品"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for query in test_queries:
            print(f"\n测试查询: {query}")
            print("-" * 50)
            
            # 发送查询请求
            response = await client.post(
                f"{base_url}/api/v1/smart-assistant/chat",
                json={"message": query, "session_id": "test_session"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # 获取响应数据
                    response_data = result.get("data", {})
                    response_text = response_data.get("response", "")
                    
                    if response_text:
                        print(f"查询结果:\n{response_text}")
                    else:
                        print("查询结果为空")
                else:
                    print(f"查询失败: {result.get('error', '未知错误')}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_smart_assistant_query())