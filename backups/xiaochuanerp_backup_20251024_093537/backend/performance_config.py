"""
性能优化配置文件
针对智能助手系统的性能优化设置
"""

import os
from typing import Dict, Any

# 数据库连接池配置
DATABASE_POOL_CONFIG = {
    "pool_size": 20,  # 连接池大小
    "max_overflow": 30,  # 最大溢出连接数
    "pool_pre_ping": True,  # 连接前检查
    "pool_recycle": 3600,  # 连接回收时间（秒）
}

# FastAPI 性能配置
FASTAPI_CONFIG = {
    "max_workers": 10,  # 最大工作线程数
    "max_keepalive_requests": 100,  # 最大保持连接请求数
    "timeout_keep_alive": 5,  # 保持连接超时时间
}

# SQL查询优化配置
SQL_OPTIMIZATION_CONFIG = {
    "query_timeout": 30,  # 查询超时时间（秒）
    "max_result_size": 1000,  # 最大结果集大小
    "enable_query_cache": True,  # 启用查询缓存
    "cache_ttl": 300,  # 缓存生存时间（秒）
}

# 智能助手性能配置
SMART_ASSISTANT_CONFIG = {
    "max_concurrent_queries": 5,  # 最大并发查询数
    "query_batch_size": 10,  # 查询批处理大小
    "enable_response_caching": True,  # 启用响应缓存
    "response_cache_ttl": 600,  # 响应缓存生存时间（秒）
}

# 日志配置（性能优化）
LOGGING_CONFIG = {
    "level": "WARNING",  # 日志级别
    "disable_sql_logging": True,  # 禁用SQL日志
    "enable_performance_logging": True,  # 启用性能日志
    "slow_query_threshold": 2.0,  # 慢查询阈值（秒）
}

# 内存优化配置
MEMORY_OPTIMIZATION_CONFIG = {
    "enable_garbage_collection": True,  # 启用垃圾回收
    "gc_threshold": (700, 10, 10),  # 垃圾回收阈值
    "max_memory_usage_mb": 500,  # 最大内存使用量（MB）
}

def get_performance_config() -> Dict[str, Any]:
    """获取性能优化配置"""
    config = {
        "database": DATABASE_POOL_CONFIG,
        "fastapi": FASTAPI_CONFIG,
        "sql_optimization": SQL_OPTIMIZATION_CONFIG,
        "smart_assistant": SMART_ASSISTANT_CONFIG,
        "logging": LOGGING_CONFIG,
        "memory": MEMORY_OPTIMIZATION_CONFIG,
    }
    
    # 根据环境变量调整配置
    if os.getenv("ENVIRONMENT") == "production":
        config["database"]["pool_size"] = 50
        config["database"]["max_overflow"] = 100
        config["fastapi"]["max_workers"] = 50
        config["smart_assistant"]["max_concurrent_queries"] = 20
    
    return config

def apply_performance_optimizations():
    """应用性能优化设置"""
    config = get_performance_config()
    
    # 应用数据库连接池优化
    os.environ["SQLALCHEMY_POOL_SIZE"] = str(config["database"]["pool_size"])
    os.environ["SQLALCHEMY_MAX_OVERFLOW"] = str(config["database"]["max_overflow"])
    os.environ["SQLALCHEMY_POOL_RECYCLE"] = str(config["database"]["pool_recycle"])
    
    # 应用FastAPI优化
    os.environ["MAX_WORKERS"] = str(config["fastapi"]["max_workers"])
    os.environ["MAX_KEEPALIVE_REQUESTS"] = str(config["fastapi"]["max_keepalive_requests"])
    
    print("✅ 性能优化配置已应用")
    return config

if __name__ == "__main__":
    # 测试配置
    config = apply_performance_optimizations()
    print("性能优化配置:")
    for section, settings in config.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")