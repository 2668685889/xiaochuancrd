"""
产品数据模型
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4

from app.core.database import Base


class Product(Base):
    """产品模型"""
    __tablename__ = "products"
    
    uuid = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    product_name = Column(String(100), nullable=False, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_name = Column(String(50), nullable=True, index=True)  # 产品分类名称（兼容性字段）
    unit_price = Column(Float(precision=2), nullable=False, default=0.0)
    current_quantity = Column(Integer, nullable=False, default=0)
    min_quantity = Column(Integer, nullable=False, default=0)
    max_quantity = Column(Integer, nullable=False, default=0)
    supplier_uuid = Column(CHAR(36), ForeignKey('suppliers.uuid'), nullable=False, index=True)
    model_uuid = Column(CHAR(36), ForeignKey('product_models.uuid'), nullable=True, index=True)  # 新增：产品型号关联
    category_uuid = Column(CHAR(36), ForeignKey('product_categories.uuid'), nullable=True, index=True)  # 新增：产品分类关联
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    # 关系 - 使用字符串引用避免循环导入
    supplier = relationship("Supplier", back_populates="products", lazy="select")
    inventory_records = relationship("InventoryRecord", back_populates="product", lazy="select")
    product_model = relationship("ProductModel", back_populates="products", lazy="select")  # 新增：产品型号关系
    category_rel = relationship("ProductCategory", back_populates="products", lazy="select")  # 新增：产品分类关系
    
    def __repr__(self):
        return f"<Product(name='{self.product_name}', code='{self.product_code}')>"