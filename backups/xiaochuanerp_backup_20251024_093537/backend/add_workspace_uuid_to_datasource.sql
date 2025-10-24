-- 为 sys_data_source 表添加 workspace_uuid 字段
ALTER TABLE sys_data_source ADD COLUMN workspace_uuid VARCHAR(36) NOT NULL DEFAULT 'default' COMMENT '工作空间UUID' AFTER uuid;

-- 为 workspace_uuid 字段创建索引
CREATE INDEX idx_sys_data_source_workspace_uuid ON sys_data_source(workspace_uuid);

-- 更新现有记录的 workspace_uuid 字段
UPDATE sys_data_source SET workspace_uuid = 'default' WHERE workspace_uuid = '' OR workspace_uuid IS NULL;