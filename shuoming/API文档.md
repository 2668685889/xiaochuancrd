# 进销存管理系统 - API文档

## 概述

进销存管理系统提供RESTful API接口，采用前后端分离架构。所有API端点都遵循统一的响应格式和错误处理机制。

## 基础信息

### API根路径
```
http://localhost:8000/api/v1
```

### 认证方式
- 使用JWT Bearer Token进行认证
- Token通过登录接口获取
- Token需要在请求头中携带

### 请求头
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

### 响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

#### 错误响应
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "错误描述",
  "details": {}
}
```

## 认证接口

### 用户登录

**POST** `/Auth/Login`

#### 请求参数
```json
{
  "username": "admin",
  "password": "password123"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "isActive": true,
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:30:00Z"
    }
  },
  "message": "登录成功"
}
```

### 获取当前用户信息

**GET** `/Auth/Me`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "isActive": true,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  },
  "message": "获取成功"
}
```

## 产品管理接口

### 获取产品列表

**GET** `/Products`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "productName": "笔记本电脑",
        "productCode": "NB001",
        "unitPrice": 5999.00,
        "currentQuantity": 100,
        "minQuantity": 10,
        "maxQuantity": 500,
        "supplierUuid": "550e8400-e29b-41d4-a716-446655440000",
        "supplierName": "联想集团",
        "isActive": true,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "size": 20,
    "pages": 8
  },
  "message": "获取成功"
}
```

### 获取单个产品

**GET** `/Products/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 产品UUID |

### 创建产品

**POST** `/Products`

#### 请求参数
```json
{
  "productName": "智能手机",
  "productCode": "PH001",
  "unitPrice": 2999.00,
  "currentQuantity": 50,
  "minQuantity": 5,
  "maxQuantity": 200,
  "supplierUuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 更新产品

**PUT** `/Products/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 产品UUID |

#### 请求参数
```json
{
  "productName": "智能手机 Pro",
  "unitPrice": 3999.00,
  "isActive": true
}
```

### 删除产品

**DELETE** `/Products/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 产品UUID |

## 供应商管理接口

### 获取供应商列表

**GET** `/Suppliers`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "supplierName": "联想集团",
        "supplierCode": "LENOVO001",
        "contactPerson": "张三",
        "phone": "13800138000",
        "email": "zhangsan@lenovo.com",
        "address": "北京市海淀区",
        "isActive": true,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取成功"
}
```

### 获取单个供应商

**GET** `/Suppliers/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 供应商UUID |

### 创建供应商

**POST** `/Suppliers`

#### 请求参数
```json
{
  "supplierName": "华为技术有限公司",
  "supplierCode": "HUAWEI001",
  "contactPerson": "李四",
  "phone": "13900139000",
  "email": "lisi@huawei.com",
  "address": "深圳市龙岗区"
}
```

### 更新供应商

**PUT** `/Suppliers/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 供应商UUID |

### 删除供应商

**DELETE** `/Suppliers/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 供应商UUID |

## 库存管理接口

### 获取库存记录列表

**GET** `/Inventory`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| productUuid | string | 否 | 产品UUID |
| changeType | string | 否 | 变动类型 (IN/OUT/ADJUST) |
| startDate | string | 否 | 开始日期 (YYYY-MM-DD) |
| endDate | string | 否 | 结束日期 (YYYY-MM-DD) |
| search | string | 否 | 搜索关键词 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "productUuid": "123e4567-e89b-12d3-a456-426614174000",
        "productName": "笔记本电脑",
        "productCode": "NB001",
        "changeType": "IN",
        "quantityChange": 50,
        "currentQuantity": 150,
        "remark": "采购入库",
        "recordDate": "2024-01-15",
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  },
  "message": "获取成功"
}
```

### 获取单个库存记录

**GET** `/Inventory/{uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uuid | string | 是 | 库存记录UUID |

### 创建库存记录

**POST** `/Inventory`

#### 请求参数
```json
{
  "productUuid": "123e4567-e89b-12d3-a456-426614174000",
  "changeType": "OUT",
  "quantityChange": 10,
  "remark": "销售出库",
  "recordDate": "2024-01-15"
}
```

### 获取库存汇总信息

**GET** `/Inventory/Summary`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "totalProducts": 150,
    "totalValue": 1250000.00,
    "lowStockCount": 5,
    "highStockCount": 3,
    "todayIn": 200,
    "todayOut": 150,
    "lowStockProducts": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "productName": "笔记本电脑",
        "currentQuantity": 5,
        "minQuantity": 10
      }
    ],
    "highStockProducts": [
      {
        "uuid": "323e4567-e89b-12d3-a456-426614174000",
        "productName": "鼠标",
        "currentQuantity": 500,
        "maxQuantity": 300
      }
    ]
  },
  "message": "获取成功"
}
```

### 获取库存预警列表

**GET** `/Inventory/Alerts`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "type": "LOW_STOCK",
        "productUuid": "123e4567-e89b-12d3-a456-426614174000",
        "productName": "笔记本电脑",
        "currentQuantity": 5,
        "minQuantity": 10,
        "severity": "HIGH"
      },
      {
        "type": "HIGH_STOCK",
        "productUuid": "323e4567-e89b-12d3-a456-426614174000",
        "productName": "鼠标",
        "currentQuantity": 500,
        "maxQuantity": 300,
        "severity": "LOW"
      }
    ]
  },
  "message": "获取成功"
}
```

## 错误码说明

### 通用错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| PRODUCT_CODE_EXISTS | 400 | 产品编码已存在 |
| SUPPLIER_CODE_EXISTS | 400 | 供应商编码已存在 |
| INSUFFICIENT_STOCK | 400 | 库存不足 |
| SUPPLIER_HAS_PRODUCTS | 400 | 供应商下有关联产品 |

## 数据格式说明

### 日期时间格式
- 所有日期时间字段使用ISO 8601格式
- 示例：`2024-01-15T10:30:00Z`

### 货币格式
- 所有货币字段使用浮点数格式
- 精确到小数点后两位
- 示例：`5999.00`

### UUID格式
- 所有ID字段使用UUID v4格式
- 示例：`123e4567-e89b-12d3-a456-426614174000`

## 分页说明

### 分页参数
- `page`: 当前页码，从1开始
- `size`: 每页记录数，最大100
- `total`: 总记录数
- `pages`: 总页数

### 分页响应结构
```json
{
  "items": [],      // 当前页数据列表
  "total": 0,       // 总记录数
  "page": 1,        // 当前页码
  "size": 20,       // 每页大小
  "pages": 0        // 总页数
}
```

## 搜索和过滤

### 搜索参数
- `search`: 全局搜索关键词，匹配多个字段
- 支持产品名称、编码、供应商名称等字段搜索

### 过滤参数
- 支持按产品、供应商、日期等条件过滤
- 支持多条件组合过滤

## 排序说明

### 默认排序
- 产品列表：按创建时间倒序
- 供应商列表：按创建时间倒序
- 库存记录：按记录日期倒序

### 自定义排序
- 目前API不支持自定义排序参数
- 如需特殊排序需求，请联系开发团队

## 批量操作

### 批量创建
- 目前不支持批量创建产品/供应商
- 单个创建确保数据一致性

### 批量更新
- 目前不支持批量更新操作
- 需要逐个更新确保数据准确性

## 数据验证规则

### 产品数据验证
- 产品名称：必填，最大长度100字符
- 产品编码：必填，唯一，最大长度50字符
- 单价：必填，大于等于0
- 库存数量：必填，大于等于0

### 供应商数据验证
- 供应商名称：必填，最大长度100字符
- 供应商编码：必填，唯一，最大长度50字符
- 联系人：最大长度50字符
- 邮箱：邮箱格式验证

### 库存记录验证
- 产品UUID：必填，必须存在
- 变动类型：必填，IN/OUT/ADJUST
- 变动数量：必填，大于0
- 记录日期：必填，有效日期

## 性能优化建议

### 查询优化
- 使用分页参数避免大数据量查询
- 合理使用搜索和过滤条件
- 避免频繁的全表扫描

### 缓存策略
- 静态数据可适当缓存
- 动态数据谨慎使用缓存
- 注意缓存失效策略

## 安全注意事项

### 认证安全
- 妥善保管JWT Token
- Token过期时间合理设置
- 使用HTTPS传输敏感数据

### 数据安全
- 实施输入验证和过滤
- 防止SQL注入攻击
- 敏感数据加密存储

### 权限控制
- 基于角色的访问控制
- 操作权限细粒度管理
- 重要操作日志记录

## 版本管理

### API版本
- 当前版本：v1
- 版本号在URL路径中体现
- 向后兼容性保证

### 版本变更
- 重大变更需要升级版本号
- 小版本变更保持兼容
- 废弃接口提供迁移指导

## 监控和日志

### 访问日志
- 记录所有API请求
- 包含请求时间、IP、用户等信息
- 用于安全审计和问题排查

### 错误日志
- 记录系统错误和异常
- 包含详细错误堆栈信息
- 用于系统监控和故障排除

### 性能监控
- API响应时间监控
- 数据库查询性能监控
- 系统资源使用情况监控