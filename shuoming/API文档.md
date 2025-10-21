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

### 命名约定
- **后端数据库字段**：使用蛇形命名法（snake_case），如 `product_name`, `product_code`, `supplier_uuid`
- **前端变量命名**：使用大驼峰命名法（PascalCase），如 `ProductName`, `ProductCode`, `SupplierUuid`
- **API路径参数**：使用蛇形命名法（snake_case），如 `product_uuid`, `category_uuid`, `order_uuid`
- **API查询参数**：使用蛇形命名法（snake_case），如 `operation_type`, `operation_module`, `operator_name`
- **API响应字段**：后端返回蛇形命名，前端自动转换为大驼峰命名
- **API路径**：使用帕斯卡命名法（PascalCase），如 `/Products`, `/SalesOrders`

#### 命名转换机制
系统内置命名转换函数：
- 后端：`snake_to_camel()` 和 `camel_to_snake()` 函数
- 前端：`snakeToCamel()` 和 `camelToSnake()` 函数
- 所有API调用都会自动进行命名风格转换

## 认证接口

### 用户登录

**POST** `/auth/login`

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
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "系统管理员",
      "is_active": true,
      "is_superuser": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  },
  "message": "登录成功"
}
```

### 刷新访问令牌

**POST** `/auth/refresh`

#### 响应示例
```json
{
  "success": false,
  "data": {},
  "message": "令牌已过期，请重新登录"
}
```

### 用户登出

**POST** `/auth/logout`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "登出成功"
  },
  "message": "登出成功"
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
| product_uuid | string | 否 | 产品UUID |
| supplier_uuid | string | 否 | 供应商UUID |
| category_uuid | string | 否 | 产品分类UUID |
| model_uuid | string | 否 | 产品型号UUID |
| is_active | boolean | 否 | 是否激活 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_name": "笔记本电脑",
        "product_code": "NB001",
        "description": "高性能笔记本电脑",
        "unit_price": 5999.00,
        "current_quantity": 100,
        "min_quantity": 10,
        "max_quantity": 500,
        "supplier_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "supplier_name": "联想集团",
        "model_uuid": "223e4567-e89b-12d3-a456-426614174000",
        "model_name": "ThinkPad X1 Carbon",
        "category_uuid": "333e4567-e89b-12d3-a456-426614174000",
        "category_name": "电子产品",
        "specifications": {
          "cpu": "Intel i7",
          "ram": "16GB",
          "storage": "512GB SSD"
        },
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "size": 20,
    "pages": 8
  },
  "message": "获取产品列表成功"
}
```

### 获取单个产品

**GET** `/Products/{product_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| product_uuid | string | 是 | 产品UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_name": "笔记本电脑",
    "product_code": "NB001",
    "description": "高性能笔记本电脑",
    "unit_price": 5999.00,
    "current_quantity": 100,
    "min_quantity": 10,
    "max_quantity": 500,
    "supplier_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "supplier_name": "联想集团",
    "model_uuid": "223e4567-e89b-12d3-a456-426614174000",
    "model_name": "ThinkPad X1 Carbon",
    "category_uuid": "333e4567-e89b-12d3-a456-426614174000",
    "category_name": "电子产品",
    "specifications": {
      "cpu": "Intel i7",
      "ram": "16GB",
      "storage": "512GB SSD"
    },
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取产品成功"
}
```

### 创建产品

**POST** `/Products`

#### 请求参数
```json
{
  "product_name": "笔记本电脑",
  "product_code": "NB001",
  "description": "高性能笔记本电脑",
  "unit_price": 5999.00,
  "min_quantity": 10,
  "max_quantity": 500,
  "supplier_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "model_uuid": "223e4567-e89b-12d3-a456-426614174000",
  "category_uuid": "333e4567-e89b-12d3-a456-426614174000",
  "specifications": {
    "cpu": "Intel i7",
    "ram": "16GB",
    "storage": "512GB SSD"
  }
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_name": "笔记本电脑",
    "product_code": "NB001",
    "description": "高性能笔记本电脑",
    "unit_price": 5999.00,
    "current_quantity": 0,
    "min_quantity": 10,
    "max_quantity": 500,
    "supplier_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "supplier_name": "联想集团",
    "model_uuid": "223e4567-e89b-12d3-a456-426614174000",
    "model_name": "ThinkPad X1 Carbon",
    "category_uuid": "333e4567-e89b-12d3-a456-426614174000",
    "category_name": "电子产品",
    "specifications": {
      "cpu": "Intel i7",
      "ram": "16GB",
      "storage": "512GB SSD"
    },
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "产品创建成功"
}
```

### 更新产品

**PUT** `/Products/{product_uuid}`

#### 请求参数
```json
{
  "product_name": "笔记本电脑（升级版）",
  "description": "高性能笔记本电脑（最新型号）",
  "unit_price": 6999.00,
  "min_quantity": 15,
  "max_quantity": 600,
  "specifications": {
    "cpu": "Intel i9",
    "ram": "32GB",
    "storage": "1TB SSD"
  }
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_name": "笔记本电脑（升级版）",
    "product_code": "NB001",
    "description": "高性能笔记本电脑（最新型号）",
    "unit_price": 6999.00,
    "current_quantity": 100,
    "min_quantity": 15,
    "max_quantity": 600,
    "supplier_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "supplier_name": "联想集团",
    "model_uuid": "223e4567-e89b-12d3-a456-426614174000",
    "model_name": "ThinkPad X1 Carbon",
    "category_uuid": "333e4567-e89b-12d3-a456-426614174000",
    "category_name": "电子产品",
    "specifications": {
      "cpu": "Intel i9",
      "ram": "32GB",
      "storage": "1TB SSD"
    },
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:30:00Z"
  },
  "message": "产品更新成功"
}
```

### 删除产品

**DELETE** `/Products/{product_uuid}`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "产品删除成功"
  },
  "message": "产品删除成功"
}
```
    "minQuantity": 10,
    "maxQuantity": 500,
    "supplierUuid": "550e8400-e29b-41d4-a716-446655440000",
    "supplierName": "联想集团",
    "modelUuid": "223e4567-e89b-12d3-a456-426614174000",
    "modelName": "ThinkPad X1 Carbon",
    "specifications": {
      "cpu": "Intel i7",
      "ram": "16GB",
      "storage": "512GB SSD"
    },
    "isActive": true,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  },
  "message": "获取产品成功"
}
```

### 创建产品

**POST** `/Products`

#### 请求参数
```json
{
  "productName": "智能手机",
  "description": "高性能智能手机",
  "unitPrice": 2999.00,
  "currentQuantity": 50,
  "minQuantity": 5,
  "maxQuantity": 200,
  "supplierUuid": "550e8400-e29b-41d4-a716-446655440000",
  "modelUuid": "223e4567-e89b-12d3-a456-426614174000"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "productName": "智能手机",
    "productCode": "PH001",
    "description": "高性能智能手机",
    "unitPrice": 2999.00,
    "currentQuantity": 50,
    "minQuantity": 5,
    "maxQuantity": 200,
    "supplierUuid": "550e8400-e29b-41d4-a716-446655440000",
    "modelUuid": "223e4567-e89b-12d3-a456-426614174000",
    "isActive": true,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  },
  "message": "产品创建成功"
}
```

### 更新产品

**PUT** `/Products/{product_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| product_uuid | string | 是 | 产品UUID |

#### 请求参数
```json
{
  "productName": "智能手机 Pro",
  "description": "高性能智能手机 Pro 版本",
  "unitPrice": 3999.00,
  "isActive": true
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "productName": "智能手机 Pro",
    "productCode": "PH001",
    "description": "高性能智能手机 Pro 版本",
    "unitPrice": 3999.00,
    "currentQuantity": 50,
    "minQuantity": 5,
    "maxQuantity": 200,
    "supplierUuid": "550e8400-e29b-41d4-a716-446655440000",
    "modelUuid": "223e4567-e89b-12d3-a456-426614174000",
    "isActive": true,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  },
  "message": "产品更新成功"
}
```

### 删除产品

**DELETE** `/Products/{product_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| product_uuid | string | 是 | 产品UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "产品删除成功"
  },
  "message": "产品删除成功"
}
```

## 供应商管理接口

### 获取供应商列表

**GET** `/Suppliers`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |
| supplier_uuid | string | 否 | 供应商UUID |
| is_active | boolean | 否 | 是否激活 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "supplier_name": "联想集团",
        "supplier_code": "SUP001",
        "contact_person": "张三",
        "phone": "13800138000",
        "email": "zhangsan@lenovo.com",
        "address": "北京市海淀区",
        "tax_number": "91110108700000000X",
        "bank_account": "6222020200000000000",
        "bank_name": "中国工商银行",
        "payment_terms": "月结30天",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取供应商列表成功"
}
```

### 获取单个供应商

**GET** `/Suppliers/{supplier_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| supplier_uuid | string | 是 | 供应商UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "supplier_name": "联想集团",
    "supplier_code": "SUP001",
    "contact_person": "张三",
    "phone": "13800138000",
    "email": "zhangsan@lenovo.com",
    "address": "北京市海淀区",
    "tax_number": "91110108700000000X",
    "bank_account": "6222020200000000000",
    "bank_name": "中国工商银行",
    "payment_terms": "月结30天",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取供应商成功"
}
```

### 创建供应商

**POST** `/Suppliers`

#### 请求参数
```json
{
  "supplier_name": "华为技术有限公司",
  "supplier_code": "SUP002",
  "contact_person": "李四",
  "phone": "13900139000",
  "email": "lisi@huawei.com",
  "address": "深圳市龙岗区",
  "tax_number": "9144030071526726XG",
  "bank_account": "6222020200000000001",
  "bank_name": "中国建设银行",
  "payment_terms": "月结60天"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "supplier_name": "华为技术有限公司",
    "supplier_code": "SUP002",
    "contact_person": "李四",
    "phone": "13900139000",
    "email": "lisi@huawei.com",
    "address": "深圳市龙岗区",
    "tax_number": "9144030071526726XG",
    "bank_account": "6222020200000000001",
    "bank_name": "中国建设银行",
    "payment_terms": "月结60天",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "供应商创建成功"
}
```

### 更新供应商

**PUT** `/Suppliers/{supplier_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| supplier_uuid | string | 是 | 供应商UUID |

#### 请求参数
```json
{
  "supplier_name": "华为技术有限公司（深圳）",
  "contact_person": "李四",
  "payment_terms": "月结45天",
  "is_active": true
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "supplier_name": "华为技术有限公司（深圳）",
    "supplier_code": "SUP002",
    "contact_person": "李四",
    "phone": "13900139000",
    "email": "lisi@huawei.com",
    "address": "深圳市龙岗区",
    "tax_number": "9144030071526726XG",
    "bank_account": "6222020200000000001",
    "bank_name": "中国建设银行",
    "payment_terms": "月结45天",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "供应商更新成功"
}
```

### 删除供应商

**DELETE** `/Suppliers/{supplier_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| supplier_uuid | string | 是 | 供应商UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "供应商删除成功"
  },
  "message": "供应商删除成功"
}
```

## 客户管理接口

### 获取客户列表

**GET** `/Customers`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |
| customer_uuid | string | 否 | 客户UUID |
| is_active | boolean | 否 | 是否激活过滤 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "customer_name": "北京科技有限公司",
        "customer_code": "CUST001",
        "contact_person": "王五",
        "phone": "13600136000",
        "email": "wangwu@tech.com",
        "address": "北京市朝阳区",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取客户列表成功"
}
```

### 获取单个客户

**GET** `/Customers/{customer_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| customer_uuid | string | 是 | 客户UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "customer_name": "北京科技有限公司",
    "customer_code": "CUST001",
    "contact_person": "王五",
    "phone": "13600136000",
    "email": "wangwu@tech.com",
    "address": "北京市朝阳区",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取客户成功"
}
```

### 创建客户

**POST** `/Customers`

#### 请求参数
```json
{
  "customer_name": "上海信息技术有限公司",
  "contact_person": "赵六",
  "phone": "13700137000",
  "email": "zhaoliu@info.com",
  "address": "上海市浦东新区"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174001",
    "customer_name": "上海信息技术有限公司",
    "customer_code": "CUST002",
    "contact_person": "赵六",
    "phone": "13700137000",
    "email": "zhaoliu@info.com",
    "address": "上海市浦东新区",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "客户创建成功"
}
```

### 更新客户

**PUT** `/Customers/{customer_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| customer_uuid | string | 是 | 客户UUID |

#### 请求参数
```json
{
  "customer_name": "上海信息技术有限公司（浦东）",
  "contact_person": "赵六",
  "is_active": true
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174001",
    "customer_name": "上海信息技术有限公司（浦东）",
    "customer_code": "CUST002",
    "contact_person": "赵六",
    "phone": "13700137000",
    "email": "zhaoliu@info.com",
    "address": "上海市浦东新区",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "客户更新成功"
}
```

### 删除客户

**DELETE** `/Customers/{customer_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| customer_uuid | string | 是 | 客户UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "客户删除成功"
  },
  "message": "客户删除成功"
}
```

## 产品类别管理接口

### 获取产品类别列表

**GET** `/ProductCategories`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |
| parent_uuid | string | 否 | 父级分类UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "category_name": "电子产品",
        "category_code": "CAT001",
        "description": "各类电子产品",
        "parent_uuid": null,
        "sort_order": 0,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取产品分类列表成功"
}
```

### 获取产品类别树形结构

**GET** `/ProductCategories/tree`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "category_name": "电子产品",
        "category_code": "CAT001",
        "description": "各类电子产品",
        "parent_uuid": null,
        "sort_order": 0,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "children": [
          {
            "uuid": "223e4567-e89b-12d3-a456-426614174000",
            "category_name": "手机",
            "category_code": "CAT002",
            "description": "智能手机",
            "parent_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "sort_order": 1,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "children": []
          }
        ]
      }
    ],
    "total": 2
  },
  "message": "获取产品分类树成功"
}
```

### 获取单个产品类别

**GET** `/ProductCategories/{category_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category_uuid | string | 是 | 产品类别UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "category_name": "电子产品",
    "category_code": "CAT001",
    "description": "各类电子产品",
    "parent_uuid": null,
    "sort_order": 0,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取产品分类成功"
}
```

### 创建产品类别

**POST** `/ProductCategories`

#### 请求参数
```json
{
  "category_name": "电脑配件",
  "description": "各类电脑配件",
  "parent_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "sort_order": 2
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "323e4567-e89b-12d3-a456-426614174000",
    "category_name": "电脑配件",
    "category_code": "CAT003",
    "description": "各类电脑配件",
    "parent_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "sort_order": 2,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "产品分类创建成功"
}
```

### 更新产品类别

**PUT** `/ProductCategories/{category_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category_uuid | string | 是 | 产品类别UUID |

#### 请求参数
```json
{
  "category_name": "电脑配件（更新）",
  "description": "各类电脑配件和周边",
  "sort_order": 3,
  "is_active": true
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "323e4567-e89b-12d3-a456-426614174000",
    "category_name": "电脑配件（更新）",
    "category_code": "CAT003",
    "description": "各类电脑配件和周边",
    "parent_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "sort_order": 3,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "产品分类更新成功"
}
```

### 删除产品类别

**DELETE** `/ProductCategories/{category_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| category_uuid | string | 是 | 产品类别UUID |

#### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "产品分类删除成功"
}
```

## 产品型号管理接口

### 获取产品型号列表

**GET** `/ProductModels`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词 |
| category_uuid | string | 否 | 产品分类UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "model_name": "iPhone 15 Pro",
        "model_code": "PM001",
        "description": "苹果最新旗舰手机",
        "category_uuid": "123e4567-e89b-12d3-a456-426614174001",
        "category_name": "手机",
        "specifications": [
          {
            "key": "屏幕尺寸",
            "value": "6.1",
            "unit": "英寸"
          },
          {
            "key": "内存",
            "value": "8",
            "unit": "GB"
          }
        ],
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取产品型号列表成功"
}
```

### 获取单个产品型号

**GET** `/ProductModels/{model_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| model_uuid | string | 是 | 产品型号UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "model_name": "iPhone 15 Pro",
    "model_code": "PM001",
    "description": "苹果最新旗舰手机",
    "category_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "category_name": "手机",
    "specifications": [
      {
        "key": "屏幕尺寸",
        "value": "6.1",
        "unit": "英寸"
      },
      {
        "key": "内存",
        "value": "8",
        "unit": "GB"
      }
    ],
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取产品型号成功"
}
```

### 创建产品型号

**POST** `/ProductModels`

#### 请求参数
```json
{
  "model_name": "MacBook Pro 16寸",
  "description": "苹果专业笔记本电脑",
  "category_uuid": "123e4567-e89b-12d3-a456-426614174002",
  "specifications": [
    {
      "key": "处理器",
      "value": "M3",
      "unit": "芯片"
    },
    {
      "key": "内存",
      "value": "16",
      "unit": "GB"
    }
  ]
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "223e4567-e89b-12d3-a456-426614174000",
    "model_name": "MacBook Pro 16寸",
    "model_code": "PM002",
    "description": "苹果专业笔记本电脑",
    "category_uuid": "123e4567-e89b-12d3-a456-426614174002",
    "category_name": "电脑",
    "specifications": [
      {
        "key": "处理器",
        "value": "M3",
        "unit": "芯片"
      },
      {
        "key": "内存",
        "value": "16",
        "unit": "GB"
      }
    ],
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "产品型号创建成功"
}
```

### 更新产品型号

**PUT** `/ProductModels/{model_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| model_uuid | string | 是 | 产品型号UUID |

#### 请求参数
```json
{
  "model_name": "MacBook Pro 16寸（更新）",
  "description": "苹果专业笔记本电脑最新款",
  "specifications": [
    {
      "key": "处理器",
      "value": "M3 Pro",
      "unit": "芯片"
    },
    {
      "key": "内存",
      "value": "32",
      "unit": "GB"
    }
  ]
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "223e4567-e89b-12d3-a456-426614174000",
    "model_name": "MacBook Pro 16寸（更新）",
    "model_code": "PM002",
    "description": "苹果专业笔记本电脑最新款",
    "category_uuid": "123e4567-e89b-12d3-a456-426614174002",
    "category_name": "电脑",
    "specifications": [
      {
        "key": "处理器",
        "value": "M3 Pro",
        "unit": "芯片"
      },
      {
        "key": "内存",
        "value": "32",
        "unit": "GB"
      }
    ],
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "message": "产品型号更新成功"
}
```

### 删除产品型号

**DELETE** `/ProductModels/{model_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| model_uuid | string | 是 | 产品型号UUID |

#### 响应示例
```json
{
  "success": true,
  "data": null,
  "message": "产品型号删除成功"
}
```

### 获取产品分类列表

**GET** `/ProductModels/categories`

#### 响应示例
```json
{
  "success": true,
  "data": ["手机", "电脑", "配件"],
  "message": "获取产品分类成功"
}
```

## 库存管理接口

### 获取库存汇总信息

**GET** `/Inventory/Summary`

#### 响应示例
```json
{
  "success": true,
  "data": {
    "total_products": 150,
    "total_value": 1250000.50,
    "low_stock_count": 5,
    "high_stock_count": 3,
    "today_in": 250,
    "today_out": 180,
    "low_stock_products": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "current_quantity": 2,
        "min_quantity": 10
      }
    ],
    "high_stock_products": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "MacBook Pro",
        "current_quantity": 150,
        "max_quantity": 100
      }
    ]
  },
  "message": "获取库存汇总信息成功"
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
        "product_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "current_quantity": 2,
        "min_quantity": 10,
        "severity": "HIGH"
      },
      {
        "type": "HIGH_STOCK",
        "product_uuid": "223e4567-e89b-12d3-a456-426614174000",
        "product_name": "MacBook Pro",
        "current_quantity": 150,
        "max_quantity": 100,
        "severity": "LOW"
      }
    ]
  },
  "message": "获取库存预警列表成功"
}
```

### 获取库存记录列表

**GET** `/Inventory`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| product_uuid | string | 否 | 产品UUID |
| change_type | string | 否 | 变动类型（in/out/adjust） |
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |
| search | string | 否 | 搜索关键词 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "123e4567-e89b-12d3-a456-426614174001",
        "product_name": "iPhone 15 Pro",
        "product_code": "P001",
        "previous_quantity": 50,
        "current_quantity": 70,
        "change_quantity": 20,
        "change_type": "in",
        "reason": "采购入库",
        "recorded_by": "system",
        "recorded_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取库存记录列表成功"
}
```

### 获取单个库存记录

**GET** `/Inventory/{record_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| record_uuid | string | 是 | 库存记录UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "product_name": "iPhone 15 Pro",
    "product_code": "P001",
    "previous_quantity": 50,
    "current_quantity": 70,
    "change_quantity": 20,
    "change_type": "in",
    "reason": "采购入库",
    "recorded_by": "system",
    "recorded_at": "2024-01-15T10:30:00Z"
  },
  "message": "获取库存记录成功"
}
```

### 创建库存记录

**POST** `/Inventory`

#### 请求参数
```json
{
  "product_uuid": "123e4567-e89b-12d3-a456-426614174001",
  "change_type": "in",
  "change_quantity": 20,
  "reason": "采购入库"
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "product_name": "iPhone 15 Pro",
    "product_code": "P001",
    "previous_quantity": 50,
    "current_quantity": 70,
    "change_quantity": 20,
    "change_type": "in",
    "reason": "采购入库",
    "recorded_by": "system",
    "recorded_at": "2024-01-15T10:30:00Z"
  },
  "message": "库存记录创建成功"
}
```

## 采购订单管理接口

### 获取采购订单列表

**GET** `/PurchaseOrders`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词（订单编号） |
| supplier_uuid | string | 否 | 供应商UUID |
| product_uuid | string | 否 | 商品UUID |
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |
| min_amount | float | 否 | 最小金额 |
| max_amount | float | 否 | 最大金额 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "order_number": "PO202401150001",
        "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
        "supplier_name": "供应商A",
        "total_amount": 15000.00,
        "order_date": "2024-01-15",
        "expected_delivery_date": "2024-01-20",
        "actual_delivery_date": null,
        "remark": "常规采购",
        "created_by": "system",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "items": [
          {
            "uuid": "223e4567-e89b-12d3-a456-426614174000",
            "purchase_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
            "product_name": "iPhone 15 Pro",
            "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
            "model_name": "256GB 深空黑",
            "selected_specification": "256GB 深空黑",
            "quantity": 10,
            "unit_price": 1500.00,
            "total_price": 15000.00,
            "received_quantity": 0,
            "notes": "",
            "created_at": "2024-01-15T10:30:00Z"
          }
        ]
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取采购订单列表成功"
}
```

### 获取单个采购订单

**GET** `/PurchaseOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 采购订单UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "PO202401150001",
    "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "supplier_name": "供应商A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "actual_delivery_date": null,
    "total_amount": 15000.00,
    "status": "PENDING",
    "remark": "常规采购",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "purchase_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 10,
        "unit_price": 1500.00,
        "total_price": 15000.00,
        "received_quantity": 0,
        "notes": "",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "获取采购订单成功"
}
```

### 创建采购订单

**POST** `/PurchaseOrders`

#### 请求参数
```json
{
  "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
  "order_date": "2024-01-15",
  "expected_delivery_date": "2024-01-20",
  "remark": "常规采购",
  "items": [
    {
      "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
      "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
      "selected_specification": "256GB 深空黑",
      "quantity": 10,
      "unit_price": 1500.00,
      "remark": ""
    }
  ]
}```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "PO202401150001",
    "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "supplier_name": "供应商A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "total_amount": 15000.00,
    "status": "PENDING",
    "actual_delivery_date": null,
    "remark": "常规采购",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "purchase_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 10,
        "unit_price": 1500.00,
        "total_price": 15000.00,
        "received_quantity": 0,
        "remark": "",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "采购订单创建成功"
}
```

### 更新采购订单

**PUT** `/PurchaseOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 采购订单UUID |

#### 请求参数
```json
{
  "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
  "order_date": "2024-01-15",
  "expected_delivery_date": "2024-01-20",
  "actual_delivery_date": "2024-01-18",
  "remark": "更新后的采购备注",
  "items": [
    {
      "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
      "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
      "selected_specification": "256GB 深空黑",
      "quantity": 15,
      "unit_price": 1500.00,
      "remark": "增加采购数量"
    }
  ]
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "PO202401150001",
    "supplier_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "supplier_name": "供应商A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "actual_delivery_date": "2024-01-18",
    "total_amount": 22500.00,
    "status": "PENDING",
    "remark": "更新后的采购备注",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "purchase_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 15,
        "unit_price": 1500.00,
        "total_price": 22500.00,
        "received_quantity": 0,
        "remark": "增加采购数量",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "采购订单更新成功"
}
```

### 删除采购订单

**DELETE** `/PurchaseOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 采购订单UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "采购订单删除成功"
  },
  "message": "采购订单删除成功"
}
```

## 销售订单管理接口

### 获取销售订单列表

**GET** `/SalesOrders`

#### 查询参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页大小，默认20 |
| search | string | 否 | 搜索关键词（订单编号） |
| customer_uuid | string | 否 | 客户UUID |
| product_uuid | string | 否 | 商品UUID |
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |
| min_amount | float | 否 | 最小金额 |
| max_amount | float | 否 | 最大金额 |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "order_number": "SO202401150001",
        "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
        "customer_name": "客户A",
        "total_amount": 15000.00,
        "order_date": "2024-01-15",
        "expected_delivery_date": "2024-01-20",
        "actual_delivery_date": null,
        "remark": "常规销售",
        "created_by": "system",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "items": [
          {
            "uuid": "223e4567-e89b-12d3-a456-426614174000",
            "sales_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
            "product_name": "iPhone 15 Pro",
            "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
            "model_name": "256GB 深空黑",
            "selected_specification": "256GB 深空黑",
            "quantity": 10,
            "unit_price": 1500.00,
            "total_price": 15000.00,
            "delivered_quantity": 0,
            "notes": "",
            "created_at": "2024-01-15T10:30:00Z"
          }
        ]
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20,
    "pages": 3
  },
  "message": "获取销售订单列表成功"
}
```

### 获取单个销售订单

**GET** `/SalesOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 销售订单UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "SO202401150001",
    "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "customer_name": "客户A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "actual_delivery_date": null,
    "total_amount": 15000.00,
    "status": "PENDING",
    "remark": "常规销售",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "sales_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 10,
        "unit_price": 1500.00,
        "total_price": 15000.00,
        "delivered_quantity": 0,
        "notes": "",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "获取销售订单成功"
}
```

### 创建销售订单

**POST** `/SalesOrders`

#### 请求参数
```json
{
  "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
  "order_date": "2024-01-15",
  "expected_delivery_date": "2024-01-20",
  "remark": "常规销售",
  "items": [
    {
      "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
      "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
      "selected_specification": "256GB 深空黑",
      "quantity": 10,
      "unit_price": 1500.00,
      "remark": ""
    }
  ]
}```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "SO202401150001",
    "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "customer_name": "客户A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "total_amount": 15000.00,
    "status": "PENDING",
    "actual_delivery_date": null,
    "remark": "常规销售",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "sales_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 10,
        "unit_price": 1500.00,
        "total_price": 15000.00,
        "delivered_quantity": 0,
        "remark": "",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "销售订单创建成功"
}
```

### 更新销售订单

**PUT** `/SalesOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 销售订单UUID |

#### 请求参数
```json
{
  "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
  "order_date": "2024-01-15",
  "expected_delivery_date": "2024-01-20",
  "actual_delivery_date": "2024-01-18",
  "remark": "更新后的销售备注",
  "items": [
    {
      "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
      "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
      "selected_specification": "256GB 深空黑",
      "quantity": 15,
      "unit_price": 1500.00,
      "remark": "增加销售数量"
    }
  ]
}
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "order_number": "SO202401150001",
    "customer_uuid": "123e4567-e89b-12d3-a456-426614174001",
    "customer_name": "客户A",
    "order_date": "2024-01-15",
    "expected_delivery_date": "2024-01-20",
    "actual_delivery_date": "2024-01-18",
    "total_amount": 22500.00,
    "status": "PENDING",
    "remark": "更新后的销售备注",
    "created_by": "system",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:30:00Z",
    "items": [
      {
        "uuid": "223e4567-e89b-12d3-a456-426614174000",
        "sales_order_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "product_uuid": "323e4567-e89b-12d3-a456-426614174000",
        "product_name": "iPhone 15 Pro",
        "model_uuid": "423e4567-e89b-12d3-a456-426614174000",
        "model_name": "256GB 深空黑",
        "selected_specification": "256GB 深空黑",
        "quantity": 15,
        "unit_price": 1500.00,
        "total_price": 22500.00,
        "delivered_quantity": 0,
        "remark": "增加销售数量",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "销售订单更新成功"
}
```

### 删除销售订单

**DELETE** `/SalesOrders/{order_uuid}`

#### 路径参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| order_uuid | string | 是 | 销售订单UUID |

#### 响应示例
```json
{
  "success": true,
  "data": {
    "message": "销售订单删除成功"
  },
  "message": "销售订单删除成功"
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