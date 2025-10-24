-- 创建数据变化日志表
CREATE TABLE IF NOT EXISTS data_change_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL COMMENT '表名',
    record_uuid CHAR(36) NOT NULL COMMENT '记录UUID',
    operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL COMMENT '操作类型',
    change_data JSON COMMENT '变化数据（JSON格式）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    processed TINYINT DEFAULT 0 COMMENT '是否已处理（0-未处理，1-已处理）',
    processed_at TIMESTAMP NULL COMMENT '处理时间',
    INDEX idx_table_name (table_name),
    INDEX idx_record_uuid (record_uuid),
    INDEX idx_operation_type (operation_type),
    INDEX idx_created_at (created_at),
    INDEX idx_processed (processed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据变化日志表';

-- 为products表创建触发器
DELIMITER //

-- INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'products',
        NEW.uuid,
        'INSERT',
        JSON_OBJECT(
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
        )
    );
END//

-- UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'products',
        NEW.uuid,
        'UPDATE',
        JSON_OBJECT(
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
        )
    );
END//

-- DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_products_delete
AFTER DELETE ON products
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'products',
        OLD.uuid,
        'DELETE',
        JSON_OBJECT(
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
        )
    );
END//

-- 为suppliers表创建触发器

-- INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_insert
AFTER INSERT ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'suppliers',
        NEW.uuid,
        'INSERT',
        JSON_OBJECT(
            'uuid', NEW.uuid,
            'supplier_name', NEW.supplier_name,
            'supplier_code', NEW.supplier_code,
            'contact_person', NEW.contact_person,
            'phone', NEW.phone,
            'email', NEW.email,
            'address', NEW.address,
            'created_at', NEW.created_at,
            'updated_at', NEW.updated_at
        )
    );
END//

-- UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_update
AFTER UPDATE ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'suppliers',
        NEW.uuid,
        'UPDATE',
        JSON_OBJECT(
            'uuid', NEW.uuid,
            'supplier_name', NEW.supplier_name,
            'supplier_code', NEW.supplier_code,
            'contact_person', NEW.contact_person,
            'phone', NEW.phone,
            'email', NEW.email,
            'address', NEW.address,
            'created_at', NEW.created_at,
            'updated_at', NEW.updated_at
        )
    );
END//

-- DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_suppliers_delete
AFTER DELETE ON suppliers
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'suppliers',
        OLD.uuid,
        'DELETE',
        JSON_OBJECT(
            'uuid', OLD.uuid,
            'supplier_name', OLD.supplier_name,
            'supplier_code', OLD.supplier_code,
            'contact_person', OLD.contact_person,
            'phone', OLD.phone,
            'email', OLD.email,
            'address', OLD.address,
            'created_at', OLD.created_at,
            'updated_at', OLD.updated_at
        )
    );
END//

-- 为inventory_records表创建触发器

-- INSERT触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_records_insert
AFTER INSERT ON inventory_records
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'inventory_records',
        NEW.uuid,
        'INSERT',
        JSON_OBJECT(
            'uuid', NEW.uuid,
            'product_uuid', NEW.product_uuid,
            'change_type', NEW.change_type,
            'quantity_change', NEW.quantity_change,
            'current_quantity', NEW.current_quantity,
            'remark', NEW.remark,
            'record_date', NEW.record_date,
            'created_by', NEW.created_by,
            'created_at', NEW.created_at
        )
    );
END//

-- UPDATE触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_records_update
AFTER UPDATE ON inventory_records
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'inventory_records',
        NEW.uuid,
        'UPDATE',
        JSON_OBJECT(
            'uuid', NEW.uuid,
            'product_uuid', NEW.product_uuid,
            'change_type', NEW.change_type,
            'quantity_change', NEW.quantity_change,
            'current_quantity', NEW.current_quantity,
            'remark', NEW.remark,
            'record_date', NEW.record_date,
            'created_by', NEW.created_by,
            'created_at', NEW.created_at
        )
    );
END//

-- DELETE触发器
CREATE TRIGGER IF NOT EXISTS trigger_inventory_records_delete
AFTER DELETE ON inventory_records
FOR EACH ROW
BEGIN
    INSERT INTO data_change_logs (
        table_name, 
        record_uuid, 
        operation_type, 
        change_data
    ) VALUES (
        'inventory_records',
        OLD.uuid,
        'DELETE',
        JSON_OBJECT(
            'uuid', OLD.uuid,
            'product_uuid', OLD.product_uuid,
            'change_type', OLD.change_type,
            'quantity_change', OLD.quantity_change,
            'current_quantity', OLD.current_quantity,
            'remark', OLD.remark,
            'record_date', OLD.record_date,
            'created_by', OLD.created_by,
            'created_at', OLD.created_at
        )
    );
END//

DELIMITER ;

-- 创建清理已处理记录的存储过程
DELIMITER //

CREATE PROCEDURE IF NOT EXISTS cleanup_processed_changes()
BEGIN
    DECLARE cutoff_date TIMESTAMP;
    SET cutoff_date = DATE_SUB(NOW(), INTERVAL 7 DAY);
    
    DELETE FROM data_change_logs 
    WHERE processed = 1 
    AND processed_at < cutoff_date;
END//

DELIMITER ;

-- 创建清理任务的定时事件（每天凌晨2点执行）
DELIMITER //

CREATE EVENT IF NOT EXISTS event_cleanup_processed_changes
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '02:00:00')
DO
BEGIN
    CALL cleanup_processed_changes();
END//

DELIMITER ;