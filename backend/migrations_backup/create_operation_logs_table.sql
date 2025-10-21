-- 操作日志表创建脚本
-- 用于记录系统所有关键操作，确保操作可追溯

-- 选择数据库
USE xiaochuanERP;

-- 创建操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    
    -- 操作信息
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型：CREATE, UPDATE, DELETE, LOGIN, LOGOUT等',
    operation_module VARCHAR(50) NOT NULL COMMENT '操作模块：products, suppliers, purchase_orders等',
    operation_description TEXT NOT NULL COMMENT '操作描述',
    
    -- 操作目标
    target_uuid CHAR(36) NULL COMMENT '操作目标UUID（如产品UUID、订单UUID等）',
    target_name VARCHAR(200) NULL COMMENT '操作目标名称',
    
    -- 操作前后数据（用于审计）
    before_data JSON NULL COMMENT '操作前数据（JSON格式）',
    after_data JSON NULL COMMENT '操作后数据（JSON格式）',
    
    -- 操作者信息
    operator_uuid CHAR(36) NOT NULL COMMENT '操作者UUID',
    operator_name VARCHAR(100) NOT NULL COMMENT '操作者姓名',
    operator_ip VARCHAR(45) NULL COMMENT '操作者IP地址',
    
    -- 操作结果
    operation_status ENUM('SUCCESS', 'FAILED') NOT NULL DEFAULT 'SUCCESS' COMMENT '操作状态',
    error_message TEXT NULL COMMENT '错误信息（操作失败时）',
    
    -- 时间戳
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_operation_type (operation_type),
    INDEX idx_operation_module (operation_module),
    INDEX idx_operator_uuid (operator_uuid),
    INDEX idx_target_uuid (target_uuid),
    INDEX idx_operation_time (operation_time),
    INDEX idx_operation_status (operation_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统操作日志表';

-- 插入示例数据（可选）
INSERT INTO operation_logs (
    operation_type, operation_module, operation_description,
    target_uuid, target_name, operator_uuid, operator_name, operator_ip
) VALUES 
('LOGIN', 'auth', '用户登录系统', NULL, '系统登录', '01842b4b-b965-4b89-99b3-11a4f8c5f9cc', '管理员', '192.168.1.100'),
('CREATE', 'products', '创建新产品：联想ThinkPad X1 Carbon', '01842b4b-b965-4b89-99b3-11a4f8c5f9cc', '联想ThinkPad X1 Carbon', '01842b4b-b965-4b89-99b3-11a4f8c5f9cc', '管理员', '192.168.1.100'),
('UPDATE', 'purchase_orders', '修改采购订单：PO20240115001', '123e4567-e89b-12d3-a456-426614174000', 'PO20240115001', '01842b4b-b965-4b89-99b3-11a4f8c5f9cc', '管理员', '192.168.1.101');