-- 进销存管理系统 - 数据库表创建脚本
-- 创建时间: 2025-01-25
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_unicode_ci

-- 设置数据库
USE xiaochuanERP;

-- 1. 用户表 (users)
CREATE TABLE IF NOT EXISTS users (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager', 'user') NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 用户表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_users_username ON users(username);
CREATE UNIQUE INDEX IF NOT EXISTS uk_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 2. 供应商表 (suppliers)
CREATE TABLE IF NOT EXISTS suppliers (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    supplier_name VARCHAR(100) NOT NULL,
    supplier_code VARCHAR(50) NOT NULL UNIQUE,
    contact_person VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 供应商表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_suppliers_code ON suppliers(supplier_code);
CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(supplier_name);
CREATE INDEX IF NOT EXISTS idx_suppliers_is_active ON suppliers(is_active);
CREATE INDEX IF NOT EXISTS idx_suppliers_created_at ON suppliers(created_at);

-- 3. 产品表 (products)
CREATE TABLE IF NOT EXISTS products (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    product_name VARCHAR(100) NOT NULL,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    current_quantity INT NOT NULL DEFAULT 0,
    min_quantity INT NOT NULL DEFAULT 0,
    max_quantity INT NOT NULL DEFAULT 0,
    supplier_uuid CHAR(36) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (supplier_uuid) REFERENCES suppliers(uuid) ON DELETE RESTRICT
);

-- 产品表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_products_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_uuid);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_products_quantity ON products(current_quantity);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_products_stock_status ON products(current_quantity, min_quantity, max_quantity);

-- 4. 库存记录表 (inventory_records)
CREATE TABLE IF NOT EXISTS inventory_records (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    product_uuid CHAR(36) NOT NULL,
    change_type ENUM('IN', 'OUT', 'ADJUST') NOT NULL,
    quantity_change INT NOT NULL,
    current_quantity INT NOT NULL,
    remark TEXT,
    record_date DATE NOT NULL,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_uuid) REFERENCES products(uuid) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(uuid) ON DELETE RESTRICT
);

-- 库存记录表索引
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_records(product_uuid);
CREATE INDEX IF NOT EXISTS idx_inventory_change_type ON inventory_records(change_type);
CREATE INDEX IF NOT EXISTS idx_inventory_record_date ON inventory_records(record_date);
CREATE INDEX IF NOT EXISTS idx_inventory_created_by ON inventory_records(created_by);
CREATE INDEX IF NOT EXISTS idx_inventory_created_at ON inventory_records(created_at);

-- 5. 采购订单表 (purchase_orders)
CREATE TABLE IF NOT EXISTS purchase_orders (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_number VARCHAR(50) NOT NULL UNIQUE,
    supplier_uuid CHAR(36) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status ENUM('PENDING', 'CONFIRMED', 'RECEIVED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    remark TEXT,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supplier_uuid) REFERENCES suppliers(uuid) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(uuid) ON DELETE RESTRICT
);

-- 采购订单表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_purchase_orders_number ON purchase_orders(order_number);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier ON purchase_orders(supplier_uuid);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_date ON purchase_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_created_by ON purchase_orders(created_by);

-- 6. 采购订单明细表 (purchase_order_items)
CREATE TABLE IF NOT EXISTS purchase_order_items (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    purchase_order_uuid CHAR(36) NOT NULL,
    product_uuid CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    received_quantity INT NOT NULL DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (purchase_order_uuid) REFERENCES purchase_orders(uuid) ON DELETE CASCADE,
    FOREIGN KEY (product_uuid) REFERENCES products(uuid) ON DELETE RESTRICT
);

-- 采购订单明细表索引
CREATE INDEX IF NOT EXISTS idx_purchase_items_order ON purchase_order_items(purchase_order_uuid);
CREATE INDEX IF NOT EXISTS idx_purchase_items_product ON purchase_order_items(product_uuid);

-- 7. 销售订单表 (sales_orders)
CREATE TABLE IF NOT EXISTS sales_orders (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20),
    customer_address TEXT,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status ENUM('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    remark TEXT,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(uuid) ON DELETE RESTRICT
);

-- 销售订单表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_sales_orders_number ON sales_orders(order_number);
CREATE INDEX IF NOT EXISTS idx_sales_orders_status ON sales_orders(status);
CREATE INDEX IF NOT EXISTS idx_sales_orders_date ON sales_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_sales_orders_created_by ON sales_orders(created_by);

-- 8. 销售订单明细表 (sales_order_items)
CREATE TABLE IF NOT EXISTS sales_order_items (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    sales_order_uuid CHAR(36) NOT NULL,
    product_uuid CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    shipped_quantity INT NOT NULL DEFAULT 0,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sales_order_uuid) REFERENCES sales_orders(uuid) ON DELETE CASCADE,
    FOREIGN KEY (product_uuid) REFERENCES products(uuid) ON DELETE RESTRICT
);

-- 销售订单明细表索引
CREATE INDEX IF NOT EXISTS idx_sales_items_order ON sales_order_items(sales_order_uuid);
CREATE INDEX IF NOT EXISTS idx_sales_items_product ON sales_order_items(product_uuid);

-- 显示创建的表信息
SELECT 
    TABLE_NAME as '表名',
    TABLE_ROWS as '记录数',
    CREATE_TIME as '创建时间'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'xiaochuanERP' 
ORDER BY TABLE_NAME;