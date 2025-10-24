#!/usr/bin/env python3
"""
后端服务器启动与监控脚本
提供自动重启和性能监控功能
"""

import subprocess
import time
import sys
import os
import signal
import psutil
from datetime import datetime

def check_server_health(port=8000):
    """检查服务器健康状态"""
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/api/v1/smart-assistant/info", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_server_memory_usage():
    """获取服务器内存使用情况"""
    try:
        # 查找后端服务器进程
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if 'python' in proc.info['name'].lower() and 'run.py' in ' '.join(proc.cmdline()):
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                return memory_mb
    except:
        pass
    return 0

def start_backend_server():
    """启动后端服务器"""
    backend_dir = "/Users/hui/trae/xiaochuanerp/xiaochuancrd/backend"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动后端服务器...")
    
    try:
        # 使用subprocess启动服务器
        process = subprocess.Popen(
            [sys.executable, "run.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务器启动
        startup_timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < startup_timeout:
            # 检查进程是否还在运行
            if process.poll() is not None:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 服务器进程意外退出")
                return None
            
            # 检查服务器是否就绪
            if check_server_health():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 后端服务器启动成功")
                return process
            
            # 读取输出
            line = process.stdout.readline()
            if line:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
            
            time.sleep(0.5)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 服务器启动超时")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 启动服务器失败: {e}")
        return None

def monitor_server(process):
    """监控服务器运行状态"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 开始监控服务器...")
    
    last_health_check = time.time()
    consecutive_failures = 0
    max_consecutive_failures = 3
    
    try:
        while True:
            # 检查进程状态
            if process.poll() is not None:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 服务器进程已停止")
                return False
            
            # 定期健康检查（每10秒一次）
            current_time = time.time()
            if current_time - last_health_check >= 10:
                if check_server_health():
                    consecutive_failures = 0
                    memory_usage = get_server_memory_usage()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 服务器健康 - 内存使用: {memory_usage:.1f}MB")
                else:
                    consecutive_failures += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 服务器健康检查失败 ({consecutive_failures}/{max_consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 连续健康检查失败，重启服务器")
                        return False
                
                last_health_check = current_time
            
            # 读取服务器输出
            line = process.stdout.readline()
            if line:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⏹️ 收到中断信号，停止监控")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 监控异常: {e}")
        return False

def stop_server(process):
    """停止服务器"""
    if process and process.poll() is None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏹️ 停止服务器...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 服务器已停止")

def main():
    """主函数"""
    print("🔧 智能助手后端服务器监控系统")
    print("=" * 50)
    
    max_restarts = 5
    restart_count = 0
    
    while restart_count < max_restarts:
        restart_count += 1
        print(f"\n🔄 第 {restart_count}/{max_restarts} 次启动尝试...")
        
        # 启动服务器
        process = start_backend_server()
        if not process:
            print("❌ 启动失败，等待后重试...")
            time.sleep(5)
            continue
        
        # 监控服务器
        should_continue = monitor_server(process)
        
        # 停止服务器
        stop_server(process)
        
        if not should_continue:
            print("🔄 服务器异常，准备重启...")
            time.sleep(3)
        else:
            print("✅ 正常退出")
            break
    
    if restart_count >= max_restarts:
        print("❌ 达到最大重启次数，系统可能存在问题")
    else:
        print("✅ 服务器监控结束")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"❌ 系统异常: {e}")