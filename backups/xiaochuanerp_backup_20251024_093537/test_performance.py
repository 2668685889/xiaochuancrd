import time
import requests
import statistics

def test_page_load_performance(url, num_tests=5):
    """测试页面加载性能"""
    print(f"测试页面加载性能: {url}")
    print(f"测试次数: {num_tests}")
    print("-" * 50)
    
    load_times = []
    
    for i in range(num_tests):
        start_time = time.time()
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                load_time = end_time - start_time
                load_times.append(load_time)
                print(f"测试 {i+1}: {load_time:.2f}秒")
            else:
                print(f"测试 {i+1}: 失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"测试 {i+1}: 错误 - {str(e)}")
    
    if load_times:
        avg_time = statistics.mean(load_times)
        min_time = min(load_times)
        max_time = max(load_times)
        
        print("-" * 50)
        print(f"平均加载时间: {avg_time:.2f}秒")
        print(f"最快加载时间: {min_time:.2f}秒")
        print(f"最慢加载时间: {max_time:.2f}秒")
        
        if avg_time > 3:
            print("⚠️  页面加载时间过长，需要进一步优化")
        elif avg_time > 1.5:
            print("⚠️  页面加载时间较长，建议继续优化")
        else:
            print("✅ 页面加载时间良好")
    else:
        print("❌ 所有测试均失败")

if __name__ == "__main__":
    # 测试前端页面
    test_page_load_performance("http://localhost:3001/smart-assistant", 5)
    
    # 测试后端API
    print("\n测试后端API性能:")
    api_url = "http://localhost:8080/api/v1/smart-assistant/settings"
    
    api_times = []
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.get(api_url, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                load_time = end_time - start_time
                api_times.append(load_time)
                print(f"API测试 {i+1}: {load_time:.2f}秒")
            else:
                print(f"API测试 {i+1}: 失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"API测试 {i+1}: 错误 - {str(e)}")
    
    if api_times:
        avg_api_time = statistics.mean(api_times)
        print(f"平均API响应时间: {avg_api_time:.2f}秒")