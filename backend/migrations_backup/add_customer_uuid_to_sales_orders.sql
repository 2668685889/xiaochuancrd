-- 为销售订单表添加customer_uuid字段
-- 迁移脚本创建时间: 2025-01-25

-- 选择数据库
USE xiaochuanERP;

-- 1. 添加customer_uuid字段到sales_orders表
ALTER TABLE sales_orders ADD COLUMN customer_uuid CHAR(36) NULL AFTER order_number;

-- 2. 添加外键约束
ALTER TABLE sales_orders ADD CONSTRAINT fk_sales_orders_customer 
    FOREIGN KEY (customer_uuid) REFERENCES customers(uuid) ON DELETE RESTRICT;

-- 3. 创建索引
CREATE INDEX idx_sales_orders_customer ON sales_orders(customer_uuid);

-- 4. 验证表结构
DESCRIBE sales_orders;

-- 5. 显示添加的字段信息
SELECT 
    COLUMN_NAME as '字段名',
    COLUMN_TYPE as '字段类型',
    IS_NULLABLE as '是否可为空',
    COLUMN_KEY as '键类型',
    COLUMN_DEFAULT as '默认值',
    EXTRA as '额外信息'
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'xiaochuanERP' 
AND TABLE_NAME = 'sales_orders'
AND COLUMN_NAME = 'customer_uuid';