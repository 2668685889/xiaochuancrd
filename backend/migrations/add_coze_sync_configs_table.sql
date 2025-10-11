-- Coze同步配置表创建脚本
-- 用于持久化存储Coze同步配置，避免重启后配置丢失

-- 选择数据库
USE xiaochuanERP;

-- 创建Coze同步配置表
CREATE TABLE IF NOT EXISTS coze_sync_configs (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    
    -- 配置基本信息
    config_title VARCHAR(200) NOT NULL COMMENT '配置标题',
    table_name VARCHAR(100) NOT NULL COMMENT '同步的数据表名',
    
    -- Coze API配置
    coze_workflow_id VARCHAR(100) NOT NULL COMMENT 'Coze工作流ID',
    coze_api_url VARCHAR(500) NOT NULL DEFAULT 'https://api.coze.cn' COMMENT 'Coze API地址',
    coze_api_key TEXT NULL COMMENT 'Coze API密钥',
    
    -- 同步设置
    sync_on_insert BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否同步插入操作',
    sync_on_update BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否同步更新操作',
    sync_on_delete BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否同步删除操作',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用同步',
    
    -- 字段选择
    selected_fields JSON NULL COMMENT '选择的字段列表',
    
    -- 状态信息
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' COMMENT '同步状态：ACTIVE, PAUSED, ERROR',
    last_sync_time TIMESTAMP NULL COMMENT '最后同步时间',
    last_error TEXT NULL COMMENT '最后错误信息',
    
    -- 创建者信息
    created_by CHAR(36) NULL COMMENT '创建者UUID',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_table_name (table_name),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Coze同步配置表';

-- 添加外键约束（如果users表存在）
-- ALTER TABLE coze_sync_configs ADD CONSTRAINT fk_coze_sync_configs_created_by 
-- FOREIGN KEY (created_by) REFERENCES users(uuid) ON DELETE SET NULL;

-- 插入示例数据（可选）
INSERT INTO coze_sync_configs (
    config_title, table_name, coze_workflow_id, coze_api_url, 
    sync_on_insert, sync_on_update, sync_on_delete, enabled, status
) VALUES 
('产品数据同步', 'products', 'workflow_001', 'https://api.coze.cn', TRUE, TRUE, FALSE, TRUE, 'ACTIVE'),
('库存数据同步', 'inventory', 'workflow_002', 'https://api.coze.cn', TRUE, TRUE, FALSE, TRUE, 'ACTIVE');