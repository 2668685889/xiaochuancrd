# MCP 服务器使用说明

## 概述

MCP (Model Context Protocol) 服务器为 xiaochuanERP 系统提供了自然语言查询数据库的标准接口。通过该服务器，用户可以使用自然语言与数据库进行交互，无需编写复杂的 SQL 查询语句。

## 功能特性

- **自然语言查询**: 使用中文自然语言查询数据库
- **数据分析**: 提供数据分析和趋势预测功能
- **MCP 协议兼容**: 支持标准 MCP 协议，可与其他 MCP 客户端集成
- **DeepSeek AI 集成**: 基于 DeepSeek 大语言模型实现智能查询
- **RESTful API**: 提供标准的 REST API 接口

## 快速开始

### 1. 环境准备

确保系统已安装以下依赖：

- Python 3.8+
- MySQL 8.0+
- DeepSeek API 密钥

### 2. 配置环境变量

复制环境变量配置文件：

```bash
cp backend/.env.mcp.example backend/.env.mcp
```

编辑 `backend/.env.mcp` 文件，配置以下参数：

```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/xiaochuanERP

# DeepSeek API 配置
SQLBOT_LLM_API_KEY=your_deepseek_api_key_here
SQLBOT_LLM_ENDPOINT=https://api.deepseek.com/v1
SQLBOT_LLM_MODEL=deepseek-chat

# MCP 服务器配置
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
```

### 3. 启动服务器

```bash
# 激活虚拟环境（如果使用）
cd /Users/hui/trae/xiaochuanerp/xiaochuancrd/backend

# 安装依赖
pip install -r requirements.txt

# 启动 MCP 服务器
python run_mcp_server.py
```

服务器启动后，将在 `http://localhost:8001` 提供服务。

## API 接口文档

### 基础接口

#### 1. 健康检查

```http
GET /health
```

**响应示例:**
```json
{
  "status": "healthy",
  "service": "MCP MySQL Service",
  "database_connected": true,
  "ai_service_ready": true,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 2. 获取服务能力

```http
GET /capabilities
```

**响应示例:**
```json
{
  "capabilities": [
    {
      "name": "query",
      "description": "自然语言数据查询",
      "parameters": {
        "natural_language_query": "string"
      }
    },
    {
      "name": "analyze",
      "description": "数据分析功能",
      "parameters": {
        "query": "string"
      }
    }
  ],
  "database_info": {
    "type": "mysql",
    "name": "xiaochuanERP",
    "tables": ["products", "sales_orders", "purchase_orders"]
  },
  "ai_service": {
    "provider": "DeepSeek",
    "model": "deepseek-chat"
  }
}
```

### 核心功能接口

#### 1. 自然语言查询

```http
POST /query
Content-Type: application/json

{
  "natural_language_query": "查询所有产品信息",
  "session_id": "optional_session_id"
}
```

**请求参数:**
- `natural_language_query` (必需): 自然语言查询语句
- `session_id` (可选): 会话ID，用于保持对话上下文

**响应示例:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "以下是所有产品信息：\n- 产品A: 库存100件，价格¥100\n- 产品B: 库存50件，价格¥200",
      "metadata": {
        "session_id": "session_123",
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "sqlbot"
      }
    }
  ]
}
```

#### 2. 数据分析

```http
POST /analyze
Content-Type: application/json

{
  "query": "分析销售趋势"
}
```

**响应示例:**
```json
{
  "success": true,
  "analysis": {
    "trend": "上升",
    "insights": ["本月销售额比上月增长20%", "热销产品：产品A"],
    "recommendations": ["增加产品A库存", "优化产品B营销策略"]
  }
}
```

#### 3. 趋势预测

```http
POST /predict
Content-Type: application/json

{
  "data": {
    "period": "next_month",
    "product_id": "123"
  }
}
```

### MCP 协议接口

#### 1. MCP 初始化

```http
POST /mcp/initialize
Content-Type: application/json

{}
```

**响应示例:**
```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "roots": ["mcp"],
    "sampling": {}
  },
  "serverInfo": {
    "name": "xiaochuanERP-mysql-server",
    "version": "1.0.0"
  }
}
```

#### 2. MCP 工具调用

```http
POST /mcp/tools/call
Content-Type: application/json

{
  "name": "query",
  "arguments": {
    "natural_language_query": "查询产品总数"
  }
}
```

## 使用示例

### Python 客户端示例

```python
import asyncio
import aiohttp

class MCPClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
    
    async def query(self, natural_language_query: str):
        async with aiohttp.ClientSession() as session:
            data = {"natural_language_query": natural_language_query}
            async with session.post(f"{self.base_url}/query", json=data) as response:
                return await response.json()

async def main():
    client = MCPClient()
    
    # 查询产品信息
    result = await client.query("查询所有产品信息")
    print(result)
    
    # 分析销售数据
    result = await client.query("分析本月销售情况")
    print(result)

# 运行示例
asyncio.run(main())
```

### cURL 示例

```bash
# 健康检查
curl http://localhost:8001/health

# 自然语言查询
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"natural_language_query": "查询库存不足的产品"}'

# MCP 协议查询
curl -X POST http://localhost:8001/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "query", "arguments": {"natural_language_query": "统计供应商数量"}}'
```

## 测试

### 运行功能测试

```bash
cd /Users/hui/trae/xiaochuanerp/xiaochuancrd/backend
python test_mcp_server.py
```

测试脚本将验证以下功能：
- 健康检查
- 服务能力获取
- MCP 协议初始化
- 自然语言查询
- 数据分析
- MCP 工具调用

## 故障排除

### 常见问题

1. **服务器启动失败**
   - 检查数据库连接配置
   - 验证 DeepSeek API 密钥
   - 查看日志文件获取详细错误信息

2. **查询返回错误**
   - 检查自然语言查询语句是否清晰
   - 验证数据库表结构是否正确
   - 确认 AI 服务是否可用

3. **MCP 协议连接失败**
   - 检查端口是否被占用
   - 验证防火墙设置
   - 确认 MCP 客户端配置

### 日志查看

服务器日志位于标准输出，包含以下信息：
- 服务启动状态
- 数据库连接状态
- AI 服务初始化状态
- 查询处理详情

## 部署建议

### 生产环境配置

1. **安全配置**
   - 使用 HTTPS
   - 配置 API 密钥认证
   - 限制 CORS 来源
   - 启用请求限流

2. **性能优化**
   - 配置数据库连接池
   - 启用查询缓存
   - 优化 AI 服务调用

3. **监控告警**
   - 监控服务健康状态
   - 设置性能指标告警
   - 日志集中管理

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。