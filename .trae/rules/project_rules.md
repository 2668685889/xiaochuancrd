# 进销存软件技术大纲

## 项目概述
现代化的进销存管理系统，采用前后端分离架构，具有扁平化科技感的UI设计。

## 技术栈选择

### 前端技术栈
- **框架**: React 18+ (函数式组件 + Hooks)
- **样式**: Tailwind CSS + Headless UI (扁平化科技感设计)
- **状态管理**: Zustand (轻量级状态管理)
- **路由**: React Router v6
- **HTTP客户端**: Axios
- **图标**: Lucide React (现代化图标)
- **构建工具**: Vite
- **类型检查**: TypeScript

### 后端技术栈
- **框架**: FastAPI (高性能Python Web框架)
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + OAuth2
- **缓存**: Redis
- **任务队列**: Celery
- **API文档**: OpenAPI/Swagger

### 数据库设计
- **数据库**: MySQL 8.0+
- **字符集**: utf8mb4
- **存储引擎**: InnoDB
- **连接池**: SQLAlchemy连接池

## 命名规则规范

### 前端命名规则

#### 1. 文件命名规则
```
// 组件文件 - PascalCase (大驼峰)
InventoryList.tsx
ProductCard.tsx
SupplierForm.tsx

// 工具函数 - camelCase
apiClient.ts
formatUtils.ts
validationRules.ts

// 样式文件 - kebab-case
inventory-list.module.css
product-card.module.css

// 常量文件 - UPPER_SNAKE_CASE
apiEndpoints.ts
errorMessages.ts
```

#### 2. 组件命名规则
```typescript
// 页面组件 - Page后缀
InventoryPage.tsx
ProductPage.tsx
ReportPage.tsx

// 布局组件 - Layout后缀
MainLayout.tsx
SidebarLayout.tsx

// 表单组件 - Form后缀
ProductForm.tsx
SupplierForm.tsx

// 列表组件 - List后缀
InventoryList.tsx
OrderList.tsx

// 卡片组件 - Card后缀
ProductCard.tsx
SupplierCard.tsx
```

#### 3. 变量命名规则
```typescript
// 状态变量 - 描述性camelCase
const [inventoryItems, setInventoryItems] = useState([]);
const [selectedProduct, setSelectedProduct] = useState(null);
const [isLoading, setIsLoading] = useState(false);

// 函数命名 - 动词开头camelCase
const fetchInventoryData = async () => {};
const handleProductSelect = (product) => {};
const validateFormInput = (input) => {};

// 常量命名 - UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_PRODUCT_QUANTITY = 1000;
const DEFAULT_PAGE_SIZE = 20;
```

#### 4. CSS类名命名规则
```css
/* BEM命名规范 + Tailwind语义化 */
.inventory-list__header {}
.inventory-list__item--selected {}

/* 功能类名 */
.text-primary { color: #3b82f6; }
.bg-success { background-color: #10b981; }

/* 状态类名 */
.is-loading { opacity: 0.5; }
.is-disabled { pointer-events: none; }
```

### 后端命名规则

#### 1. 文件命名规则
```python
# 模型文件 - snake_case
product_models.py
supplier_models.py
inventory_models.py

# 服务文件 - snake_case
product_service.py
inventory_service.py
report_service.py

# API路由文件 - snake_case
product_routes.py
supplier_routes.py
auth_routes.py

# 工具文件 - snake_case
database_utils.py
auth_utils.py
validation_utils.py
```

#### 2. 类命名规则
```python
# 模型类 - PascalCase
class Product(BaseModel):
    pass

class Supplier(BaseModel):
    pass

class InventoryRecord(BaseModel):
    pass

# 服务类 - Service后缀
class ProductService:
    pass

class InventoryService:
    pass

# 工具类 - Utils后缀
class DateUtils:
    pass

class StringUtils:
    pass
```

#### 3. 函数命名规则
```python
# 数据库操作函数 - 动词开头snake_case
def create_product(product_data: dict) -> Product:
    pass

def get_product_by_id(product_id: int) -> Product:
    pass

def update_product_quantity(product_id: int, new_quantity: int) -> bool:
    pass

def delete_product(product_id: int) -> bool:
    pass

# 业务逻辑函数 - 描述性snake_case
def calculate_inventory_value() -> float:
    pass

def generate_sales_report(start_date, end_date) -> dict:
    pass

def validate_product_data(product_data: dict) -> bool:
    pass
```

#### 4. 变量命名规则
```python
# 数据库字段 - snake_case
product_name: str
supplier_code: str
inventory_quantity: int
unit_price: float

# 临时变量 - 描述性snake_case
current_inventory = []
total_value = 0.0
is_valid = True

# 常量 - UPPER_SNAKE_CASE
MAX_PRODUCT_NAME_LENGTH = 100
DEFAULT_PAGE_SIZE = 20
API_VERSION = "v1"
```

#### 5. API端点命名规则
```python
# RESTful API命名规范 - 使用大驼峰命名
# 产品相关
GET /api/v1/Products              # 获取产品列表
POST /api/v1/Products            # 创建新产品
GET /api/v1/Products/{uuid}      # 获取单个产品
PUT /api/v1/Products/{uuid}      # 更新产品
DELETE /api/v1/Products/{uuid}   # 删除产品

# 库存相关
GET /api/v1/Inventory            # 获取库存列表
POST /api/v1/Inventory/Adjust    # 调整库存
GET /api/v1/Inventory/Alerts     # 获取库存预警

# 报表相关
GET /api/v1/Reports/Sales        # 销售报表
GET /api/v1/Reports/Inventory    # 库存报表
POST /api/v1/Reports/Export     # 导出报表
```

#### 6. API数据映射规则 (关键)
```python
# 前端使用大驼峰命名，后端API也使用大驼峰命名
# 但数据库使用蛇形命名，需要在API层进行映射转换

# 前端请求数据 (大驼峰)
{
    "productName": "笔记本电脑",
    "productCode": "NB001",
    "unitPrice": 5999.00,
    "currentQuantity": 100,
    "minQuantity": 10,
    "maxQuantity": 500,
    "supplierId": "550e8400-e29b-41d4-a716-446655440000"
}

# API层转换到数据库 (蛇形命名)
{
    "product_name": "笔记本电脑",
    "product_code": "NB001",
    "unit_price": 5999.00,
    "current_quantity": 100,
    "min_quantity": 10,
    "max_quantity": 500,
    "supplier_id": "550e8400-e29b-41d4-a716-446655440000"
}

# 数据库返回数据 (蛇形命名)
{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "product_name": "笔记本电脑",
    "product_code": "NB001",
    "unit_price": 5999.00,
    "current_quantity": 100,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}

# API层转换到前端 (大驼峰)
{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "productName": "笔记本电脑",
    "productCode": "NB001",
    "unitPrice": 5999.00,
    "currentQuantity": 100,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
}
```

#### 7. API映射实现代码示例

##### 前端API客户端 (TypeScript)
```typescript
// src/services/api/mapper.ts
/**
 * 将蛇形命名转换为大驼峰命名
 */
export function snakeToCamel(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => snakeToCamel(item));
    }
    
    const result: any = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
            result[camelKey] = snakeToCamel(obj[key]);
        }
    }
    return result;
}

/**
 * 将大驼峰命名转换为蛇形命名
 */
export function camelToSnake(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    if (Array.isArray(obj)) {
        return obj.map(item => camelToSnake(item));
    }
    
    const result: any = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
            result[snakeKey] = camelToSnake(obj[key]);
        }
    }
    return result;
}

// src/services/api/client.ts
import { snakeToCamel, camelToSnake } from './mapper';

class ApiClient {
    private baseURL = process.env.REACT_APP_API_BASE_URL;

    async request(endpoint: string, options: RequestInit = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        // 请求数据转换
        if (options.body && typeof options.body === 'object') {
            options.body = JSON.stringify(camelToSnake(options.body));
        }
        
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        
        const data = await response.json();
        
        // 响应数据转换
        return snakeToCamel(data);
    }

    async getProducts(): Promise<Product[]> {
        return this.request('/api/v1/Products');
    }

    async createProduct(productData: CreateProductRequest): Promise<Product> {
        return this.request('/api/v1/Products', {
            method: 'POST',
            body: productData,
        });
    }
}

export const apiClient = new ApiClient();
```

##### 后端API映射 (Python FastAPI)
```python
# app/utils/mapper.py
from typing import Any, Dict
import re


def snake_to_camel(data: Any) -> Any:
    """将蛇形命名转换为大驼峰命名"""
    if data is None or not isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, list):
        return [snake_to_camel(item) for item in data]
    
    result = {}
    for key, value in data.items():
        # 将蛇形命名转换为大驼峰
        camel_key = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), key)
        # 首字母大写
        camel_key = camel_key[0].upper() + camel_key[1:] if camel_key else camel_key
        result[camel_key] = snake_to_camel(value)
    
    return result


def camel_to_snake(data: Any) -> Any:
    """将大驼峰命名转换为蛇形命名"""
    if data is None or not isinstance(data, (dict, list)):
        return data
    
    if isinstance(data, list):
        return [camel_to_snake(item) for item in data]
    
    result = {}
    for key, value in data.items():
        # 将大驼峰转换为蛇形命名
        snake_key = re.sub(r'([A-Z])', r'_\1', key).lower()
        result[snake_key] = camel_to_snake(value)
    
    return result


# app/schemas/product.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


# 数据库模型 (蛇形命名)
class ProductDB(BaseModel):
    uuid: UUID
    product_name: str
    product_code: str
    unit_price: float
    current_quantity: int
    min_quantity: int
    max_quantity: int
    supplier_uuid: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# API响应模型 (大驼峰命名)
class ProductResponse(BaseModel):
    uuid: UUID
    productName: str
    productCode: str
    unitPrice: float
    currentQuantity: int
    minQuantity: int
    maxQuantity: int
    supplierUuid: UUID
    createdAt: datetime
    updatedAt: datetime


# API请求模型 (大驼峰命名)
class CreateProductRequest(BaseModel):
    productName: str
    productCode: str
    unitPrice: float
    currentQuantity: int
    minQuantity: int
    maxQuantity: int
    supplierUuid: UUID


# app/routes/products.py
from fastapi import APIRouter, Depends
from app.schemas.product import ProductResponse, CreateProductRequest
from app.utils.mapper import snake_to_camel, camel_to_snake

router = APIRouter()


@router.get("/Products", response_model=list[ProductResponse])
async def get_products():
    # 从数据库获取数据 (蛇形命名)
    db_products = await get_products_from_db()
    
    # 转换为大驼峰命名返回给前端
    return snake_to_camel(db_products)


@router.post("/Products", response_model=ProductResponse)
async def create_product(product_data: CreateProductRequest):
    # 将前端的大驼峰数据转换为蛇形命名
    db_data = camel_to_snake(product_data.dict())
    
    # 保存到数据库
    created_product = await create_product_in_db(db_data)
    
    # 转换为大驼峰命名返回给前端
    return snake_to_camel(created_product)
```

## 数据库表命名规则

### 1. 表名命名规则
```sql
-- 使用复数形式，snake_case
products
suppliers
inventory_records
sales_orders
purchase_orders

-- 关联表使用两个表名的组合
product_categories
supplier_products
order_items
```

### 2. 字段命名规则
```sql
-- 主键字段 - 使用UUID避免跨数据库重复
uuid CHAR(36) PRIMARY KEY DEFAULT (UUID())

-- 外键字段 - 使用UUID关联
product_uuid CHAR(36)
supplier_uuid CHAR(36)
user_uuid CHAR(36)

-- 时间字段
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
deleted_at TIMESTAMP NULL

-- 业务字段
product_name VARCHAR(100)
product_code VARCHAR(50)
unit_price DECIMAL(10,2)
current_quantity INT
min_quantity INT
max_quantity INT

-- 状态字段
status ENUM('active', 'inactive', 'pending')
is_available BOOLEAN DEFAULT TRUE
```

### 3. 索引命名规则
```sql
-- 唯一索引
UNIQUE INDEX uk_product_code (product_code)
UNIQUE INDEX uk_supplier_code (supplier_code)

-- 普通索引
INDEX idx_product_name (product_name)
INDEX idx_supplier_uuid (supplier_uuid)
INDEX idx_created_at (created_at)

-- 复合索引
INDEX idx_product_status (product_uuid, status)
INDEX idx_inventory_date (product_uuid, record_date)
```

## 项目目录结构

### 前端目录结构
```
src/
├── components/          # 可复用组件
│   ├── ui/              # 基础UI组件
│   ├── forms/           # 表单组件
│   ├── tables/          # 表格组件
│   └── charts/          # 图表组件
├── pages/               # 页面组件
│   ├── inventory/       # 库存管理
│   ├── products/        # 产品管理
│   ├── suppliers/       # 供应商管理
│   └── reports/         # 报表分析
├── services/           # API服务
│   ├── api/            # API客户端
│   ├── auth/           # 认证服务
│   └── storage/        # 存储服务
├── hooks/              # 自定义Hooks
├── utils/              # 工具函数
├── constants/          # 常量定义
├── types/              # TypeScript类型定义
└── styles/             # 全局样式
```

### 后端目录结构
```
backend/
├── app/
│   ├── models/         # 数据模型
│   ├── schemas/        # Pydantic模式
│   ├── services/       # 业务逻辑
│   ├── routes/         # API路由
│   ├── utils/          # 工具函数
│   └── core/           # 核心配置
├── migrations/         # 数据库迁移
├── tests/              # 测试文件
├── scripts/            # 脚本文件
└── docs/               # 项目文档
```

## UI设计规范

### 色彩方案 (扁平化科技感)
```css
/* 主色调 - 科技蓝 */
--primary-color: #3b82f6;
--primary-dark: #1d4ed8;
--primary-light: #60a5fa;

/* 辅助色 */
--success-color: #10b981;
--warning-color: #f59e0b;
--error-color: #ef4444;
--info-color: #6b7280;

/* 中性色 */
--text-primary: #1f2937;
--text-secondary: #6b7280;
--border-color: #e5e7eb;
--background-color: #f9fafb;
```

### 字体规范
```css
/* 字体家族 */
--font-family-primary: 'Inter', -apple-system, sans-serif;
--font-family-mono: 'JetBrains Mono', monospace;

/* 字体大小 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
```

### 间距规范
```css
/* 间距系统 */
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
```

## 开发规范

### 代码提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具变动
```

### 代码审查规范
1. 所有代码必须通过ESLint检查
2. 重要功能必须包含单元测试
3. API变更必须更新文档
4. 数据库变更必须提供迁移脚本

## 部署架构

### 开发环境
- 前端: Vite开发服务器
- 后端: Uvicorn开发服务器
- 数据库: Docker MySQL

### 生产环境
- 前端: Nginx + CDN
- 后端: Gunicorn + Uvicorn
- 数据库: MySQL主从复制
- 缓存: Redis集群
- 监控: Prometheus + Grafana

---