#!/bin/bash

# 进销存管理系统状态检查脚本
# 检查前端和后端服务的运行状态

echo "📊 进销存管理系统服务状态检查..."
echo ""

# 检查后端服务状态
echo "🔧 后端服务状态:"
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   ✅ 运行中 (PID: $BACKEND_PID)"
    else
        echo "   ❌ PID文件存在但进程未运行"
    fi
else
    echo "   ⚠️  PID文件不存在"
fi

# 检查后端端口
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ 端口 8000 被占用"
else
    echo "   ❌ 端口 8000 未被占用"
fi

echo ""

# 检查前端服务状态
echo "🎨 前端服务状态:"
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "   ✅ 运行中 (PID: $FRONTEND_PID)"
    else
        echo "   ❌ PID文件存在但进程未运行"
    fi
else
    echo "   ⚠️  PID文件不存在"
fi

# 检查前端端口
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ 端口 3000 被占用"
else
    echo "   ❌ 端口 3000 未被占用"
fi

echo ""

# 检查服务连通性
echo "🔗 服务连通性检查:"

# 检查后端API
if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
    echo "   ✅ 后端API可访问 (http://localhost:8000)"
else
    echo "   ❌ 后端API不可访问"
fi

# 检查前端应用
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "   ✅ 前端应用可访问 (http://localhost:3000)"
else
    echo "   ❌ 前端应用不可访问"
fi

echo ""

# 显示服务信息
echo "📋 服务信息:"
echo "   后端API: http://localhost:8000"
echo "   前端应用: http://localhost:3000"
echo "   API文档: http://localhost:8000/docs"
echo ""

# 显示可用命令
echo "💡 可用命令:"
echo "   ./start.sh  - 启动所有服务"
echo "   ./stop.sh   - 停止所有服务"
echo "   ./status.sh - 查看服务状态"
echo ""