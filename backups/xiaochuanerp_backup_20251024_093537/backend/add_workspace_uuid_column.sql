-- 为sys_assistant表添加workspace_uuid字段
ALTER TABLE sys_assistant ADD COLUMN workspace_uuid VARCHAR(36) NOT NULL DEFAULT 'default' COMMENT '工作空间UUID' AFTER uuid;

-- 为workspace_uuid字段添加索引
CREATE INDEX idx_sys_assistant_workspace_uuid ON sys_assistant(workspace_uuid);

-- 更新现有记录的workspace_uuid字段值
UPDATE sys_assistant SET workspace_uuid = 'default' WHERE workspace_uuid = 'default' OR workspace_uuid IS NULL;