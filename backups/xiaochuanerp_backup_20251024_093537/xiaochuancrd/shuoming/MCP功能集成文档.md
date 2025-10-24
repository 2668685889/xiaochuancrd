# MCP 功能集成文档

## 概述

本项目已成功将 SQLBot 智能助手功能迁移至 MCP (Model Context Protocol) 架构，实现了更灵活、可扩展的智能助手服务。

## 集成内容

### 前端修改

1. **SmartAssistantPage 页面**
   - 将页面标题从 "SQLBot 智能助手" 改为 "MCP 智能助手"
   - 移除了所有 SQLBot 相关的 API 导入和使用

2. **RecommendQuestions 组件**
   - 创建了新的 MCP API 服务类 (`mcpApi.ts`)
   - 将 SQLBot API 调用替换为 MCP API 调用
   - 保持了原有的流式响应处理逻辑

### 后端修改

1. **路由层** (`smart_assistant.py`)
   - 将 SQLBot 服务替换为 MCP 服务
   - 保持了相同的 API 接口规范

2. **服务层**
   - 创建了 `mcp_service.py` 实现智能助手功能
   - 支持与 MCP 服务器的通信

### MCP 服务器

- 服务器地址：http://localhost:8000
- 支持的工具：
  - `query_database`: 数据库查询
  - `analyze_data`: 数据分析
- 健康检查接口：`/health`

## 技术架构

```
前端 (React + TypeScript)
    ↓
MCP API 服务层 (mcpApi.ts)
    ↓
后端 API 路由 (smart_assistant.py)
    ↓
MCP 服务层 (mcp_service.py)
    ↓
MCP 服务器 (localhost:8000)
```

## API 接口

### 推荐问题生成

**端点**: `POST /api/v1/smart-assistant/recommend-questions`

**请求体**:
```json
{
  "user_input": "用户输入文本"
}
```

**响应**: 流式响应，包含思考过程和推荐问题

### 健康检查

**端点**: `GET /api/v1/smart-assistant/health`

**响应**:
```json
{
  "status": "running",
  "tools": ["query_database", "analyze_data"]
}
```

## 启动流程

1. **启动 MCP 服务器**
   ```bash
   cd /Users/hui/trae/xiaochuanerp/xiaochuancrd/backend
   python run.py
   ```

2. **启动前端开发服务器**
   ```bash
   cd /Users/hui/trae/xiaochuanerp/xiaochuancrd/frontend
   npm run dev
   ```

3. **访问应用**
   - 前端地址：http://localhost:3000
   - 后端地址：http://localhost:8000

## 优势

1. **标准化**: 使用 MCP 协议，与多种 AI 模型兼容
2. **可扩展**: 易于添加新的工具和功能
3. **模块化**: 前后端分离，便于维护
4. **流式响应**: 提供更好的用户体验

## 注意事项

- 确保 MCP 服务器在启动前端之前运行
- 检查网络连接，确保前端能访问后端 API
- 监控服务器日志，及时处理错误

## 后续优化

- 添加更多 MCP 工具支持
- 实现更复杂的智能助手功能
- 优化错误处理和重试机制
- 添加性能监控和日志记录