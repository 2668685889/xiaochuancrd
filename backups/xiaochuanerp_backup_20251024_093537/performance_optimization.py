#!/usr/bin/env python3
"""
智能助手系统性能优化脚本
用于分析和优化系统性能瓶颈
"""

import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

def test_api_response_time(url, data=None, method='GET', headers=None):
    """测试单个API接口的响应时间"""
    start_time = time.time()
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            'url': url,
            'method': method,
            'status_code': response.status_code,
            'response_time': response_time,
            'success': response.status_code == 200,
            'response_size': len(response.content)
        }
    except Exception as e:
        end_time = time.time()
        return {
            'url': url,
            'method': method,
            'status_code': None,
            'response_time': end_time - start_time,
            'success': False,
            'error': str(e)
        }

def test_concurrent_requests(url, concurrent_requests=10):
    """测试并发请求性能"""
    print(f"\n📊 测试并发性能: {concurrent_requests} 个并发请求到 {url}")
    
    start_time = time.time()
    response_times = []
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(test_api_response_time, url) for _ in range(concurrent_requests)]
        
        for future in as_completed(futures):
            result = future.result()
            response_times.append(result['response_time'])
            
            if result['success']:
                print(f"  ✅ 请求成功 - 响应时间: {result['response_time']:.2f}秒")
            else:
                print(f"  ❌ 请求失败 - 错误: {result.get('error', 'Unknown error')}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return {
        'total_requests': concurrent_requests,
        'total_time': total_time,
        'avg_response_time': statistics.mean(response_times) if response_times else 0,
        'min_response_time': min(response_times) if response_times else 0,
        'max_response_time': max(response_times) if response_times else 0,
        'requests_per_second': concurrent_requests / total_time if total_time > 0 else 0
    }

def analyze_database_performance():
    """分析数据库查询性能"""
    print("\n🔍 分析数据库查询性能...")
    
    # 测试简单的数据库查询
    simple_queries = [
        {
            'name': '查询产品数量',
            'url': 'http://localhost:8000/api/v1/smart-assistant/chat',
            'data': {'message': '查询产品数量', 'session_id': 'perf-test-001'}
        },
        {
            'name': '查询客户信息',
            'url': 'http://localhost:8000/api/v1/smart-assistant/chat',
            'data': {'message': '查询客户信息', 'session_id': 'perf-test-002'}
        },
        {
            'name': '查询销售订单',
            'url': 'http://localhost:8000/api/v1/smart-assistant/chat',
            'data': {'message': '查询销售订单', 'session_id': 'perf-test-003'}
        }
    ]
    
    results = []
    for query in simple_queries:
        result = test_api_response_time(query['url'], query['data'], 'POST')
        results.append({
            'query_name': query['name'],
            'response_time': result['response_time'],
            'success': result['success']
        })
        
        if result['success']:
            print(f"  ✅ {query['name']}: {result['response_time']:.2f}秒")
        else:
            print(f"  ❌ {query['name']}: 失败 - {result.get('error', 'Unknown error')}")
    
    return results

def check_system_health():
    """检查系统健康状态"""
    print("\n🏥 检查系统健康状态...")
    
    health_endpoints = [
        {'name': '智能助手信息', 'url': 'http://localhost:8000/api/v1/smart-assistant/info'},
        {'name': '模型配置', 'url': 'http://localhost:8000/api/v1/smart-assistant/model-config'},
        {'name': '聊天历史', 'url': 'http://localhost:8000/api/v1/smart-assistant/history'},
        {'name': '前端页面', 'url': 'http://localhost:3001'}
    ]
    
    health_status = {}
    for endpoint in health_endpoints:
        result = test_api_response_time(endpoint['url'])
        health_status[endpoint['name']] = {
            'available': result['success'],
            'response_time': result['response_time']
        }
        
        status_icon = '✅' if result['success'] else '❌'
        print(f"  {status_icon} {endpoint['name']}: {'可用' if result['success'] else '不可用'} - {result['response_time']:.2f}秒")
    
    return health_status

def generate_optimization_recommendations(performance_data):
    """生成性能优化建议"""
    print("\n💡 性能优化建议:")
    
    recommendations = []
    
    # 分析响应时间
    avg_response_time = performance_data.get('avg_response_time', 0)
    if avg_response_time > 3:
        recommendations.append("🔴 高优先级: 平均响应时间超过3秒，需要立即优化")
        recommendations.append("   - 检查数据库查询性能，添加索引")
        recommendations.append("   - 优化SQL查询语句，避免全表扫描")
        recommendations.append("   - 考虑添加查询缓存机制")
    elif avg_response_time > 1:
        recommendations.append("🟡 中优先级: 平均响应时间超过1秒，建议优化")
        recommendations.append("   - 检查API接口的数据库查询")
        recommendations.append("   - 优化前端资源加载")
        recommendations.append("   - 考虑使用异步处理")
    else:
        recommendations.append("🟢 良好: 响应时间在可接受范围内")
    
    # 分析并发性能
    if performance_data.get('requests_per_second', 0) < 5:
        recommendations.append("🔴 高优先级: 并发处理能力不足")
        recommendations.append("   - 检查数据库连接池配置")
        recommendations.append("   - 优化服务器资源配置")
        recommendations.append("   - 考虑负载均衡")
    
    # 检查系统健康状态
    health_status = performance_data.get('health_status', {})
    unavailable_services = [name for name, status in health_status.items() if not status['available']]
    if unavailable_services:
        recommendations.append(f"🔴 高优先级: 以下服务不可用: {', '.join(unavailable_services)}")
    
    for rec in recommendations:
        print(rec)
    
    return recommendations

def main():
    """主函数"""
    print("🚀 智能助手系统性能优化分析")
    print("=" * 50)
    
    # 1. 检查系统健康状态
    health_status = check_system_health()
    
    # 2. 测试主要API接口响应时间
    print("\n⏱️ 测试主要API接口响应时间...")
    
    api_endpoints = [
        'http://localhost:8000/api/v1/smart-assistant/info',
        'http://localhost:8000/api/v1/smart-assistant/model-config',
        'http://localhost:8000/api/v1/smart-assistant/history'
    ]
    
    api_results = []
    for endpoint in api_endpoints:
        result = test_api_response_time(endpoint)
        api_results.append(result)
        
        status_icon = '✅' if result['success'] else '❌'
        print(f"  {status_icon} {endpoint}: {result['response_time']:.2f}秒")
    
    # 3. 测试智能助手聊天功能性能
    print("\n🤖 测试智能助手聊天功能性能...")
    chat_results = analyze_database_performance()
    
    # 4. 测试并发性能
    concurrent_results = test_concurrent_requests('http://localhost:8000/api/v1/smart-assistant/info', 5)
    
    # 5. 汇总性能数据
    all_response_times = [r['response_time'] for r in api_results if r['success']]
    all_response_times.extend([r['response_time'] for r in chat_results if r['success']])
    
    performance_data = {
        'health_status': health_status,
        'api_results': api_results,
        'chat_results': chat_results,
        'concurrent_results': concurrent_results,
        'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
        'total_tests': len(all_response_times)
    }
    
    # 6. 生成优化建议
    generate_optimization_recommendations(performance_data)
    
    # 7. 输出性能报告
    print("\n📊 性能报告摘要:")
    print(f"  平均响应时间: {performance_data['avg_response_time']:.2f}秒")
    print(f"  并发处理能力: {concurrent_results['requests_per_second']:.1f} 请求/秒")
    print(f"  总测试次数: {performance_data['total_tests']}")
    
    # 检查是否有严重问题
    if performance_data['avg_response_time'] > 5:
        print("\n⚠️ 警告: 系统性能较差，需要立即优化！")
    elif performance_data['avg_response_time'] > 2:
        print("\nℹ️ 提示: 系统性能有待优化")
    else:
        print("\n✅ 系统性能良好")

if __name__ == "__main__":
    main()