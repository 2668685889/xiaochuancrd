-- 为采购订单明细表添加产品型号关联字段

-- 选择数据库
USE xiaochuanERP;

-- 1. 添加model_uuid字段到purchase_order_items表
ALTER TABLE purchase_order_items ADD COLUMN model_uuid CHAR(36) NULL;

-- 2. 添加外键约束
ALTER TABLE purchase_order_items ADD CONSTRAINT fk_purchase_order_items_model 
    FOREIGN KEY (model_uuid) REFERENCES product_models(uuid) ON DELETE SET NULL;

-- 3. 创建索引
CREATE INDEX idx_purchase_order_items_model ON purchase_order_items(model_uuid);