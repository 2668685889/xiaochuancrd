#!/bin/bash

# 进销存管理系统一键启动脚本
# 同时启动前端和后端服务

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info "🚀 启动进销存管理系统..."

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    log_error "请在项目根目录下运行此脚本"
    exit 1
fi

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        local process_name=$(ps -p $pid -o comm= 2>/dev/null || echo "未知进程")
        log_warning "端口 $port 已被占用 ($process_name, PID: $pid)，$service 服务可能已在运行"
        return 1
    fi
    return 0
}

# 函数：清理占用端口的进程
cleanup_port() {
    local port=$1
    local service=$2
    
    log_info "清理端口 $port 的占用进程..."
    
    # 获取占用端口的进程PID
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        local process_name=$(ps -p $pid -o comm= 2>/dev/null || echo "未知进程")
        log_warning "杀死占用端口 $port 的进程 ($process_name, PID: $pid)..."
        
        # 尝试优雅终止
        kill $pid 2>/dev/null
        sleep 1
        
        # 如果进程仍在运行，强制终止
        if ps -p $pid > /dev/null 2>&1; then
            log_warning "进程仍在运行，强制终止..."
            kill -9 $pid 2>/dev/null
        fi
        
        # 等待进程完全终止
        sleep 2
        
        # 再次检查端口是否被占用
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_error "无法清理端口 $port，请手动检查"
            return 1
        else
            log_success "端口 $port 已成功清理"
            return 0
        fi
    else
        log_success "端口 $port 未被占用"
        return 0
    fi
}

# 自动清理端口函数
auto_cleanup_ports() {
    local ports=("8000" "3000" "8001")
    local services=("后端" "前端" "MCP")
    
    for i in "${!ports[@]}"; do
        local port="${ports[$i]}"
        local service="${services[$i]}"
        
        if check_port $port "$service"; then
            log_success "$service 端口 $port 可用"
        else
            log_info "尝试清理 $service 端口 $port..."
            if cleanup_port $port "$service"; then
                log_success "$service 端口 $port 清理成功"
            else
                log_error "$service 端口 $port 清理失败，请手动处理"
                exit 1
            fi
        fi
    done
}

log_info "开始自动端口清理..."
auto_cleanup_ports

# 自动安装依赖函数
auto_install_dependencies() {
    log_info "检查并安装依赖..."
    
    # 检查并安装后端依赖
    if [ ! -d "backend/venv" ]; then
        log_info "设置后端Python虚拟环境..."
        cd backend
        if python3 -m venv venv; then
            source venv/bin/activate
            if pip install -r requirements.txt; then
                log_success "后端依赖安装成功"
            else
                log_error "后端依赖安装失败"
                cd ..
                return 1
            fi
        else
            log_error "后端虚拟环境创建失败"
            cd ..
            return 1
        fi
        cd ..
    else
        log_success "后端虚拟环境已存在"
    fi
    
    # 检查并安装前端依赖
    if [ ! -d "frontend/node_modules" ]; then
        log_info "安装前端依赖..."
        cd frontend
        if npm install; then
            log_success "前端依赖安装成功"
        else
            log_error "前端依赖安装失败"
            cd ..
            return 1
        fi
        cd ..
    else
        log_success "前端依赖已存在"
    fi
    
    return 0
}

auto_install_dependencies

# 自动启动服务函数
auto_start_services() {
    log_info "启动服务..."
    
    # 启动后端服务
    log_info "启动后端服务 (端口 8000)..."
    cd backend
    source venv/bin/activate
    python -m app.main &
    BACKEND_PID=$!
    log_success "后端服务启动成功 (PID: $BACKEND_PID)"
    cd ..
    
    # 等待后端服务启动
    log_info "等待后端服务启动..."
    local backend_ready=false
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            backend_ready=true
            log_success "后端服务已就绪"
            break
        fi
        sleep 1
    done
    
    if [ "$backend_ready" = false ]; then
        log_warning "后端服务启动较慢，继续启动其他服务..."
    fi
    
    # 启动MCP服务
    log_info "启动MCP服务 (端口 8001)..."
    cd backend
    source venv/bin/activate
    python run_mcp_server.py &
    MCP_PID=$!
    log_success "MCP服务启动成功 (PID: $MCP_PID)"
    cd ..
    
    # 等待MCP服务启动
    log_info "等待MCP服务启动..."
    local mcp_ready=false
    for i in {1..20}; do
        if curl -s http://localhost:8001/health >/dev/null 2>&1; then
            mcp_ready=true
            log_success "MCP服务已就绪"
            break
        fi
        sleep 1
    done
    
    if [ "$mcp_ready" = false ]; then
        log_warning "MCP服务启动较慢，继续启动前端..."
    fi
    
    # 启动前端服务
    log_info "启动前端服务 (端口 3000)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    log_success "前端服务启动成功 (PID: $FRONTEND_PID)"
    cd ..
    
    return 0
}

auto_start_services

# 保存进程ID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid
echo $MCP_PID > .mcp.pid

# 显示启动信息
log_success "服务启动完成！"
echo ""
echo "📊 ${BLUE}服务信息：${NC}"
echo "   ${GREEN}后端API:${NC} http://localhost:8000"
echo "   ${GREEN}前端应用:${NC} http://localhost:3000"
echo "   ${GREEN}MCP服务:${NC} http://localhost:8001"
echo "   ${GREEN}API文档:${NC} http://localhost:8000/docs"
echo ""
echo "🛑 ${YELLOW}停止服务请运行:${NC} ./stop.sh"
echo "📋 ${YELLOW}查看服务状态请运行:${NC} ./status.sh"
echo ""

# 健康检查函数
health_check() {
    log_info "进行最终健康检查..."
    
    local backend_healthy=false
    local frontend_healthy=false
    local mcp_healthy=false
    
    # 检查后端服务
    for i in {1..10}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            backend_healthy=true
            log_success "后端服务健康检查通过"
            break
        fi
        sleep 2
    done
    
    if [ "$backend_healthy" = false ]; then
        log_warning "后端服务健康检查失败，但服务可能仍在启动中"
    fi
    
    # 检查MCP服务
    for i in {1..10}; do
        if curl -s http://localhost:8001/health >/dev/null 2>&1; then
            mcp_healthy=true
            log_success "MCP服务健康检查通过"
            break
        fi
        sleep 2
    done
    
    if [ "$mcp_healthy" = false ]; then
        log_warning "MCP服务健康检查失败，但服务可能仍在启动中"
    fi
    
    # 检查前端服务
    for i in {1..10}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            frontend_healthy=true
            log_success "前端服务健康检查通过"
            break
        fi
        sleep 2
    done
    
    if [ "$frontend_healthy" = false ]; then
        log_warning "前端服务健康检查失败，但服务可能仍在启动中"
    fi
    
    if [ "$backend_healthy" = true ] && [ "$frontend_healthy" = true ] && [ "$mcp_healthy" = true ]; then
        log_success "所有服务健康检查通过！系统已完全就绪。"
    else
        log_warning "部分服务健康检查未通过，但系统已启动完成。"
    fi
}

health_check

# 设置信号处理
trap 'echo ""; log_info "正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID $MCP_PID 2>/dev/null; rm -f .backend.pid .frontend.pid .mcp.pid; log_success "服务已停止"; exit 0' INT

log_info "按 Ctrl+C 停止所有服务..."

# 等待进程
wait $BACKEND_PID $FRONTEND_PID $MCP_PID