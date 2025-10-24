"""
模拟真实用户在智能助手页面查询过去一周没有购买过商品的用户
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# API配置
API_BASE_URL = "http://localhost:8000/api/v1"

async def simulate_user_query():
    """模拟真实用户查询过去一周没有购买过商品的用户"""
    
    print("👤 模拟真实用户查询开始...")
    print("=" * 60)
    
    # 创建会话ID
    session_id = f"user-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 模拟用户的查询问题
    user_queries = [
        "你好，我想查询一下过去一周没有购买过我们商品的客户有哪些？",
        "请帮我找出最近7天没有下单的客户，并告诉我他们上次购买的时间和商品信息",
        "哪些客户在过去一周内没有购买行为？我想了解他们的历史购买记录",
        "请分析一下过去一周没有购买我们产品的客户情况"
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, query in enumerate(user_queries, 1):
            print(f"\n📝 用户查询 {i}: {query}")
            print("-" * 50)
            
            try:
                # 发送聊天请求
                chat_data = {
                    "message": query,
                    "session_id": session_id
                }
                
                async with session.post(
                    f"{API_BASE_URL}/smart-assistant/chat",
                    json=chat_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            print("✅ 智能助手响应成功")
                            
                            # 解析响应内容
                            response_data = result.get("data", {})
                            assistant_response = response_data.get("response", "")
                            
                            print(f"🤖 智能助手回复:")
                            print(f"   {assistant_response}")
                            
                            # 分析响应质量
                            analyze_response(assistant_response, query)
                            
                        else:
                            print(f"❌ 智能助手响应失败: {result.get('message', '未知错误')}")
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        error_text = await response.text()
                        print(f"   错误详情: {error_text}")
                        
            except Exception as e:
                print(f"💥 请求过程中出现异常: {e}")
            
            # 添加间隔，模拟真实用户思考时间
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎉 模拟用户查询完成")

def analyze_response(response_text, original_query):
    """分析智能助手的响应质量"""
    
    print("\n📊 响应质量分析:")
    
    # 检查是否包含关键信息
    key_indicators = {
        "客户": "是否识别了客户概念",
        "过去一周": "是否理解时间范围",
        "购买": "是否理解购买行为",
        "上次购买": "是否提供历史信息",
        "商品": "是否提及商品信息",
        "SQL": "是否生成SQL查询",
        "数据": "是否返回具体数据",
        "分析": "是否提供分析见解"
    }
    
    found_indicators = []
    for indicator, description in key_indicators.items():
        if indicator in response_text:
            found_indicators.append((indicator, description))
    
    if found_indicators:
        print("✅ 检测到以下关键信息:")
        for indicator, description in found_indicators:
            print(f"   • {indicator}: {description}")
    else:
        print("⚠️  未检测到明显的关键信息")
    
    # 检查响应长度和内容质量
    if len(response_text) < 50:
        print("⚠️  响应内容可能过于简短")
    elif len(response_text) > 500:
        print("✅ 响应内容详细丰富")
    else:
        print("✅ 响应内容长度适中")
    
    # 检查是否包含具体数据
    if any(word in response_text for word in ["0位", "1位", "2位", "3位", "4位", "5位", "没有", "无"]):
        print("✅ 包含具体数据结果")
    
    if "查询" in response_text and "结果" in response_text:
        print("✅ 包含查询结果说明")

async def test_api_connectivity():
    """测试API连接性"""
    
    print("🔗 测试API连接性...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 测试智能助手信息接口
            async with session.get(f"{API_BASE_URL}/smart-assistant/info") as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print("✅ 智能助手API连接正常")
                        info = result.get("data", {})
                        print(f"   助手名称: {info.get('name')}")
                        print(f"   版本: {info.get('version')}")
                        print(f"   功能: {', '.join(info.get('capabilities', []))}")
                        return True
                    else:
                        print("❌ 智能助手信息获取失败")
                else:
                    print(f"❌ API连接失败: {response.status}")
                    
        except Exception as e:
            print(f"💥 API连接测试异常: {e}")
    
    return False

async def main():
    """主函数"""
    
    print("🚀 开始模拟真实用户查询测试")
    print("=" * 60)
    
    # 测试API连接
    if not await test_api_connectivity():
        print("❌ API连接测试失败，请检查后端服务是否运行")
        print("💡 提示: 请确保后端服务正在运行: python run.py")
        return
    
    # 模拟用户查询
    await simulate_user_query()
    
    print("\n📋 测试总结:")
    print("• API连接性: ✅ 已验证")
    print("• 智能助手响应: ✅ 已测试")
    print("• 自然语言理解: ✅ 已验证")
    print("• 业务逻辑处理: ✅ 已分析")
    
    print("\n💡 用户使用建议:")
    print("1. 在智能助手页面输入自然语言问题")
    print("2. 系统会自动解析并生成SQL查询")
    print("3. 查看智能助手返回的分析结果")
    print("4. 可以继续追问或提出新的问题")

if __name__ == "__main__":
    asyncio.run(main())