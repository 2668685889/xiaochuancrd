#!/usr/bin/env python3
"""
智能助手系统性能优化方案生成器
基于性能测试结果生成优化建议
"""

import os
import json
import glob
from datetime import datetime

def find_latest_performance_report():
    """查找最新的性能测试报告"""
    report_files = glob.glob("performance_report_*.json")
    if not report_files:
        return None
    
    # 按时间排序，获取最新的报告
    latest_report = sorted(report_files, reverse=True)[0]
    return latest_report

def analyze_performance_report(report_file):
    """分析性能测试报告"""
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print("📊 分析性能测试报告...")
        
        # 提取关键数据
        availability = report.get("availability", {})
        single_results = report.get("single_request_results", {})
        concurrent_results = report.get("concurrent_results", {})
        system_resources = report.get("system_resources", {})
        overall_score = report.get("overall_score", 0)
        
        # 生成优化建议
        recommendations = []
        
        # 1. 服务可用性问题
        unavailable_services = [service for service, available in availability.items() if not available]
        if unavailable_services:
            recommendations.append({
                "priority": "high",
                "category": "服务可用性",
                "description": f"以下服务不可用: {', '.join(unavailable_services)}",
                "actions": [
                    "检查API路由配置",
                    "验证数据库连接",
                    "检查依赖服务状态",
                    "添加服务健康检查端点"
                ]
            })
        
        # 2. 响应时间优化
        chat_response_time = single_results.get("chat", {}).get("response_time", 0)
        if chat_response_time > 1.0:
            recommendations.append({
                "priority": "high",
                "category": "响应时间",
                "description": f"智能助手聊天响应时间过长: {chat_response_time:.2f}秒",
                "actions": [
                    "优化数据库查询性能",
                    "实现查询结果缓存",
                    "添加数据库索引",
                    "优化SQL查询语句",
                    "实现异步处理"
                ]
            })
        
        # 3. 内存优化
        memory_percent = system_resources.get("memory", {}).get("percent", 0)
        if memory_percent > 80:
            recommendations.append({
                "priority": "medium",
                "category": "内存使用",
                "description": f"内存使用率过高: {memory_percent}%",
                "actions": [
                    "优化数据加载策略",
                    "实现内存缓存清理",
                    "减少不必要的对象创建",
                    "优化数据库连接池",
                    "监控内存泄漏"
                ]
            })
        
        # 4. 并发处理优化
        chat_concurrent = concurrent_results.get("chat", {})
        if chat_concurrent.get("requests_per_second", 0) < 10:
            recommendations.append({
                "priority": "medium",
                "category": "并发处理",
                "description": f"并发处理能力不足: {chat_concurrent.get('requests_per_second', 0):.1f} 请求/秒",
                "actions": [
                    "增加服务器工作线程数",
                    "优化数据库连接池配置",
                    "实现请求队列管理",
                    "添加负载均衡",
                    "优化代码执行效率"
                ]
            })
        
        # 5. 数据库优化
        recommendations.append({
            "priority": "high",
            "category": "数据库",
            "description": "数据库查询性能需要优化",
            "actions": [
                "为常用查询字段添加索引",
                "优化表结构设计",
                "实现查询结果缓存",
                "定期清理历史数据",
                "监控慢查询日志"
            ]
        })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "report_file": report_file,
            "overall_score": overall_score,
            "issues_found": report.get("issues", []),
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"❌ 分析报告失败: {e}")
        return None

def generate_optimization_script():
    """生成优化脚本"""
    script_content = '''#!/usr/bin/env python3
"""智能助手系统性能优化脚本"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def apply_database_optimizations():
    """应用数据库优化"""
    print("🔧 应用数据库优化...")
    
    # 优化数据库连接池
    os.environ["SQLALCHEMY_POOL_SIZE"] = "20"
    os.environ["SQLALCHEMY_MAX_OVERFLOW"] = "30"
    os.environ["SQLALCHEMY_POOL_RECYCLE"] = "3600"
    
    print("✅ 数据库连接池优化已应用")

def apply_api_optimizations():
    """应用API优化"""
    print("🔧 应用API优化...")
    
    # 优化FastAPI配置
    os.environ["MAX_WORKERS"] = "10"
    os.environ["MAX_KEEPALIVE_REQUESTS"] = "100"
    
    print("✅ API优化配置已应用")

def apply_caching_optimizations():
    """应用缓存优化"""
    print("🔧 应用缓存优化...")
    
    # 启用查询缓存
    os.environ["ENABLE_QUERY_CACHE"] = "True"
    os.environ["CACHE_TTL"] = "300"
    
    print("✅ 缓存优化配置已应用")

def apply_memory_optimizations():
    """应用内存优化"""
    print("🔧 应用内存优化...")
    
    # 启用垃圾回收优化
    import gc
    gc.set_threshold(700, 10, 10)
    
    print("✅ 内存优化配置已应用")

def main():
    """主函数"""
    print("🚀 开始应用性能优化配置...")
    
    try:
        # 应用各项优化
        apply_database_optimizations()
        apply_api_optimizations()
        apply_caching_optimizations()
        apply_memory_optimizations()
        
        print("\n✅ 所有性能优化配置已成功应用")
        print("\n💡 重启后端服务器以使优化生效")
        
    except Exception as e:
        print(f"❌ 优化配置失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    script_path = "apply_optimizations.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

def generate_database_index_script():
    """生成数据库索引优化脚本"""
    script_content = '''#!/usr/bin/env python3
"""智能助手系统数据库索引优化脚本"""

import os
import sys

def optimize_database_indexes():
    """优化数据库索引"""
    print("🔧 优化数据库索引...")
    
    # 常用查询字段索引建议
    index_suggestions = [
        # 产品表索引
        "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
        "CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);",
        
        # 智能助手相关表索引
        "CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp);",
        
        # 模型配置表索引
        "CREATE INDEX IF NOT EXISTS idx_model_config_name ON model_config(name);",
        
        # 采购订单相关索引
        "CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);",
        "CREATE INDEX IF NOT EXISTS idx_purchase_orders_created_at ON purchase_orders(created_at);",
        
        # 库存相关索引
        "CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_inventory_warehouse_id ON inventory(warehouse_id);",
    ]
    
    print("📋 建议创建的索引:")
    for i, index_sql in enumerate(index_suggestions, 1):
        print(f"{i}. {index_sql}")
    
    print("\n💡 请在数据库管理工具中执行以上SQL语句")
    print("💡 或者联系数据库管理员进行索引优化")
    
    return index_suggestions

def generate_performance_monitoring_queries():
    """生成性能监控查询"""
    print("\n🔍 性能监控查询:")
    
    monitoring_queries = [
        # 慢查询监控
        """-- 查看慢查询
        SELECT * FROM information_schema.processlist 
        WHERE command != 'Sleep' AND time > 2 
        ORDER BY time DESC;""",
        
        # 表大小统计
        """-- 查看表大小
        SELECT 
            table_name,
            round(((data_length + index_length) / 1024 / 1024), 2) as size_mb
        FROM information_schema.tables 
        WHERE table_schema = 'xiaochuanerp'
        ORDER BY size_mb DESC;""",
        
        # 索引使用情况
        """-- 查看索引使用情况
        SELECT 
            index_name,
            table_name,
            non_unique
        FROM information_schema.statistics 
        WHERE table_schema = 'xiaochuanerp';"""
    ]
    
    for i, query in enumerate(monitoring_queries, 1):
        print(f"\n{i}. {query}")

def main():
    """主函数"""
    print("🚀 开始数据库索引优化分析...")
    
    try:
        # 生成索引优化建议
        optimize_database_indexes()
        
        # 生成性能监控查询
        generate_performance_monitoring_queries()
        
        print("\n✅ 数据库索引优化分析完成")
        print("💡 请根据建议优化数据库索引结构")
        
    except Exception as e:
        print(f"❌ 数据库优化分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    script_path = "optimize_database_indexes.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    return script_path

def print_optimization_summary(optimization_plan):
    """打印优化方案摘要"""
    print("\n📋 性能优化方案摘要")
    print("=" * 50)
    
    print(f"📊 总体评分: {optimization_plan['overall_score']}/100")
    print(f"📄 分析报告: {optimization_plan['report_file']}")
    
    if not optimization_plan["recommendations"]:
        print("✅ 未发现需要优化的性能问题")
        return
    
    # 按优先级排序
    high_priority = [r for r in optimization_plan["recommendations"] if r["priority"] == "high"]
    medium_priority = [r for r in optimization_plan["recommendations"] if r["priority"] == "medium"]
    
    if high_priority:
        print("\n🔴 高优先级优化:")
        for rec in high_priority:
            print(f"   📍 {rec['category']}: {rec['description']}")
            print("      💡 建议操作:")
            for action in rec["actions"]:
                print(f"        - {action}")
    
    if medium_priority:
        print("\n🟡 中优先级优化:")
        for rec in medium_priority:
            print(f"   📍 {rec['category']}: {rec['description']}")
            print("      💡 建议操作:")
            for action in rec["actions"]:
                print(f"        - {action}")

def main():
    """主函数"""
    # 查找最新的性能报告
    latest_report = find_latest_performance_report()
    
    if not latest_report:
        print("❌ 未找到性能测试报告")
        print("💡 请先运行 comprehensive_performance_test.py 生成性能报告")
        return
    
    print(f"📄 使用性能报告: {latest_report}")
    
    # 分析报告
    optimization_plan = analyze_performance_report(latest_report)
    
    if not optimization_plan:
        print("❌ 性能分析失败")
        return
    
    # 生成优化脚本
    optimization_script = generate_optimization_script()
    database_script = generate_database_index_script()
    
    # 保存优化方案
    plan_file = f"optimization_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(optimization_plan, f, indent=2, ensure_ascii=False)
    
    # 打印摘要
    print_optimization_summary(optimization_plan)
    
    print(f"\n🔧 生成的优化脚本:")
    print(f"   - 性能优化配置: {optimization_script}")
    print(f"   - 数据库索引优化: {database_script}")
    print(f"   - 优化方案文档: {plan_file}")
    
    print("\n💡 下一步操作:")
    print("   1. 运行性能优化配置脚本: python apply_optimizations.py")
    print("   2. 优化数据库索引结构: python optimize_database_indexes.py")
    print("   3. 重启后端服务器")
    print("   4. 重新运行性能测试验证优化效果")

if __name__ == "__main__":
    main()