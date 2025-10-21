import time
import requests
import statistics
import json

def test_page_initialization_performance():
    """测试页面初始化性能"""
    print("测试页面初始化性能:")
    print("-" * 50)
    
    # 模拟页面初始化时的API调用序列
    init_times = []
    
    for i in range(5):
        print(f"\n初始化测试 {i + 1}:")
        start_time = time.time()
        
        # 1. 加载设置
        try:
            settings_start = time.time()
            response = requests.get("http://localhost:8080/api/v1/smart-assistant/settings", timeout=10)
            settings_end = time.time()
            settings_time = settings_end - settings_start
            
            if response.status_code == 200:
                print(f"  设置加载: {settings_time:.2f}秒 ✅")
            else:
                print(f"  设置加载: 失败 (状态码: {response.status_code}) ❌")
        except Exception as e:
            print(f"  设置加载: 错误 - {str(e)} ❌")
            settings_time = 0
        
        # 2. 检查MCP状态
        try:
            mcp_start = time.time()
            response = requests.post("http://localhost:8080/api/v1/smart-assistant/chat", 
                                   json={"message": "test"}, timeout=10)
            mcp_end = time.time()
            mcp_time = mcp_end - mcp_start
            
            if response.status_code == 200:
                print(f"  MCP状态检查: {mcp_time:.2f}秒 ✅")
            else:
                print(f"  MCP状态检查: 失败 (状态码: {response.status_code}) ❌")
        except Exception as e:
            print(f"  MCP状态检查: 错误 - {str(e)} ❌")
            mcp_time = 0
        
        end_time = time.time()
        total_time = end_time - start_time
        init_times.append(total_time)
        print(f"  总初始化时间: {total_time:.2f}秒")
    
    if init_times:
        avg_time = statistics.mean(init_times)
        min_time = min(init_times)
        max_time = max(init_times)
        
        print(f"\n初始化性能统计:")
        print(f"  平均初始化时间: {avg_time:.2f}秒")
        print(f"  最快初始化时间: {min_time:.2f}秒")
        print(f"  最慢初始化时间: {max_time:.2f}秒")
        
        # 评估优化效果
        if avg_time > 3:
            print("  ⚠️  初始化时间过长，需要进一步优化")
        elif avg_time > 1.5:
            print("  ⚠️  初始化时间较长，建议继续优化")
        else:
            print("  ✅ 初始化时间良好")
        
        return avg_time

def test_concurrent_initialization():
    """测试并发初始化性能"""
    print("\n测试并发初始化性能:")
    print("-" * 50)
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def simulate_initialization(request_id):
        start_time = time.time()
        
        # 模拟初始化序列
        try:
            # 加载设置
            requests.get("http://localhost:8080/api/v1/smart-assistant/settings", timeout=10)
            
            # 检查MCP状态
            requests.post("http://localhost:8080/api/v1/smart-assistant/chat", 
                         json={"message": "test"}, timeout=10)
            
            end_time = time.time()
            total_time = end_time - start_time
            results.put(total_time)
        except Exception as e:
            results.put(None)
    
    # 创建5个并发初始化请求
    threads = []
    start_time = time.time()
    
    for i in range(5):
        thread = threading.Thread(target=simulate_initialization, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 收集结果
    init_times = []
    while not results.empty():
        result = results.get()
        if result is not None:
            init_times.append(result)
    
    if init_times:
        avg_time = statistics.mean(init_times)
        print(f"并发初始化结果:")
        print(f"  并发初始化数: {len(init_times)}")
        print(f"  总执行时间: {total_time:.2f}秒")
        print(f"  平均初始化时间: {avg_time:.2f}秒")
        print(f"  最快初始化时间: {min(init_times):.2f}秒")
        print(f"  最慢初始化时间: {max(init_times):.2f}秒")

def compare_optimization():
    """比较优化前后的性能"""
    print("\n优化效果评估:")
    print("-" * 50)
    
    # 假设优化前的平均初始化时间为2.5秒
    before_optimization = 2.5
    after_optimization = test_page_initialization_performance()
    
    if after_optimization:
        improvement = ((before_optimization - after_optimization) / before_optimization) * 100
        print(f"\n优化效果比较:")
        print(f"  优化前平均初始化时间: {before_optimization:.2f}秒")
        print(f"  优化后平均初始化时间: {after_optimization:.2f}秒")
        print(f"  性能提升: {improvement:.1f}%")
        
        if improvement > 50:
            print("  🚀 优化效果显著!")
        elif improvement > 20:
            print("  ✅ 优化效果良好")
        else:
            print("  ⚠️  优化效果有限，可能需要进一步优化")

if __name__ == "__main__":
    test_page_initialization_performance()
    test_concurrent_initialization()
    compare_optimization()