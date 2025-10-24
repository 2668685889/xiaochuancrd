#!/usr/bin/env python3
"""
智能助手系统综合性能测试脚本
提供详细的性能分析和优化建议
"""

import asyncio
import time
import requests
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import statistics
from typing import Dict, List, Any

class PerformanceAnalyzer:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    def check_service_availability(self) -> Dict[str, bool]:
        """检查各个服务的可用性"""
        services = {
            "smart_assistant_info": "/api/v1/smart-assistant/info",
            "model_config": "/api/v1/model-config",
            "chat_history": "/api/v1/chat-history",
            "chat_endpoint": "/api/v1/smart-assistant/chat",
            "products": "/api/v1/products",
        }
        
        availability = {}
        for service_name, endpoint in services.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                availability[service_name] = response.status_code == 200
                print(f"✅ {service_name}: {'可用' if availability[service_name] else '不可用'}")
            except Exception as e:
                availability[service_name] = False
                print(f"❌ {service_name}: 连接失败 - {e}")
        
        return availability
    
    def test_single_request(self, endpoint: str, payload: Dict = None) -> Dict[str, Any]:
        """测试单个请求的性能"""
        start_time = time.time()
        try:
            if payload:
                response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=30)
            else:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "response_size": len(response.content),
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def test_concurrent_requests(self, endpoint: str, num_requests: int = 10, payload: Dict = None) -> Dict[str, Any]:
        """测试并发请求性能"""
        print(f"🚀 测试 {num_requests} 个并发请求到 {endpoint}")
        
        start_time = time.time()
        response_times = []
        success_count = 0
        
        def make_request(request_id):
            return self.test_single_request(endpoint, payload)
        
        with ThreadPoolExecutor(max_workers=min(num_requests, 20)) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if result["success"]:
                    success_count += 1
                    response_times.append(result["response_time"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            requests_per_second = success_count / total_time if total_time > 0 else 0
        else:
            avg_response_time = min_response_time = max_response_time = 0
            requests_per_second = 0
        
        return {
            "total_requests": num_requests,
            "successful_requests": success_count,
            "success_rate": success_count / num_requests if num_requests > 0 else 0,
            "total_time": total_time,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "requests_per_second": requests_per_second,
            "response_times": response_times
        }
    
    def get_system_resources(self) -> Dict[str, Any]:
        """获取系统资源使用情况"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 查找后端进程
        backend_process = None
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            if 'python' in proc.info['name'].lower():
                try:
                    cmdline = ' '.join(proc.cmdline())
                    if 'run.py' in cmdline:
                        backend_process = proc
                        break
                except:
                    continue
        
        backend_info = {}
        if backend_process:
            backend_info = {
                "pid": backend_process.info['pid'],
                "memory_percent": backend_process.info['memory_percent'],
                "cpu_percent": backend_process.info['cpu_percent'],
                "memory_mb": backend_process.memory_info().rss / 1024 / 1024
            }
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "used_gb": memory.used / 1024 / 1024 / 1024,
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / 1024 / 1024 / 1024,
                "used_gb": disk.used / 1024 / 1024 / 1024,
                "percent": disk.percent
            },
            "backend_process": backend_info
        }
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """分析数据库性能"""
        # 测试数据库查询性能
        test_queries = [
            {"query": "获取产品数量", "endpoint": "/api/v1/products", "method": "GET"},
            {"query": "获取智能助手信息", "endpoint": "/api/v1/smart-assistant/info", "method": "GET"},
        ]
        
        db_performance = {}
        for query_info in test_queries:
            result = self.test_single_request(query_info["endpoint"])
            db_performance[query_info["query"]] = result
        
        return db_performance
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合性能测试"""
        print("🔧 开始智能助手系统综合性能测试")
        print("=" * 60)
        
        # 1. 检查服务可用性
        print("\n1. 📡 检查服务可用性")
        availability = self.check_service_availability()
        
        # 2. 系统资源检查
        print("\n2. 💻 系统资源检查")
        system_resources = self.get_system_resources()
        print(f"   CPU使用率: {system_resources['cpu_percent']}%")
        print(f"   内存使用率: {system_resources['memory']['percent']}%")
        print(f"   磁盘使用率: {system_resources['disk']['percent']}%")
        
        if system_resources['backend_process']:
            print(f"   后端进程内存: {system_resources['backend_process']['memory_mb']:.1f}MB")
        
        # 3. 单请求性能测试
        print("\n3. ⚡ 单请求性能测试")
        single_request_results = {}
        
        # 测试智能助手聊天
        chat_payload = {
            "message": "查询所有产品信息",
            "session_id": "performance_test_session"
        }
        
        chat_result = self.test_single_request("/api/v1/smart-assistant/chat", chat_payload)
        single_request_results["chat"] = chat_result
        
        if chat_result["success"]:
            print(f"   智能助手聊天: {chat_result['response_time']:.3f}秒")
        else:
            print(f"   智能助手聊天: 失败 - {chat_result.get('error', '未知错误')}")
        
        # 测试产品查询
        products_result = self.test_single_request("/api/v1/products")
        single_request_results["products"] = products_result
        
        if products_result["success"]:
            print(f"   产品查询: {products_result['response_time']:.3f}秒")
        else:
            print(f"   产品查询: 失败 - {products_result.get('error', '未知错误')}")
        
        # 4. 并发性能测试
        print("\n4. 🔥 并发性能测试")
        concurrent_results = {}
        
        # 并发聊天请求测试
        chat_concurrent = self.test_concurrent_requests(
            "/api/v1/smart-assistant/chat", 
            num_requests=5, 
            payload=chat_payload
        )
        concurrent_results["chat"] = chat_concurrent
        
        print(f"   并发聊天请求:")
        print(f"     - 成功率: {chat_concurrent['success_rate']*100:.1f}%")
        print(f"     - 平均响应时间: {chat_concurrent['avg_response_time']:.3f}秒")
        print(f"     - 吞吐量: {chat_concurrent['requests_per_second']:.1f} 请求/秒")
        
        # 并发产品查询测试
        products_concurrent = self.test_concurrent_requests("/api/v1/products", num_requests=10)
        concurrent_results["products"] = products_concurrent
        
        print(f"   并发产品查询:")
        print(f"     - 成功率: {products_concurrent['success_rate']*100:.1f}%")
        print(f"     - 平均响应时间: {products_concurrent['avg_response_time']:.3f}秒")
        print(f"     - 吞吐量: {products_concurrent['requests_per_second']:.1f} 请求/秒")
        
        # 5. 数据库性能分析
        print("\n5. 🗄️ 数据库性能分析")
        db_performance = self.analyze_database_performance()
        
        # 6. 生成性能报告
        print("\n6. 📊 性能分析报告")
        performance_report = self.generate_performance_report(
            availability, system_resources, single_request_results, concurrent_results, db_performance
        )
        
        return performance_report
    
    def generate_performance_report(self, availability, system_resources, single_results, concurrent_results, db_performance) -> Dict[str, Any]:
        """生成性能分析报告"""
        
        # 计算总体评分
        availability_score = sum(availability.values()) / len(availability) * 100
        
        # 响应时间评分
        response_times = []
        for result in single_results.values():
            if result["success"]:
                response_times.append(result["response_time"])
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        response_time_score = max(0, 100 - (avg_response_time * 20))  # 每0.05秒扣1分
        
        # 并发性能评分
        success_rates = [result["success_rate"] for result in concurrent_results.values()]
        avg_success_rate = statistics.mean(success_rates) if success_rates else 0
        concurrency_score = avg_success_rate * 100
        
        # 系统资源评分
        resource_score = max(0, 100 - system_resources["cpu_percent"] - system_resources["memory"]["percent"] / 2)
        
        # 总体评分
        overall_score = (availability_score + response_time_score + concurrency_score + resource_score) / 4
        
        # 问题识别
        issues = []
        
        if availability_score < 100:
            unavailable_services = [service for service, available in availability.items() if not available]
            issues.append(f"服务不可用: {', '.join(unavailable_services)}")
        
        if avg_response_time > 1.0:
            issues.append(f"响应时间过长: {avg_response_time:.2f}秒")
        
        if avg_success_rate < 0.9:
            issues.append(f"并发成功率低: {avg_success_rate*100:.1f}%")
        
        if system_resources["cpu_percent"] > 80:
            issues.append(f"CPU使用率过高: {system_resources['cpu_percent']}%")
        
        if system_resources["memory"]["percent"] > 80:
            issues.append(f"内存使用率过高: {system_resources['memory']['percent']}%")
        
        # 优化建议
        recommendations = []
        
        if issues:
            if "服务不可用" in str(issues):
                recommendations.append("检查服务配置和数据库连接")
            if "响应时间过长" in str(issues):
                recommendations.append("优化数据库查询和API响应")
            if "并发成功率低" in str(issues):
                recommendations.append("增加服务器资源和优化并发处理")
            if any("使用率过高" in issue for issue in issues):
                recommendations.append("优化资源使用和考虑水平扩展")
        else:
            recommendations.append("系统性能良好，继续保持监控")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(overall_score, 1),
            "availability_score": round(availability_score, 1),
            "response_time_score": round(response_time_score, 1),
            "concurrency_score": round(concurrency_score, 1),
            "resource_score": round(resource_score, 1),
            "availability": availability,
            "system_resources": system_resources,
            "single_request_results": single_results,
            "concurrent_results": concurrent_results,
            "db_performance": db_performance,
            "issues": issues,
            "recommendations": recommendations
        }
        
        # 打印报告摘要
        print(f"\n📈 性能评分摘要:")
        print(f"   总体评分: {report['overall_score']}/100")
        print(f"   可用性: {report['availability_score']}/100")
        print(f"   响应时间: {report['response_time_score']}/100")
        print(f"   并发性能: {report['concurrency_score']}/100")
        print(f"   资源使用: {report['resource_score']}/100")
        
        if issues:
            print(f"\n⚠️ 发现的问题:")
            for issue in issues:
                print(f"   - {issue}")
        
        print(f"\n💡 优化建议:")
        for recommendation in recommendations:
            print(f"   - {recommendation}")
        
        # 保存详细报告
        report_filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_filename}")
        
        return report

def main():
    """主函数"""
    analyzer = PerformanceAnalyzer()
    
    try:
        report = analyzer.run_comprehensive_test()
        
        # 根据评分给出最终建议
        print("\n" + "=" * 60)
        if report["overall_score"] >= 80:
            print("✅ 系统性能优秀")
        elif report["overall_score"] >= 60:
            print("⚠️ 系统性能良好，有优化空间")
        else:
            print("❌ 系统性能需要优化")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")

if __name__ == "__main__":
    main()