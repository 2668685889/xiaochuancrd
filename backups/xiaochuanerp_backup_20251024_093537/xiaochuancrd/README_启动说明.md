# 进销存管理系统 - 一键启动说明

## 快速启动

### 方法一：使用一键启动脚本（推荐）

```bash
# 启动所有服务
./start.sh

# 停止所有服务
./stop.sh

# 查看服务状态
./status.sh
```

### 方法二：手动启动

#### 启动后端服务
```bash
cd backend
source venv/bin/activate
python -m app.main
```

#### 启动前端服务
```bash
cd frontend
npm run dev
```

## 服务信息

- **后端API**: http://localhost:8000
- **前端应用**: http://localhost:3000
- **API文档**: http://localhost:8000/docs

## 脚本功能说明

### start.sh
- 检查端口占用情况
- 自动安装依赖（如果尚未安装）
- 同时启动前端和后端服务
- 保存进程ID到文件
- 显示服务访问地址

### stop.sh
- 停止所有运行的服务
- 清理残留进程
- 释放端口占用
- 删除进程ID文件

### status.sh
- 检查服务运行状态
- 检查端口占用情况
- 测试服务连通性
- 显示服务信息

## 系统要求

- macOS / Linux 系统
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

## 首次运行

如果是首次运行，请确保：

1. 数据库已正确配置（检查 backend/.env 文件）
2. 后端依赖已安装：`cd backend && pip install -r requirements.txt`
3. 前端依赖已安装：`cd frontend && npm install`

一键启动脚本会自动检查并安装缺失的依赖。

## 故障排除

### 端口被占用
如果端口 8000 或 3000 被占用，脚本会提示警告。可以：
- 使用 `./stop.sh` 停止现有服务
- 手动杀死占用端口的进程
- 修改配置文件中的端口号

### 依赖安装失败
如果自动安装依赖失败，可以手动安装：
```bash
# 后端依赖
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 服务无法启动
如果服务启动失败，可以查看详细日志：
```bash
# 后端日志
cd backend && source venv/bin/activate && python -m app.main

# 前端日志
cd frontend && npm run dev
```

## 开发说明

- 后端使用 FastAPI 框架，支持热重载
- 前端使用 Vite 开发服务器，支持热重载
- API 遵循大驼峰命名规范
- 数据库使用蛇形命名规范
- 前后端数据自动映射转换

## 联系方式

如有问题，请查看项目文档或联系开发团队。