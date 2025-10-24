# 通用Coze同步模板使用说明

## 概述

通用Coze同步模板是一个配置化的数据同步解决方案，支持将不同表单的数据自动同步到Coze平台。该模板具有以下特点：

- **通用性**：支持任意数据表的同步配置
- **配置化**：通过可视化界面配置同步参数
- **批量处理**：支持手动和自动批量同步
- **实时同步**：支持插入、更新、删除操作的实时同步
- **字段选择**：可选择需要同步的特定字段

## 核心功能

### 1. 同步模板创建

支持为任意数据表创建同步配置：

```python
# 创建客户数据同步模板
result = await CozeSyncTemplate.create_sync_template(
    table_name="customers",           # 数据表名
    config_title="客户数据同步",       # 配置标题
    coze_workflow_id="workflow_123",   # Coze工作流ID
    coze_api_url="https://api.coze.cn", # Coze API地址
    coze_api_key="your_api_key",       # Coze API密钥
    selected_fields=[                 # 选择同步字段
        "customer_name", 
        "customer_code", 
        "phone", 
        "email"
    ],
    sync_on_insert=True,              # 同步插入操作
    sync_on_update=True,              # 同步更新操作
    sync_on_delete=False              # 不同步删除操作
)
```

### 2. 手动同步功能

支持手动触发全量数据同步：

```python
# 手动同步所有记录
result = await CozeSyncTemplate.manual_sync_all_records(
    config_uuid=config_uuid,  # 同步配置UUID
    batch_size=100,           # 批次大小
    filters=None              # 数据过滤条件
)
```

### 3. 模板管理

提供完整的模板管理功能：

- **查询模板**：获取所有同步模板列表
- **模板预览**：预览同步数据和字段映射
- **更新模板**：修改同步配置参数
- **删除模板**：移除不需要的同步配置

## API接口

### 1. 创建同步模板

**POST** `/api/v1/coze-sync-templates/`

**参数：**
- `table_name` (string): 数据表名
- `config_title` (string): 配置标题
- `coze_workflow_id` (string): Coze工作流ID
- `coze_api_url` (string, optional): Coze API地址，默认"https://api.coze.cn"
- `coze_api_key` (string, optional): Coze API密钥
- `selected_fields` (array, optional): 选择的字段列表
- `sync_on_insert` (boolean, optional): 是否同步插入操作，默认true
- `sync_on_update` (boolean, optional): 是否同步更新操作，默认true
- `sync_on_delete` (boolean, optional): 是否同步删除操作，默认false
- `created_by` (string, optional): 创建者UUID

**响应：**
```json
{
    "success": true,
    "message": "同步模板创建成功",
    "config": {
        "uuid": "配置UUID",
        "config_title": "配置标题",
        "table_name": "数据表名",
        "coze_workflow_id": "工作流ID",
        "selected_fields": ["字段列表"],
        "enabled": true
    }
}
```

### 2. 手动同步记录

**POST** `/api/v1/coze-sync-templates/{config_uuid}/manual-sync`

**参数：**
- `config_uuid` (path): 同步配置UUID
- `batch_size` (int, optional): 批次大小，默认100
- `filters` (object, optional): 数据过滤条件

**响应：**
```json
{
    "success": true,
    "message": "同步完成，成功同步 X 条记录",
    "records_synced": 10,
    "total_records": 15
}
```

### 3. 获取同步模板列表

**GET** `/api/v1/coze-sync-templates/`

**响应：**
```json
[
    {
        "uuid": "配置UUID",
        "config_title": "配置标题",
        "table_name": "数据表名",
        "coze_workflow_id": "工作流ID",
        "sync_on_insert": true,
        "sync_on_update": true,
        "sync_on_delete": false,
        "selected_fields": ["字段列表"],
        "status": "ACTIVE",
        "last_sync_time": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-15T10:00:00Z"
    }
]
```

### 4. 获取模板预览

**GET** `/api/v1/coze-sync-templates/preview`

**参数：**
- `table_name` (query): 数据表名
- `selected_fields` (query, optional): 选择的字段列表

**响应：**
```json
{
    "success": true,
    "table_name": "customers",
    "table_display_name": "客户表",
    "available_fields": [
        {"name": "customer_name", "type": "string"},
        {"name": "customer_code", "type": "string"}
    ],
    "selected_fields": ["customer_name", "customer_code"],
    "sample_data": [
        {"customer_name": "张三", "customer_code": "C001"}
    ],
    "sample_size": 1
}
```

### 5. 更新同步模板

**PUT** `/api/v1/coze-sync-templates/{config_uuid}`

**参数：**
- `config_uuid` (path): 同步配置UUID
- `updates` (body): 更新字段

### 6. 删除同步模板

**DELETE** `/api/v1/coze-sync-templates/{config_uuid}`

## 使用示例

### 示例1：创建客户数据同步

```python
# 创建客户数据同步模板
result = await CozeSyncTemplate.create_sync_template(
    table_name="customers",
    config_title="客户信息同步",
    coze_workflow_id="customer_sync_workflow",
    selected_fields=["customer_name", "customer_code", "phone", "email", "address"]
)
```

### 示例2：创建产品数据同步

```python
# 创建产品数据同步模板
result = await CozeSyncTemplate.create_sync_template(
    table_name="products",
    config_title="产品信息同步",
    coze_workflow_id="product_sync_workflow",
    selected_fields=["product_name", "product_code", "unit_price", "current_quantity"]
)
```

### 示例3：手动同步供应商数据

```python
# 手动同步供应商数据
result = await CozeSyncTemplate.manual_sync_all_records(
    config_uuid="供应商同步配置UUID",
    batch_size=50
)
```

## 字段映射规则

### 数据库字段到Coze参数的映射

通用同步模板采用以下字段映射规则：

1. **通用规则**：将`uuid`字段映射为`user_id`
2. **直接映射**：其他字段直接使用蛇形命名（如`customer_name`）
3. **类型转换**：
   - `datetime`类型转换为ISO格式字符串
   - `UUID`类型转换为字符串
   - 其他类型保持原样

### 映射示例

**数据库记录：**
```json
{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "customer_name": "张三",
    "customer_code": "C001",
    "phone": "13800138000",
    "created_at": "2024-01-15T10:00:00Z"
}
```

**Coze API参数：**
```json
{
    "workflow_id": "customer_sync_workflow",
    "parameters": {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "customer_name": "张三",
        "customer_code": "C001",
        "phone": "13800138000",
        "created_at": "2024-01-15T10:00:00Z"
    }
}
```

## 错误处理

### 常见错误及解决方案

1. **表不存在错误**
   - 原因：指定的表名不存在于数据库中
   - 解决方案：检查表名拼写，确保表已创建

2. **字段不存在错误**
   - 原因：选择的字段在表中不存在
   - 解决方案：检查字段名拼写，使用模板预览功能验证字段

3. **API连接错误**
   - 原因：Coze API服务器不可达或API密钥无效
   - 解决方案：检查网络连接和API密钥配置

4. **工作流不存在错误**
   - 原因：指定的工作流ID不存在
   - 解决方案：检查工作流ID是否正确

## 最佳实践

### 1. 配置管理
- 为每个业务表创建独立的同步配置
- 使用有意义的配置标题便于管理
- 定期检查同步配置的状态

### 2. 性能优化
- 合理设置批次大小（建议50-200）
- 选择必要的同步字段，避免传输冗余数据
- 启用实时同步时注意数据库性能

### 3. 安全考虑
- 保护API密钥，避免泄露
- 限制敏感字段的同步
- 定期轮换API密钥

### 4. 监控和维护
- 监控同步任务的执行状态
- 记录同步日志便于排查问题
- 定期清理无效的同步配置

## 扩展功能

### 自定义字段映射
如需自定义字段映射规则，可扩展`CozeSyncTemplate`类：

```python
class CustomCozeSyncTemplate(CozeSyncTemplate):
    @classmethod
    async def custom_field_mapping(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """自定义字段映射"""
        mapped_record = {}
        
        # 自定义映射规则
        if "customer_name" in record:
            mapped_record["name"] = record["customer_name"]
        if "customer_code" in record:
            mapped_record["code"] = record["customer_code"]
        
        return mapped_record
```

### 数据过滤
支持基于条件的同步过滤：

```python
# 只同步活跃客户
filters = {
    "is_active": True
}

result = await CozeSyncTemplate.manual_sync_all_records(
    config_uuid=config_uuid,
    filters=filters
)
```

## 总结

通用Coze同步模板提供了一个灵活、可配置的数据同步解决方案，支持多种业务场景的数据同步需求。通过简单的配置即可实现不同表单数据的自动化同步，大大提高了数据集成效率。