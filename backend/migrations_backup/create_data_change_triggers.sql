-- 创建数据变化触发器
-- 为每个业务表创建INSERT、UPDATE、DELETE触发器

-- 1. 创建数据变化日志表
CREATE TABLE IF NOT EXISTS data_change_logs (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    table_name VARCHAR(100) NOT NULL COMMENT '表名',
    record_uuid CHAR(36) NOT NULL COMMENT '记录UUID',
    operation_type VARCHAR(20) NOT NULL COMMENT '操作类型: INSERT, UPDATE, DELETE',
    change_data JSON COMMENT '变化数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    processed TINYINT DEFAULT 0 COMMENT '是否已处理: 0-未处理, 1-已处理',
    processed_at TIMESTAMP NULL COMMENT '处理时间',
    INDEX idx_table_name (table_name),
    INDEX idx_processed (processed),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据变化日志表';

-- 2. 为products表创建触发器
DELIMITER //

-- products表INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('products', NEW.uuid, 'INSERT', JSON_OBJECT(
        'uuid', NEW.uuid,
        'product_name', NEW.product_name,
        'product_code', NEW.product_code,
        'unit_price', NEW.unit_price,
        'current_quantity', NEW.current_quantity,
        'min_quantity', NEW.min_quantity,
        'max_quantity', NEW.max_quantity,
        'supplier_uuid', NEW.supplier_uuid,
        'category_uuid', NEW.category_uuid,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- products表UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('products', NEW.uuid, 'UPDATE', JSON_OBJECT(
        'uuid', NEW.uuid,
        'product_name', NEW.product_name,
        'product_code', NEW.product_code,
        'unit_price', NEW.unit_price,
        'current_quantity', NEW.current_quantity,
        'min_quantity', NEW.min_quantity,
        'max_quantity', NEW.max_quantity,
        'supplier_uuid', NEW.supplier_uuid,
        'category_uuid', NEW.category_uuid,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- products表DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_delete
AFTER DELETE ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('products', OLD.uuid, 'DELETE', JSON_OBJECT(
        'uuid', OLD.uuid,
        'product_name', OLD.product_name,
        'product_code', OLD.product_code,
        'unit_price', OLD.unit_price,
        'current_quantity', OLD.current_quantity,
        'min_quantity', OLD.min_quantity,
        'max_quantity', OLD.max_quantity,
        'supplier_uuid', OLD.supplier_uuid,
        'category_uuid', OLD.category_uuid,
        'created_at', OLD.created_at,
        'updated_at', OLD.updated_at
    ));
END//

-- 3. 为suppliers表创建触发器

-- suppliers表INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_insert
AFTER INSERT ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('suppliers', NEW.uuid, 'INSERT', JSON_OBJECT(
        'uuid', NEW.uuid,
        'supplier_name', NEW.supplier_name,
        'supplier_code', NEW.supplier_code,
        'contact_person', NEW.contact_person,
        'phone', NEW.phone,
        'email', NEW.email,
        'address', NEW.address,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- suppliers表UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_update
AFTER UPDATE ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('suppliers', NEW.uuid, 'UPDATE', JSON_OBJECT(
        'uuid', NEW.uuid,
        'supplier_name', NEW.supplier_name,
        'supplier_code', NEW.supplier_code,
        'contact_person', NEW.contact_person,
        'phone', NEW.phone,
        'email', NEW.email,
        'address', NEW.address,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- suppliers表DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_delete
AFTER DELETE ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('suppliers', OLD.uuid, 'DELETE', JSON_OBJECT(
        'uuid', OLD.uuid,
        'supplier_name', OLD.supplier_name,
        'supplier_code', OLD.supplier_code,
        'contact_person', OLD.contact_person,
        'phone', OLD.phone,
        'email', OLD.email,
        'address', OLD.address,
        'created_at', OLD.created_at,
        'updated_at', OLD.updated_at
    ));
END//

-- 4. 为inventory表创建触发器

-- inventory表INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_insert
AFTER INSERT ON inventory
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('inventory', NEW.uuid, 'INSERT', JSON_OBJECT(
        'uuid', NEW.uuid,
        'product_uuid', NEW.product_uuid,
        'quantity', NEW.quantity,
        'location', NEW.location,
        'batch_number', NEW.batch_number,
        'expiry_date', NEW.expiry_date,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- inventory表UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_update
AFTER UPDATE ON inventory
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('inventory', NEW.uuid, 'UPDATE', JSON_OBJECT(
        'uuid', NEW.uuid,
        'product_uuid', NEW.product_uuid,
        'quantity', NEW.quantity,
        'location', NEW.location,
        'batch_number', NEW.batch_number,
        'expiry_date', NEW.expiry_date,
        'created_at', NEW.created_at,
        'updated_at', NEW.updated_at
    ));
END//

-- inventory表DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_delete
AFTER DELETE ON inventory
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (table_name, record_uuid, operation_type, change_data)
    VALUES ('inventory', OLD.uuid, 'DELETE', JSON_OBJECT(
        'uuid', OLD.uuid,
        'product_uuid', OLD.product_uuid,
        'quantity', OLD.quantity,
        'location', OLD.location,
        'batch_number', OLD.batch_number,
        'expiry_date', OLD.expiry_date,
        'created_at', OLD.created_at,
        'updated_at', OLD.updated_at
    ));
END//

DELIMITER ;

-- 5. 为其他表创建触发器（可以根据需要继续添加）
-- sales_orders, purchase_orders, customers, product_categories, product_models等

-- 注意：实际部署时需要为所有需要同步的表创建相应的触发器