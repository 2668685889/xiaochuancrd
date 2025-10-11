-- 添加三个独立工作流ID字段到coze_sync_configs表
-- 用于支持新增、更新、删除操作的独立工作流配置

-- 选择数据库
USE xiaochuanERP;

-- 添加三个独立工作流ID字段
ALTER TABLE coze_sync_configs 
ADD COLUMN coze_workflow_id_insert VARCHAR(100) NULL COMMENT '新增操作工作流ID' AFTER coze_workflow_id,
ADD COLUMN coze_workflow_id_update VARCHAR(100) NULL COMMENT '更新操作工作流ID' AFTER coze_workflow_id_insert,
ADD COLUMN coze_workflow_id_delete VARCHAR(100) NULL COMMENT '删除操作工作流ID' AFTER coze_workflow_id_update;

-- 将原有的coze_workflow_id字段改为可空，因为现在可以使用独立的工作流ID
ALTER TABLE coze_sync_configs 
MODIFY COLUMN coze_workflow_id VARCHAR(100) NULL COMMENT 'Coze工作流ID（向后兼容）';

-- 更新现有数据，将原有的工作流ID复制到新增操作工作流ID字段
UPDATE coze_sync_configs 
SET coze_workflow_id_insert = coze_workflow_id 
WHERE coze_workflow_id IS NOT NULL;

-- 显示表结构确认修改成功
DESCRIBE coze_sync_configs;