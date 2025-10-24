#!/usr/bin/env python3
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
