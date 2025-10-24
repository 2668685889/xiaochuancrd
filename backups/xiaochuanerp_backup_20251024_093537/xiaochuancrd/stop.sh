#!/bin/bash

# 进销存管理系统停止脚本
# 停止所有运行的前端和后端服务

echo "🛑 停止进销存管理系统服务..."

# 函数：清理占用端口的进程
cleanup_port() {
    local port=$1
    local service=$2
    
    echo "🧹 清理端口 $port 的占用进程..."
    
    # 获取占用端口的进程PID
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔫 杀死占用端口 $port 的进程 (PID: $pid)..."
        kill -9 $pid 2>/dev/null
        
        # 等待进程完全终止
        sleep 2
        
        # 再次检查端口是否被占用
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ 无法清理端口 $port，请手动检查"
            return 1
        else
            echo "✅ 端口 $port 已成功清理"
            return 0
        fi
    else
        echo "✅ 端口 $port 未被占用"
        return 0
    fi
}

# 停止后端服务
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        # 等待进程结束
        while kill -0 $BACKEND_PID 2>/dev/null; do
            sleep 1
        done
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务未运行"
    fi
    rm -f .backend.pid
else
    echo "⚠️  后端服务PID文件不存在"
fi

# 停止前端服务
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        # 等待进程结束
        while kill -0 $FRONTEND_PID 2>/dev/null; do
            sleep 1
        done
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务未运行"
    fi
    rm -f .frontend.pid
else
    echo "⚠️  前端服务PID文件不存在"
fi

# 清理可能残留的进程
echo "🧹 清理残留进程..."

# 杀死所有相关的Python进程（后端）
pkill -f "python -m app.main" 2>/dev/null && echo "✅ 清理后端残留进程" || echo "⚠️  无后端残留进程"

# 杀死所有相关的Node进程（前端）
pkill -f "vite" 2>/dev/null && echo "✅ 清理前端残留进程" || echo "⚠️  无前端残留进程"

# 强制清理端口占用
echo "🔍 强制清理端口占用..."

# 清理后端端口
cleanup_port 8000 "后端"

# 清理前端端口
cleanup_port 3000 "前端"

echo ""
echo "✅ 所有服务已停止！"