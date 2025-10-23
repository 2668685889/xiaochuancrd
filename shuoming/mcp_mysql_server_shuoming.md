# MCP MySQL 服务器连接机制说明

## 概述

MCP MySQL 服务器是一个基于 Node.js 的 Model Context Protocol 服务器，专门用于让 AI 助手（如 Claude）安全地连接和查询 MySQL 数据库。

## 连接机制详解

### 1. 数据库连接流程

#### 连接配置
- **环境变量配置**：通过 `.env` 文件配置数据库连接参数
- **连接池管理**：使用 `mysql2` 库创建连接池，默认连接数限制为 10
- **多连接方式支持**：支持 TCP/IP 和 Unix Socket 两种连接方式

#### 连接参数
```bash
# 基本连接配置
MYSQL_HOST=localhost          # 数据库主机
MYSQL_PORT=3306              # 数据库端口
MYSQL_USER=root              # 数据库用户名
MYSQL_PASS=your_password     # 数据库密码
MYSQL_DB=your_database       # 默认数据库（可选，支持多数据库模式）

# 安全配置
MYSQL_SSL=false              # SSL 加密连接
```

### 2. 表结构发现机制

#### 自动发现数据库表
MCP 服务器通过查询 MySQL 的 `information_schema` 系统数据库来获取所有表信息：

```sql
-- 获取所有表信息
SELECT
  table_name as name,
  table_schema as `database`,
  table_comment as description,
  table_rows as rowCount,
  data_length as dataSize,
  index_length as indexSize,
  create_time as createTime,
  update_time as updateTime
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
ORDER BY table_schema, table_name
```

#### 获取表字段信息
当需要查看具体表结构时，查询字段信息：

```sql
-- 获取表字段信息
SELECT 
  column_name, 
  data_type,
  is_nullable,
  column_default,
  column_comment
FROM information_schema.columns 
WHERE table_name = ? AND table_schema = ?
```

### 3. 与你的项目集成

#### 当前数据库配置
基于你的项目配置，MCP 服务器可以连接以下数据库：

- **主机**：`localhost`
- **端口**：`3306`
- **用户名**：`root`
- **密码**：`Xiaochuan123!`
- **数据库**：`xiaochuanERP`

#### 支持的数据库操作
- **查询操作**：SELECT 查询
- **写入操作**：INSERT、UPDATE、DELETE（可配置）
- **DDL 操作**：CREATE、ALTER、DROP（可配置）

### 4. 安全特性

#### 权限控制
- **全局权限**：可配置是否允许写操作
- **模式级权限**：可针对不同数据库模式设置不同权限
- **表级权限**：支持细粒度的表操作权限控制

#### SQL 注入防护
- 使用参数化查询
- 输入验证和过滤
- 查询白名单机制

### 5. 运行模式

#### 本地模式（推荐）
- 通过 stdio 与 AI 助手通信
- 低延迟，高安全性
- 适合开发环境

#### 远程 HTTP 模式
- 通过 HTTP 接口提供服务
- 支持 Bearer Token 认证
- 适合生产环境部署

### 6. 与 AI 助手的交互

#### 提供的工具
- `mysql_query`：执行 SQL 查询的主要工具
- 支持复杂的 JOIN 查询、子查询、聚合函数等

#### 资源访问
- 表列表资源：`mysql://tables`
- 表结构资源：`mysql://tables/表名`
- 支持通过 URI 模式访问特定表信息

### 7. 部署方式

#### 快速启动
```bash
# 克隆项目
git clone https://github.com/benborla/mcp-server-mysql.git
cd mcp-server-mysql

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的数据库配置

# 构建项目
npm run build

# 启动服务器
npm start
```

#### Docker 部署
```bash
# 使用 Docker 运行
docker run -d \
  --name mcp-mysql-server \
  -p 3001:3001 \
  -e MYSQL_HOST=localhost \
  -e MYSQL_USER=root \
  -e MYSQL_PASS=your_password \
  benborla/mcp-server-mysql:latest
```

### 8. 监控和日志

#### 日志输出
- 连接状态日志
- 查询执行日志
- 错误和警告日志

#### 性能监控
- 连接池使用情况
- 查询执行时间
- 错误率统计

## 总结

MCP MySQL 服务器通过标准化的 MCP 协议，为 AI 助手提供了安全、高效的数据库访问能力。它能够自动发现数据库结构，支持灵活的权限控制，并且可以与你的现有项目无缝集成。

通过这种方式，AI 助手可以：
1. 自动了解数据库中的所有表和字段结构
2. 安全地执行 SQL 查询
3. 获取实时的数据分析和报告
4. 支持复杂的业务逻辑查询

这种集成方式大大提升了 AI 助手在数据分析和业务处理方面的能力。