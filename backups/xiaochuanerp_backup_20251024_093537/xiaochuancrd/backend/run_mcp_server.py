#!/usr/bin/env python3
"""
MCP 服务器启动脚本
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# 加载环境变量 - 优先加载 .env.mcp，如果不存在则加载 .env
mcp_env_path = Path(__file__).parent / ".env.mcp"
if mcp_env_path.exists():
    load_dotenv(mcp_env_path)
    print(f"✅ 加载 MCP 专用环境变量文件: {mcp_env_path}")
else:
    load_dotenv()
    print("⚠️  未找到 MCP 专用环境变量文件，使用默认 .env 文件")

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.mcp_server import app


def main():
    """主函数"""
    # 检查环境变量
    if not os.getenv("DATABASE_URL"):
        print("错误: 未设置 DATABASE_URL 环境变量")
        print("请设置数据库连接字符串，例如:")
        print("export DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/xiaochuanERP")
        sys.exit(1)
    
    print("启动 xiaochuanERP MCP 服务器...")
    print(f"项目根目录: {project_root}")
    print(f"数据库 URL: {os.getenv('DATABASE_URL', '未设置')}")
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False  # 生产环境关闭热重载
    )


if __name__ == "__main__":
    main()