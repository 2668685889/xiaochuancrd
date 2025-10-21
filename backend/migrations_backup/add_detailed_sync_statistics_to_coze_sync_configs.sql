-- 添加详细的同步统计字段到coze_sync_configs表
-- 迁移脚本：为同步配置添加新增、更新、删除的具体统计功能

-- 使用数据库
USE xiaochuanERP;

-- 添加新增同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN insert_sync_count INT NOT NULL DEFAULT 0 COMMENT '新增数据同步次数';

-- 添加更新同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN update_sync_count INT NOT NULL DEFAULT 0 COMMENT '更新数据同步次数';

-- 添加删除同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN delete_sync_count INT NOT NULL DEFAULT 0 COMMENT '删除数据同步次数';

-- 验证表结构
DESCRIBE coze_sync_configs;

-- 更新现有记录的默认值（确保所有记录都有正确的默认值）
UPDATE coze_sync_configs 
SET insert_sync_count = 0, 
    update_sync_count = 0, 
    delete_sync_count = 0
WHERE insert_sync_count IS NULL OR update_sync_count IS NULL OR delete_sync_count IS NULL;

-- 显示更新后的记录示例
SELECT uuid, config_title, table_name, 
       total_sync_count, success_sync_count, failed_sync_count,
       insert_sync_count, update_sync_count, delete_sync_count, last_sync_type
FROM coze_sync_configs 
LIMIT 5;