-- 添加selected_specification字段到purchase_order_items表
ALTER TABLE purchase_order_items 
ADD COLUMN selected_specification TEXT NULL COMMENT '选择的规格参数' AFTER model_uuid;