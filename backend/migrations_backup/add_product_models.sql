-- 产品型号和规格管理数据库迁移脚本

-- 1. 产品型号表 (product_models)
CREATE TABLE IF NOT EXISTS product_models (
    uuid CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    model_name VARCHAR(100) NOT NULL,
    model_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    specifications JSON NOT NULL DEFAULT (JSON_OBJECT()),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- 产品型号表索引
CREATE UNIQUE INDEX uk_product_models_code ON product_models(model_code);
CREATE INDEX idx_product_models_name ON product_models(model_name);
CREATE INDEX idx_product_models_category ON product_models(category);
CREATE INDEX idx_product_models_is_active ON product_models(is_active);
CREATE INDEX idx_product_models_created_at ON product_models(created_at);

-- 2. 修改产品表，添加型号关联字段
ALTER TABLE products ADD COLUMN model_uuid CHAR(36) NULL;
ALTER TABLE products ADD CONSTRAINT fk_products_model 
    FOREIGN KEY (model_uuid) REFERENCES product_models(uuid) ON DELETE SET NULL;

-- 3. 创建产品型号规格表索引
CREATE INDEX idx_products_model ON products(model_uuid);