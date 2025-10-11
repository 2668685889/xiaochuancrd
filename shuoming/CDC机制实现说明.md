# CDC (Change Data Capture) 机制实现说明

## 概述

为了解决新增数据无法第一时间同步的问题，我们实现了基于CDC (Change Data Capture) 的实时数据同步机制。该机制通过数据库触发器捕获数据变化，并通过CDC服务自动处理这些变化，确保数据能够实时同步到Coze平台。

## 架构设计

### 核心组件

1. **数据变化日志表 (data_change_logs)**
   - 存储所有数据表的变化记录
   - 包含表名、记录UUID、操作类型、变化数据等信息

2. **数据库触发器**
   - 为每个业务表创建INSERT、UPDATE、DELETE触发器
   - 自动捕获数据变化并记录到日志表

3. **CDC服务 (CDCService)**
   - 监控数据变化日志
   - 根据同步配置处理变化数据
   - 调用Coze服务进行数据同步

4. **Coze服务集成**
   - 支持字段筛选和配置管理
   - 与CDC服务协同工作

## 实现步骤

### 1. 数据变化日志表

创建了 `data_change_logs` 表来存储所有数据变化：

```sql
CREATE TABLE data_change_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_uuid CHAR(36) NOT NULL,
    operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    change_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed TINYINT DEFAULT 0,
    processed_at TIMESTAMP NULL
);
```

### 2. 数据库触发器

为每个业务表创建了相应的触发器：

- **products表**: `trigger_products_insert`, `trigger_products_update`, `trigger_products_delete`
- **suppliers表**: `trigger_suppliers_insert`, `trigger_suppliers_update`, `trigger_suppliers_delete`
- **inventory_records表**: `trigger_inventory_records_insert`, `trigger_inventory_records_update`, `trigger_inventory_records_delete`

### 3. CDC服务实现

CDC服务 (`/backend/app/services/cdc_service.py`) 主要功能：

- **注册同步配置**: 管理活跃的同步配置
- **监控数据变化**: 定期检查待处理的数据变化
- **处理变化数据**: 根据配置筛选字段并同步到Coze
- **清理机制**: 自动清理已处理的记录

### 4. Coze服务集成

修改了Coze服务 (`/backend/app/services/coze_service.py`) 以支持CDC机制：

- **实时同步重构**: 将原有的轮询机制改为CDC注册机制
- **配置管理**: 在配置启用/禁用时自动注册/注销CDC服务
- **错误处理**: 完善的异常处理和日志记录

## 部署说明

### 数据库迁移

执行迁移脚本创建CDC相关结构：

```bash
# 进入backend目录
cd /Users/hui/trae/wuyong/backend

# 执行迁移脚本
mysql -u your_username -p your_database < migrations/002_create_cdc_tables_and_triggers.sql
```

### 应用启动

CDC服务会在应用启动时自动启动：

```python
# 在app/main.py中自动启动CDC服务
from app.services.cdc_service import start_cdc_service
cdc_task = await start_cdc_service()
```

## 使用说明

### 1. 创建同步配置

通过Coze管理界面创建同步配置时，系统会自动：

- 注册配置到CDC服务
- 开始监控相关表的数据变化

### 2. 数据变化处理流程

1. **数据变化发生** → 数据库触发器捕获变化
2. **记录变化日志** → 写入data_change_logs表
3. **CDC服务检测** → 定期检查待处理变化
4. **配置匹配** → 查找相关的同步配置
5. **数据筛选** → 根据配置筛选字段
6. **同步到Coze** → 调用Coze API进行同步
7. **标记已处理** → 更新处理状态和时间

### 3. 配置管理

- **启用配置**: 自动注册到CDC服务，开始实时同步
- **禁用配置**: 从CDC服务注销，停止实时同步
- **删除配置**: 完全移除配置和相关的CDC注册

## 性能优化

### 1. 批量处理

CDC服务每次处理最多100条记录，避免单条处理的开销。

### 2. 索引优化

为data_change_logs表创建了多个索引：

- `idx_table_name`: 按表名查询
- `idx_record_uuid`: 按记录UUID查询
- `idx_operation_type`: 按操作类型查询
- `idx_created_at`: 按创建时间查询
- `idx_processed`: 按处理状态查询

### 3. 自动清理

实现了自动清理机制：

- 存储过程: `cleanup_processed_changes()`
- 定时事件: `event_cleanup_processed_changes` (每天凌晨2点执行)
- 保留期限: 7天内的已处理记录

## 监控和日志

### 日志记录

CDC服务会记录详细的处理日志：

```
INFO: 注册同步配置: config_id, 表: table_name
INFO: 发现 X 条待处理数据变化
INFO: 处理表 table_name 的 Y 条数据变化，关联 Z 个同步配置
INFO: 配置 config_id 需要处理 N 条数据变化
INFO: 配置 config_id 同步完成，成功: M/N
```

### 健康检查

可以通过CDC服务的 `get_pending_changes_count()` 方法监控待处理变化数量。

## 故障排除

### 常见问题

1. **触发器未生效**
   - 检查MySQL事件调度器是否启用: `SHOW VARIABLES LIKE 'event_scheduler';`
   - 启用事件调度器: `SET GLOBAL event_scheduler = ON;`

2. **数据变化未同步**
   - 检查CDC服务是否正常启动
   - 查看应用日志中的错误信息
   - 验证同步配置是否正确启用

3. **同步性能问题**
   - 检查网络连接和Coze API可用性
   - 监控数据库性能指标
   - 考虑调整批量处理大小

### 日志分析

关键日志位置：

- 应用日志: 查看CDC服务的处理日志
- 数据库日志: 检查触发器执行情况
- Coze API日志: 验证数据同步结果

## 扩展性考虑

### 1. 支持更多表

为新的业务表添加CDC支持：

1. 在迁移脚本中添加新的触发器
2. 确保表有UUID主键和时间戳字段
3. 更新CDC服务的表配置处理逻辑

### 2. 性能优化

- 考虑使用消息队列处理大量变化
- 实现变化数据的增量同步
- 添加重试机制和错误处理

### 3. 监控告警

- 集成到现有的监控系统
- 设置变化积压告警阈值
- 实现自动恢复机制

## 总结

通过实现CDC机制，我们解决了新增数据无法第一时间同步的核心问题。该机制具有以下优势：

- **实时性**: 数据变化立即捕获，无需等待轮询间隔
- **可靠性**: 基于数据库触发器，确保不丢失任何变化
- **灵活性**: 支持字段筛选和配置管理
- **可扩展性**: 易于添加对新表的支持
- **可维护性**: 完善的日志记录和监控机制

这套CDC机制为我们的进销存管理系统提供了可靠的数据同步基础，确保了业务数据的实时性和一致性。