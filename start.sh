#!/bin/bash

# 进销存管理系统一键启动脚本
# 同时启动前端和后端服务

echo "🚀 启动进销存管理系统..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录下运行此脚本"
    exit 1
fi

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用，$service 服务可能已在运行"
        return 1
    fi
    return 0
}

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

# 检查并清理后端端口 8000
if check_port 8000 "后端"; then
    echo "✅ 后端端口 8000 可用"
else
    echo "🔄 尝试清理后端端口 8000..."
    if cleanup_port 8000 "后端"; then
        echo "✅ 后端端口 8000 清理成功"
    else
        echo "❌ 后端端口 8000 清理失败，请手动处理"
        exit 1
    fi
fi

# 检查并清理前端端口 3000
if check_port 3000 "前端"; then
    echo "✅ 前端端口 3000 可用"
else
    echo "🔄 尝试清理前端端口 3000..."
    if cleanup_port 3000 "前端"; then
        echo "✅ 前端端口 3000 清理成功"
    else
        echo "❌ 前端端口 3000 清理失败，请手动处理"
        exit 1
    fi
fi

echo "📦 安装依赖（如果尚未安装）..."

# 检查并安装后端依赖
if [ ! -d "backend/venv" ]; then
    echo "🔧 设置后端Python虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ 后端虚拟环境已存在"
fi

# 检查并安装前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "🔧 安装前端依赖..."
    cd frontend
    npm install
    cd ..
else
    echo "✅ 前端依赖已存在"
fi

echo "🌟 启动服务..."

# 启动后端服务
echo "🔧 启动后端服务 (端口 8000)..."
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!
cd ..

# 等待后端服务启动
sleep 3

# 启动前端服务
echo "🎨 启动前端服务 (端口 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 保存进程ID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ 服务启动完成！"
echo ""
echo "📊 服务信息："
echo "   后端API: http://localhost:8000"
echo "   前端应用: http://localhost:3000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🛑 停止服务请运行: ./stop.sh"
echo "📋 查看服务状态请运行: ./status.sh"
echo ""

# 等待用户中断
echo "按 Ctrl+C 停止所有服务..."

# 设置信号处理
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo "✅ 服务已停止"; exit 0' INT

# 等待进程
wait $BACKEND_PID $FRONTEND_PID