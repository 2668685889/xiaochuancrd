-- 为purchase_orders表添加is_active字段
ALTER TABLE purchase_orders 
ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '软删除标记，TRUE表示有效，FALSE表示已删除';

-- 为purchase_order_items表添加is_active字段（如果需要）
ALTER TABLE purchase_order_items 
ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL COMMENT '软删除标记，TRUE表示有效，FALSE表示已删除';