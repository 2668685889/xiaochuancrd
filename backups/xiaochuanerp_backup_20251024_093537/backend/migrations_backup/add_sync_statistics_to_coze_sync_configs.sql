-- 添加同步统计字段到coze_sync_configs表
-- 迁移脚本：为同步配置添加同步次数统计功能

-- 使用数据库
USE xiaochuanERP;

-- 添加总同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN total_sync_count INT NOT NULL DEFAULT 0 COMMENT '总同步次数';

-- 添加成功同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN success_sync_count INT NOT NULL DEFAULT 0 COMMENT '成功同步次数';

-- 添加失败同步次数字段
ALTER TABLE coze_sync_configs 
ADD COLUMN failed_sync_count INT NOT NULL DEFAULT 0 COMMENT '失败同步次数';

-- 添加最后同步类型字段
ALTER TABLE coze_sync_configs 
ADD COLUMN last_sync_type VARCHAR(20) NULL COMMENT '最后同步类型：MANUAL, AUTO_INSERT, AUTO_UPDATE, AUTO_DELETE';

-- 验证表结构
DESCRIBE coze_sync_configs;

-- 更新现有记录的默认值（确保所有记录都有正确的默认值）
UPDATE coze_sync_configs 
SET total_sync_count = 0, 
    success_sync_count = 0, 
    failed_sync_count = 0
WHERE total_sync_count IS NULL OR success_sync_count IS NULL OR failed_sync_count IS NULL;

-- 显示更新后的记录示例
SELECT uuid, config_title, table_name, total_sync_count, success_sync_count, failed_sync_count, last_sync_type
FROM coze_sync_configs 
LIMIT 5;