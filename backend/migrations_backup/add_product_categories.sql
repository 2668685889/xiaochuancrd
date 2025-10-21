-- 产品分类管理数据库迁移脚本

-- 1. 产品分类表 (product_categories)
CREATE TABLE IF NOT EXISTS product_categories (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parent_uuid CHAR(36) NULL,
    sort_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    FOREIGN KEY (parent_uuid) REFERENCES product_categories(uuid) ON DELETE SET NULL
);

-- 产品分类表索引
CREATE UNIQUE INDEX uk_product_categories_code ON product_categories(category_code);
CREATE INDEX idx_product_categories_name ON product_categories(category_name);
CREATE INDEX idx_product_categories_parent ON product_categories(parent_uuid);
CREATE INDEX idx_product_categories_sort_order ON product_categories(sort_order);
CREATE INDEX idx_product_categories_is_active ON product_categories(is_active);
CREATE INDEX idx_product_categories_created_at ON product_categories(created_at);

-- 2. 修改产品型号表，将category字段改为category_uuid外键关联
ALTER TABLE product_models ADD COLUMN category_uuid CHAR(36) NULL;
ALTER TABLE product_models ADD CONSTRAINT fk_product_models_category 
    FOREIGN KEY (category_uuid) REFERENCES product_categories(uuid) ON DELETE SET NULL;

-- 3. 修改产品表，将category字段改为category_uuid外键关联
ALTER TABLE products ADD COLUMN category_uuid CHAR(36) NULL;
ALTER TABLE products ADD CONSTRAINT fk_products_category 
    FOREIGN KEY (category_uuid) REFERENCES product_categories(uuid) ON DELETE SET NULL;

-- 4. 插入默认产品分类数据
INSERT INTO product_categories (uuid, category_name, category_code, description, sort_order) VALUES
(UUID(), '电子产品', 'ELECTRONICS', '各类电子产品和设备', 1),
(UUID(), '办公用品', 'OFFICE_SUPPLIES', '办公文具和耗材', 2),
(UUID(), '家居用品', 'HOME_GOODS', '家庭生活用品', 3),
(UUID(), '服装鞋帽', 'CLOTHING', '服装、鞋帽和配饰', 4),
(UUID(), '食品饮料', 'FOOD_BEVERAGE', '食品和饮料', 5);

-- 5. 更新现有产品型号和产品的分类关联
UPDATE product_models pm 
SET category_uuid = (
    SELECT pc.uuid 
    FROM product_categories pc 
    WHERE pc.category_name = pm.category 
    LIMIT 1
)
WHERE pm.category IS NOT NULL;

UPDATE products p 
SET category_uuid = (
    SELECT pc.uuid 
    FROM product_categories pc 
    WHERE pc.category_name = p.category 
    LIMIT 1
)
WHERE p.category IS NOT NULL;

-- 6. 删除旧的category字段（可选，暂时保留以兼容现有代码）
-- ALTER TABLE product_models DROP COLUMN category;
-- ALTER TABLE products DROP COLUMN category;