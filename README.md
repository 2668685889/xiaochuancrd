# 无用进销存管理系统

现代化的进销存管理系统，采用前后端分离架构，具有扁平化科技感的UI设计。

## 技术栈

### 前端
- React 18+ (函数式组件 + Hooks)
- TypeScript
- Tailwind CSS + Headless UI
- Vite 构建工具

### 后端
- FastAPI (Python Web框架)
- MySQL 8.0+
- SQLAlchemy 2.0 ORM
- JWT + OAuth2 认证

## 项目结构

```
wuyong/
├── frontend/          # 前端项目
├── backend/           # 后端项目
├── shuoming/          # 项目文档
├── migrations/        # 数据库迁移脚本
└── README.md          # 项目说明
```

## 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- MySQL 8.0+

### 启动步骤

1. **启动后端服务**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python3 run.py
```

2. **启动前端服务**
```bash
cd frontend
npm install
npm run dev
```

3. **访问应用**
- 前端: http://localhost:3001
- 后端API文档: http://localhost:8000/docs

## 功能特性

- ✅ 产品管理
- ✅ 库存管理
- ✅ 供应商管理
- ✅ 销售订单管理
- ✅ 采购订单管理
- ✅ Coze API同步配置
- ✅ 实时数据监控
- ✅ 报表分析

## 开发规范

- 前端使用大驼峰命名规范
- 后端使用蛇形命名规范
- API数据映射：前端大驼峰 ↔ 后端蛇形命名
- 代码提交遵循Conventional Commits规范

## 版本历史

- v1.0.0 - 初始版本 (当前版本)

## 许可证

MIT License