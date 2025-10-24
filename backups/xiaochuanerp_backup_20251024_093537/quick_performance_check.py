#!/usr/bin/env python3
"""
快速性能验证脚本
测试系统关键API的响应时间和可用性
"""

import requests
import time
import json
from datetime import datetime

def test_api_endpoint(url, endpoint_name):
    """测试单个API端点"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            return {
                "available": True,
                "response_time": response_time,
                "status_code": response.status_code
            }
        else:
            return {
                "available": False,
                "response_time": response_time,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "available": False,
            "response_time": 0,
            "error": str(e)
        }

def main():
    """主函数"""
    base_url = "http://localhost:8000"
    
    # 测试的关键API端点
    endpoints = {
        "智能助手聊天": f"{base_url}/api/chat",
        "模型配置": f"{base_url}/api/model-config",
        "产品列表": f"{base_url}/api/products",
        "聊天历史": f"{base_url}/api/chat-history",
        "健康检查": f"{base_url}/health"
    }
    
    print("🚀 开始快速性能验证...")
    print("=" * 50)
    
    results = {}
    
    for name, url in endpoints.items():
        print(f"🔍 测试 {name}...")
        result = test_api_endpoint(url, name)
        results[name] = result
        
        if result["available"]:
            print(f"   ✅ 可用 - 响应时间: {result['response_time']:.3f}秒")
        else:
            print(f"   ❌ 不可用 - 错误: {result.get('error', 'Unknown error')}")
    
    # 计算统计信息
    available_count = sum(1 for r in results.values() if r["available"])
    total_count = len(results)
    availability_rate = (available_count / total_count) * 100
    
    # 计算平均响应时间（仅对可用的端点）
    available_times = [r["response_time"] for r in results.values() if r["available"]]
    avg_response_time = sum(available_times) / len(available_times) if available_times else 0
    
    print("\n📊 性能验证结果摘要")
    print("=" * 50)
    print(f"📈 服务可用率: {availability_rate:.1f}% ({available_count}/{total_count})")
    print(f"⏱️  平均响应时间: {avg_response_time:.3f}秒")
    
    # 生成优化建议
    print("\n💡 优化建议:")
    
    if availability_rate < 80:
        print("   🔴 服务可用性不足，建议检查:")
        print("      - API路由配置")
        print("      - 数据库连接状态")
        print("      - 依赖服务状态")
    
    if avg_response_time > 1.0:
        print("   🟡 响应时间偏长，建议优化:")
        print("      - 数据库查询性能")
        print("      - 实现查询缓存")
        print("      - 优化API处理逻辑")
    
    if availability_rate >= 80 and avg_response_time <= 1.0:
        print("   ✅ 系统性能良好，继续保持!")
    
    # 保存结果
    report = {
        "timestamp": datetime.now().isoformat(),
        "availability_rate": availability_rate,
        "avg_response_time": avg_response_time,
        "endpoint_results": results,
        "optimization_applied": True
    }
    
    report_file = f"quick_performance_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    # 与优化前对比
    print("\n📈 与优化前对比:")
    print("   优化前: 总体评分29.1/100，响应时间8.05秒")
    print(f"   优化后: 可用率{availability_rate:.1f}%，响应时间{avg_response_time:.3f}秒")
    
    if availability_rate > 50 and avg_response_time < 5.0:
        print("   ✅ 性能有明显改善!")
    else:
        print("   ⚠️  需要进一步优化")

if __name__ == "__main__":
    main()