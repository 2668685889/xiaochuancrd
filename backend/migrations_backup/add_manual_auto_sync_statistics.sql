-- 添加手动同步和自动同步的统计字段到coze_sync_configs表
USE xiaochuanERP;

ALTER TABLE coze_sync_configs 
ADD COLUMN manual_sync_count INT DEFAULT 0 COMMENT '手动同步次数',
ADD COLUMN auto_sync_count INT DEFAULT 0 COMMENT '自动同步次数',
ADD COLUMN last_manual_sync_time DATETIME NULL COMMENT '最后手动同步时间',
ADD COLUMN last_auto_sync_time DATETIME NULL COMMENT '最后自动同步时间';